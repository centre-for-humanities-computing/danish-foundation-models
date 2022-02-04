"""
Danish of a simple Profanity filter

Authors:
    Jens Dahl Møllerhøj
"""

from typing import Iterable

class ProfanityFilter:
    """
    Danish implementation of a profanity filter.
    """
    def __init__(self):
        pass

    def __call__(self, docs: Iterable[str]) -> Generator:
        """Applies profanity filter
        """

        # normalize

        # count occurrences of known profanities in document

        # flag document based on heuristic

        # print possible violating documents

        return docs

