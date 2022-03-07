import os
import sys
import time
from typing import Iterable, Optional
from datasets import load_dataset

from collections import defaultdict

from spacy.language import Language
from spacy.matcher import Matcher
from spacy.tokens import Doc
import spacy

sys.path.append(".")
from dfm.description.description_pattern_lists import (
    female_gendered_terms,
    male_gendered_terms,
    occupation_pattern_list,
    danish_adult_words,
)


def remove_irrelevant_columns(ds):
    return ds.remove_columns(["text", "doc_id", "LICENSE", "uri", "date_built"])


def get_muslim_name_patterns() -> list:
    from dacy.datasets import muslim_names

    muslim_names_list = [name.lower() for name in muslim_names()["first_name"]]

    return MatchCounter.term_list_to_lowercase_match_patterns(
        term_list=muslim_names_list, label="muslim_names"
    )


def get_gender_name_patterns() -> list:
    """
    Creates a list of SpaCy patterns in the shape {"[col_name]": [{"LOWER": "[pattern]"}]}
    """
    from dacy.datasets import female_names, male_names

    female_names_list = [name.lower() for name in female_names()["first_name"]]
    female_names_patterns = MatchCounter.term_list_to_lowercase_match_patterns(
        female_names_list, label="female_names"
    )

    male_names_list = [name.lower() for name in male_names()["first_name"]]
    male_name_patterns = MatchCounter.term_list_to_lowercase_match_patterns(
        male_names_list, label="male_names"
    )

    return female_names_patterns + male_name_patterns


class MatchCounter:
    """Class of utility functions for counting spacy matches"""

    def __init__(self, match_patterns: list, nlp: Language):
        self.nlp = nlp
        self.matcher_objects = self.gen_matcher_objects_from_pattern_list(match_patterns)

    @staticmethod
    def term_list_to_lowercase_match_patterns(
        term_list: list, label: Optional[str] = None, label_prefix: str = ""
    ) -> list:
        """
        Takes a list of terms and creates a list of SpaCy patterns in the shape {"label": [{"LOWER": "term"}]}
        """
        out_list = []

        for term in term_list:
            if label is None:
                cur_label = label_prefix + term
                out_list.append({cur_label: [{"LOWER": term}]})
            else:
                cur_label = label_prefix + label
                out_list.append({cur_label: [{"LOWER": term}]})

        return out_list

    def gen_matcher_objects_from_pattern_list(
        self, pattern_container_list: list
    ) -> Matcher:
        """
        Generates matcher objects from a list of dictionaries with {matcher_label (str): pattern (list)}
        Pattern must conform to SpaCy pattern standards:

        Example:
            >>> pattern_container_list = [
            >>>    {"atheism": [{"LOWER": {"REGEX": "athei.+"}}]},
            >>>    {"atheism": [{"LOWER": {"REGEX": "atei.+"}}]},
            >>>    {"skøde": [{"LOWER": "skøde"}]},
            >>> ]
            >>> match_counter.gen_matcher_objects_from_pattern_list(pattern_container_list)
        """
        matcher_object = Matcher(self.nlp.vocab)

        for pattern_container in pattern_container_list:
            pattern_label, subpattern_list = list(*pattern_container.items())

            matcher_object.add(pattern_label, [subpattern_list])

        return matcher_object

    def _get_match_counts_from_doc(
        self, doc: Doc, matcher_object: Matcher
    ) -> dict:
        """
        Get match counts for a list of SpaCy matcher-objects

        args:
            doc (Doc)
            pattern_container_list (list): A list of dictionaries fitting SpaCy patterns
            nlp: Language

        returns:
            A dictionary of the format {pattern_label (str): count (int)}.
        """

        counts = defaultdict(int)

        # Make sure that all elements are represented in the dict
        for pattern in matcher_object._patterns:
            pattern_label = self.nlp.vocab.strings[pattern]

            counts[pattern_label] = 0

        for match_id, start, end in matcher_object(doc):
            counts[self.nlp.vocab.strings[match_id]] += 1

        return dict(counts)

    def count(
        self, texts: Iterable[str]
    ) -> dict:
        """
        Takes an iterable of texts and processes them into a dictionary with
        {match_label (str): match_counts (list of ints)}
        """

        docs = self.nlp.pipe(texts)

        aggregated_match_counts = defaultdict(list)

        for doc in docs:
            doc_match_counts = self._get_match_counts_from_doc(doc, self.matcher_objects)

            for pattern_label in doc_match_counts.keys():
                pattern_match_count = doc_match_counts.get(pattern_label, 0)

                aggregated_match_counts[pattern_label].append(pattern_match_count)

        return aggregated_match_counts


if __name__ == "__main__":
    any_token_pattern = [{"tokens": [{"TEXT": {"REGEX": ".+"}}]}]

    # Religion
    religion_patterns = [
        {"atheist": [{"LOWER": {"REGEX": "ath{0,1}eis.*"}}]},
        {"buddhist": [{"LOWER": {"REGEX": "buddh{0,1}.*"}}]},
        {"christian": [{"LOWER": {"REGEX": "kriste.*"}}]},
        {"hindu": [{"LOWER": {"REGEX": "hindu.*"}}]},
        {"muslim": [{"LOWER": {"REGEX": "muslim.*"}}]},
        {"jew": [{"LOWER": {"REGEX": "jødi.*"}}]},
        {"jew": [{"LOWER": {"REGEX": "(?!jødeskæg)jøde.*"}}]},  # Jødeskæg == Stueplante
    ]

    muslim_name_patterns = get_muslim_name_patterns()

    # Genders
    gender_name_patterns = get_gender_name_patterns()

    gender_pronoun_patterns = [
        {"male_pronoun": [{"LOWER": "han"}]},
        {"female_pronoun": [{"LOWER": "hun"}]},
    ]

    # List is a partial translation of Rae et al. 2022, p. 95

    male_gendered_term_patterns = MatchCounter.term_list_to_lowercase_match_patterns(
        male_gendered_terms, label="male_gendered_terms"
    )
    female_gendered_term_patterns = MatchCounter.term_list_to_lowercase_match_patterns(
        female_gendered_terms, label="female_gendered_terms"
    )

    # Occupations 
    occupation_patterns = MatchCounter.term_list_to_lowercase_match_patterns(
        occupation_pattern_list, label_prefix="occu_"
    )
    # List is a partial translation of Rae et al. 2022, p. 95

    # Adult words
    adult_patterns = MatchCounter.term_list_to_lowercase_match_patterns(
        danish_adult_words, label_prefix="porn_"
    )

    # Execution
    combined_patterns = (
        any_token_pattern
        + religion_patterns
        + muslim_name_patterns
        + gender_name_patterns
        + gender_pronoun_patterns
        + male_gendered_term_patterns
        + female_gendered_term_patterns
        + occupation_patterns
        + adult_patterns
    )

    ds = load_dataset("DDSC/partial-danish-gigaword-no-twitter")
    ds_sharded = ds.shuffle()["train"].shard(
        num_shards=100, index=0
    )  # Work on 1/100th of DGW

    nlp = spacy.blank("da")
    nlp.max_length = 50000000

    mc = MatchCounter(match_patterns=combined_patterns, nlp=nlp)

    start_time = time.time()

    dgw_processed = ds_sharded.map(
        lambda batch: mc.count(batch["text"]),
        batched=True,
        batch_size=50,
        num_proc=16,
    )

    print(f"\n\n--- Execution time was {time.time() - start_time} seconds ---")

    if not os.path.exists("csv"):
        os.makedirs("csv")

    remove_irrelevant_columns(dgw_processed).to_csv("csv/output_100.csv")
