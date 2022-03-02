"""
Danish implementation of quality filter described in [1]

Authors:
    Kenneth C. Enevoldsen
    Kasper Junge
    Malte Højmark-Bertelsen

References:
    [1] Rae, J. W., Borgeaud, S., Cai, T., Millican, K., Hoffmann, J., Song, F.,
    Aslanides, J., Henderson, S., Ring, R., Young, S., Rutherford, E., Hennigan,
    T., Menick, J., Cassirer, A., Powell, R., Driessche, G. van den, Hendricks,
    L. A., Rauh, M., Huang, P.-S., … Irving, G. (2021).
    Scaling Language Models: Methods, Analysis & Insights from Training Gopher.
    https://arxiv.org/abs/2112.11446v2
"""

from collections import Counter
from email.generator import Generator
from functools import partial
from typing import Iterable, Optional, Set, Tuple

import spacy
from spacy.tokens import Doc


class QualityFilter:
    """
    Danish implementation of quality filter described in (Rae et al., 2021).

    Args:
        stop_words (Optional[Set[str]], optional): A set of stop words to use.
            Defaults to None.
        min_stop_words (int, optional): The least amount of stop words a text
            should have before it is kept. Defaults to 2.
        mean_word_length (Tuple[int, int], optional): Upper and lower bound on the
            mean word length. Defaults to (3, 10).
        doc_length (Tuple[int, int], optional): Upper and lower bound on the
            documents length. Defaults to [50, 100_000].
        alpha_ratio (float, optional): the percentage of words in this document
            which should contain alphabetic character. Defaults to 0.7.
            Changed from 0.8 in the paper.
        symbol_2_word_ellipsis (float, optional): The highest acceptable ratio of
            ellipsis to words. Defaults to 0.1.
        symbol_2_word_hashtag (float, optional): The highest acceptable ratio of
            ellipsis to words.. Defaults to 0.1.
        max_p_begin_bullets (float, optional): Maximum number of lines which begins
            with a bulletpoint. Defaults to 0.9.
        max_p_end_ellipsis (float, optional): Maximum number of lines which ends
            with an ellipsis. Defaults to 0.3.
        string (str, optional): String for filtering. Defaults to None.
    """

    def __init__(
        self,
        stop_words: Optional[Set[str]] = None,
        min_stop_words: int = 2,
        mean_word_length: Tuple[int, int] = (3, 10),
        doc_length: Tuple[int, int] = [50, 100_000],
        alpha_ratio: float = 0.7,
        symbol_2_word_hashtag: float = 0.1,
        symbol_2_word_ellipsis: float = 0.1,
        max_p_begin_bullets: float = 0.9,
        max_p_end_ellipsis: float = 0.3,
        string: Optional[str] = None,
    ):
        if stop_words is None:
            stop_words = set(
                [
                    "er",
                    "jeg",
                    "det",
                    "du",
                    "ikke",
                    "at",
                    "en",
                    "og",
                    "har",
                    "vi",
                    "til",
                    "på",
                    "hvad",
                    "mig",
                    "med",
                    "de",
                    "for",
                    "den",
                    "så",
                    "der",
                    "dig",
                    "han",
                    "kan",
                    "af",
                ]
            )

        self.nlp = spacy.blank("da")

        self.filters = {
            "doc_length": partial(self.doc_length, doc_length=doc_length),
            "mean_word_length": partial(
                self.mean_word_length, mean_word_length=mean_word_length
            ),
            "alpha_ratio": partial(self.alpha, ratio=alpha_ratio),
            "symbol_2_word_hashtag": partial(
                self.symbol_2_word, ratio=symbol_2_word_hashtag, symbol="#"
            ),
            "symbol_2_word_ellipsis": partial(
                self.symbol_2_word, ratio=symbol_2_word_ellipsis, symbol="…"
            ),
            "line_bullets_or_ellipsis": partial(
                self.line_bullets_or_ellipsis,
                max_p_bullets=max_p_begin_bullets,
                max_p_ellipsis=max_p_end_ellipsis,
            ),
            "stop_word": partial(
                self.stop_word, stop_words=stop_words, n=min_stop_words
            ),
        }
        self.filtered = Counter()

    def __call__(self, docs: Iterable[str], as_tuples: bool = False) -> Generator:
        """Applies quality filter

        Args:
            docs (Iterable[str]): An iterable of strings of the text you wish to filter.
            as_tuples (bool, optional): If True doc is expected to be a tuple of size
                two with the first element being the text. The output of this function
                    will then also be a generator of tuples filtered based on the text.
                    Defaults to False.

        Yields:
            Generator: A Generator of either texts or tuples depending on the as_tuples
                argument.
        """

        for doc in self.nlp.pipe(docs, as_tuples=as_tuples):
            if as_tuples:
                doc, context = doc

            valid = True
            for filter, filter_fn in self.filters.items():
                if not filter_fn(doc):
                    valid = False

                    # log filtered documents
                    self.filtered[filter] += 1
                    break
            if not valid:
                continue

            if as_tuples:
                yield doc, context
            else:
                yield doc

    @staticmethod
    def doc_length(doc: Doc, doc_length: Tuple[int, int]) -> bool:
        """
        A filter that removes any document that does not contain between {doc_length[0]}
        and {doc_length[1]} words

        Args:
            doc (Doc): SpaCy document
            doc_length (Tuple[int, int]): Tuple indicate minimum and maximum length of
                document

        Returns:
            bool: A boolean indicator of whether the text passed the filter.
        """

        return doc_length[0] <= len(doc) <= doc_length[1]

    @staticmethod
    def mean_word_length(doc: Doc, mean_word_length: Tuple[int, int]) -> bool:
        """
        Filter document whose mean word length is outside the range of {mean_word_length[0]} to {mean_word_length[1]}
        characters

        Args:
            doc (Doc): SpaCy document
            mean_word_length (Tuple[int, int]): Tuple indicate minimum and maximum
                mean word length of document

        Returns:
            bool: A boolean indicator of whether the text passed the filter.
        """

        w_len = [len(t) for t in doc]
        mwl = sum(w_len) / len(doc)
        return mean_word_length[0] <= mwl <= mean_word_length[1]

    @staticmethod
    def alpha(doc: Doc, ratio: float) -> bool:
        """
        Filter that requires the {ratio}% of words in a document contain at least one
        alphabetic character

        Args:
            doc (Doc): SpaCy document
            ratio (float): The ratio of alphabetic characters

        Returns:
            bool: A boolean indicator of whether the text passed the filter.
        """
        # checks if a non-space token contains a alphabetic character
        contains_alpha = sum(
            any(c.isalpha() for c in t.text) for t in doc if not t.is_space
        )
        len_doc = len(doc)
        ratio_ = contains_alpha / len_doc
        return ratio_ >= ratio

    @staticmethod
    def symbol_2_word(doc: Doc, ratio: float, symbol: str) -> bool:
        """
        A filter that removes any document with a symbol-to-word ratio greater than
        {ratio} for either the {symbol}

        Args:
            doc (Doc): SpaCy document
            ratio (float): The symbol to word ratio
            symbol (str): A symbol to check the ratio of.

        Returns:
            bool: A boolean indicator of whether the text passed the filter.
        """
        n_symbol = doc.text.count(symbol)
        ratio_ = n_symbol / len(doc)
        return ratio_ < ratio

    @staticmethod
    def line_bullets_or_ellipsis(
        doc: Doc, max_p_bullets: float, max_p_ellipsis: float
    ) -> bool:
        """
        A filter that remove any document with more than {max_p_bullets}% of lines
        starting with a bullet point, or more than {max_p_ellipsis}% ending with an
        ellipsis

        Args:
            doc (Doc): SpaCy document
            max_p_bullets (float): Maximum percentage of lines starting with a bullet
                point
            max_p_ellipsis (float): Maximum percentage of lines ending with an ellipsis

        Returns:
            bool: A boolean indicator of whether the text passed the filter.
        """
        lines = doc.text.split("\n")
        if lines:
            n_bullets = sum(
                1 for line in lines if line.strip(" ").startswith(("-", "*"))
            )
            n_lines = len(lines)
            if (n_bullets / n_lines) > max_p_bullets:
                return False
            n_ellipsis = sum(
                1 for line in lines if line.strip(" ").endswith(("…", "..."))
            )
            return (n_ellipsis / n_lines) < max_p_ellipsis
        return False

    @staticmethod
    def stop_word(doc: Doc, n: int, stop_words: set) -> bool:
        """
        A "stop word" filter, to remove documents that do not contain at least {n} of
        the {stop_words}. This adequately deals with documents that contain no
        coherent text.

        Args:
            doc (Doc): SpaCy document
            n (int): Number of stop words the text should contain
            stop_words (set): A set of stop words

        Returns:
            bool: A boolean indicator of whether the text passed the filter.
        """
        n_stopwords = sum(1 for t in doc if t.text in stop_words)
        return n_stopwords >= n

    @staticmethod
    def string_filter(doc: Doc, string: Optional[str] = None) -> bool:
        """Method for filtering documents containing a specific string.

        Args:
            doc (Doc): SpaCy document
            string (str, optional): String for filtering.
        """
        if string is None:
            return True
        else:
            return string not in doc.text.lower()
