from collections import defaultdict

from spacy.language import Language
from spacy.matcher import Matcher
from spacy.tokens import Doc

from typing import Iterable, Optional


class MatchCounter:
    """Class of utility functions for counting spacy matches"""

    def __init__(self, match_patterns: list, nlp: Language):
        self.nlp = nlp
        self.matcher_objects = self.gen_matcher_objects_from_pattern_list(
            match_patterns
        )

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

    def _get_match_counts_from_doc(self, doc: Doc, matcher_object: Matcher) -> dict:
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

    def count(self, texts: Iterable[str]) -> dict:
        """
        Takes an iterable of texts and processes them into a dictionary with
        {match_label (str): match_counts (list of ints)}
        """

        docs = self.nlp.pipe(texts)

        aggregated_match_counts = defaultdict(list)

        for doc in docs:
            doc_match_counts = self._get_match_counts_from_doc(
                doc, self.matcher_objects
            )

            for pattern_label in doc_match_counts.keys():
                pattern_match_count = doc_match_counts.get(pattern_label, 0)

                aggregated_match_counts[pattern_label].append(pattern_match_count)

        return aggregated_match_counts
