from collections import Counter
from ctypes import Union
from email.generator import Generator
from functools import partial
from typing import Iterable, Optional, Set, Tuple

import spacy
from spacy.tokens import Doc


class QualityFilter:
    """
    Danish implementation of quality filter described in the paper:
    "Scaling Language Models: Methods, Analysis & Insights from Training Gopher"
    link: https://arxiv.org/abs/2112.11446
    """

    def __init__(
        self,
        stop_words: Optional[Set[str]] = None,
        min_stop_words: int = 2,
        mean_word_length: Tuple[int, int] = (3, 10),
        doc_length: Tuple[int, int] = [50, 100_000],
        alpha_ratio: float = 0.7,  # changed from 70%
        symbol_2_word_hashtag: float = 0.1,
        symbol_2_word_ellipsis: float = 0.1,
        max_p_begin_bullets: float = 0.9,
        max_p_end_ellipsis: float = 0.3,
    ):
        """
        Args:
            stop_words (Optional[Set[str]], optional): A set of stop words to use. Defaults to None.
            min_stop_words (int, optional): The least ammount of stop words a text should have before it is kept. Defaults to 2.
            mean_word_length (Tuple[int, int], optional): Upper and lower bound on the mean word length. Defaults to (3, 10).
            doc_length (Tuple[int, int], optional): Upper and lower bound on the documents length. Defaults to [50, 100_000].
            alpha_ratio (float, optional): the percentage of words in this document which should contain alphabetic character. Defaults to 0.7.
            symbol_2_word_ellipsis (float, optional): The highest acceptable ratio of ellipsis to words. Defaults to 0.1.
            symbol_2_word_hashtag (float, optional): The highest acceptable ratio of ellipsis to words.. Defaults to 0.1.
            max_p_begin_bullets (float, optional): Maximum number of lines which begins with a bulletpoint. Defaults to 0.9.
            max_p_end_ellipsis (float, optional): Maximum number of lines which ends with an ellipsis. Defaults to 0.3.
        """
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

        for doc in self.nlp.pipe(docs, as_tuples=as_tuples):
            if as_tuples:
                doc, context = doc

            valid = True
            for filter, filter_fn in self.filters.items():
                if filter_fn(doc) is False:
                    valid = False
                    # log filtered documents
                    self.filtered[filter] += 1
                    break
            if valid is False:
                continue

            if as_tuples:
                yield doc, context
            else:
                yield doc

    @staticmethod
    def doc_length(doc: Doc, doc_length: Tuple[int, int]) -> bool:
        """we remove any document that does not contain between 50 and 100,000 words"""
        if doc_length[0] <= len(doc) <= doc_length[1]:
            return True
        return False

    @staticmethod
    def mean_word_length(doc: Doc, mean_word_length: Tuple[int, int]) -> bool:
        """whose mean word length is outside the range of 3 to 10 characters"""
        w_len = [len(t) for t in doc]
        mwl = sum(w_len) / len(doc)
        if mean_word_length[0] <= mwl <= mean_word_length[1]:
            return True
        return False

    @staticmethod
    def alpha(doc: Doc, ratio: float) -> bool:
        """
        We also require that 80% of words in a document contain at least one alphabetic
        character
        """
        contains_alpha = sum(
            any(c.isalpha() for c in t.text) for t in doc if not t.is_space
        )
        len_doc = len(doc)
        ratio_ = contains_alpha / len_doc
        if ratio_ >= ratio:
            return True
        return False

    @staticmethod
    def symbol_2_word(doc: Doc, ratio: float, symbol: str) -> bool:
        """
        we remove any document with a symbol-to-word ratio greater than 0.1 for either the
        hash symbol or the ellipsis
        """
        n_symbol = doc.text.count(symbol)
        ratio_ = n_symbol / len(doc)
        if ratio_ >= ratio:
            return False
        return True

    @staticmethod
    def line_bullets_or_ellipsis(
        doc: Doc, max_p_bullets: float, max_p_ellipsis: float
    ) -> bool:
        """
        we remove any document with more than 90% of lines starting with a bullet point,
        or more than 30% ending with an ellipsis
        """
        lines = doc.text.split("\n")
        if lines:
            n_bullets = sum(1 for l in lines if l.strip(" ").startswith(("-", "*")))
            n_lines = len(lines)
            if (n_bullets / n_lines) > max_p_bullets:
                return False
            n_ellipsis = sum(1 for l in lines if l.strip(" ").endswith(("…", "...")))
            if (n_ellipsis / n_lines) > max_p_ellipsis:
                return False
            return True
        return False

    @staticmethod
    def stop_word(doc: Doc, n: int, stop_words: set) -> bool:
        """
        and apply a "stop word" filter, to remove documents that do not contain at least two of
        the following English words: the, be, to, of, and, that, have, with; this adequately deals
        with ostensibly English documents that contain no coherent English text.
        """
        n_stopwords = sum(1 for t in doc if t.text in stop_words)
        if n_stopwords >= n:
            return True
        return False
