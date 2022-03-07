import os
import sys
import time
from datasets import load_dataset


import spacy

sys.path.append(".")

from dfm.description.description_pattern_lists import (
    female_gendered_terms,
    male_gendered_terms,
    occupation_pattern_list,
    danish_adult_words,
)

from matchcounter import MatchCounter


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

    MatchCounter = MatchCounter(match_patterns=combined_patterns, nlp=nlp)

    start_time = time.time()

    dgw_processed = ds_sharded.map(
        lambda batch: MatchCounter.count(batch["text"]),
        batched=True,
        batch_size=50,
        num_proc=16,
    )

    print(f"\n\n--- Execution time was {time.time() - start_time} seconds ---")

    if not os.path.exists("csv"):
        os.makedirs("csv")

    remove_irrelevant_columns(dgw_processed).to_csv("csv/output_100.csv")
