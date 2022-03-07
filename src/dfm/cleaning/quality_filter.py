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
from functools import partial
from typing import Iterable, Optional, Set, Tuple, List

import spacy
from spacy.tokens import Doc

from nltk.tokenize import RegexpTokenizer

from .repetitious_filter import (
    set_dynamic_ext,
    duplicate_fraction_getter,
    duplicate_chr_fraction_getter,
    top_ngram_chr_fraction,
    duplicate_n_gram_fraction,
)


class NLTKTokenizer:
    """
    The NLTK tokenizer is noticeably faster than the spacy tokenizer
    though performs notably worse tokenization:

    Speed Comparison on a text of 237 tokens:

    .. code:

        text multiplication: time taken to tokenize

        NLTK
        10: 0.004389047622680664
        100: 0.018768787384033203
        1000: 0.17305397987365723
        10000: 1.4743471145629883
        SPACY
        10: 0.019192934036254883
        100: 0.15356707572937012
        1000: 1.7956039905548096
        10000: 18.097763776779175

    Note this removes newlines and does not keep the text intact. Therefore it sets
    the extension: doc._.text to keep the original text.

    Example:
        >>> nlp = spacy.blank("en")
        >>> nlp.tokenizer = NLTKTokenizer(nlp.vocab)
        >>> doc = nlp("What's happened to me? he thought. It wasn't a dream.")
    """

    def __init__(self, vocab):
        self.vocab = vocab
        self.tokenizer = RegexpTokenizer(pattern=r"\w+|[^\w\s]+")

        if not Doc.has_extension("text"):
            Doc.set_extension("text", default=None)

    def __call__(self, text):
        words = self.tokenizer.tokenize(text)
        doc = Doc(self.vocab, words=words)
        doc._.text = text
        return doc


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
        duplicate_line_fraction (float, optional): Max fraction of duplicate lines.
        duplicate_paragraph_fraction (float, optional): Max fraction of duplicate
            paragraphs
        duplicate_lines_chr_fraction (float, optional): Max fraction of character which
            is a part of a duplicate line
        duplicate_paragraph_chr_fraction (float, optional): Max fraction of character
            which is a part of a duplicate paragraph
        top_ngram_chr_fraction_thresholds: The maximum fraction of characters which is a
            part of the top ngram. Should be a list of floats corresponding to the
            n-grams range top_ngram_chr_fraction_range. I.e. [0.20, 0.18, 0.16] with a
            range of (2, 4) states that if the first top 20% of characters is contained
            within the top 2-gram then filter out the text.
        top_ngram_chr_fraction_range (Tuple[int, int], optional): Range of n-gram to
            check for top_ngram_chr_fraction_thresholds.
        duplicate_n_gram_fraction_thresholds (List[float], optional): The character
            fraction thresholds. Defaults to [0.15, 0.14, 0.13, 0.12, 0.11, 0.10],
            which for example denote that the any text with duplicate 5 grams
            constituting more than 15% of the text characters is filtered, 14% for
            6-grams and so on.
        duplicate_n_gram_fraction_range (Tuple[int, int], optional): The n-gram range.
            Defaults to (5, 11).
        max_length (int, optional): max_length in characters
        string (str, optional): String for filtering. Defaults to None.
        tokenizer (str, optional): Tokenizer to use. Either "nltk" or "spacy".
    """

    def __init__(
        self,
        stop_words: Optional[Set[str]] = None,
        min_stop_words: int = 2,
        mean_word_length: Tuple[int, int] = (3, 10),
        doc_length: Tuple[int, int] = (50, 100_000),
        alpha_ratio: float = 0.7,
        symbol_2_word_hashtag: float = 0.1,
        symbol_2_word_ellipsis: float = 0.1,
        max_p_begin_bullets: float = 0.9,
        max_p_end_ellipsis: float = 0.3,
        duplicate_line_fraction: float = 0.3,
        duplicate_paragraph_fraction: float = 0.3,
        duplicate_lines_chr_fraction: float = 0.2,
        duplicate_paragraph_chr_fraction: float = 0.2,
        top_ngram_chr_fraction_thresholds: List[float] = [0.20, 0.18, 0.16],
        top_ngram_chr_fraction_range: Tuple[int, int] = (2, 4),
        duplicate_n_gram_fraction_thresholds: List[float] = [
            0.15,
            0.14,
            0.13,
            0.12,
            0.11,
            0.10,
        ],
        duplicate_n_gram_fraction_range: Tuple[int, int] = (5, 11),
        max_length: int = 5_000_000,
        string_filter: Optional[str] = None,
        tokenizer: str = "NLTK",
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

        if tokenizer.lower() == "nltk":
            self.nlp.tokenizer = NLTKTokenizer(self.nlp.vocab)

        self.__set_getters()

        self.filters = {
            "doc_length": partial(self.doc_length, doc_length=doc_length),
            "mean_word_length": partial(
                self.mean_word_length, mean_word_length=mean_word_length
            ),
            "alpha_ratio": partial(self.alpha, ratio=alpha_ratio),
            "stop_word": partial(
                self.stop_word, stop_words=stop_words, n=min_stop_words
            ),
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
            "duplicate_line_fraction": lambda doc: doc._.duplicate_lines_fraction
            > duplicate_line_fraction,
            "duplicate_paragraph_fraction": lambda doc: doc._.duplicate_paragraph_fraction
            > duplicate_paragraph_fraction,
            "duplicate_lines_chr_fraction": lambda doc: doc._.duplicate_lines_chr_fraction
            > duplicate_lines_chr_fraction,
            "duplicate_paragraph_chr_fraction": lambda doc: doc._.duplicate_paragraph_chr_fraction
            > duplicate_paragraph_chr_fraction,
            "top_ngram_chr_fraction": partial(
                top_ngram_chr_fraction,
                ngram_range=top_ngram_chr_fraction_range,
                thresholds=top_ngram_chr_fraction_thresholds,
            ),
            "duplicate_n_gram_fraction": partial(
                duplicate_n_gram_fraction,
                ngram_range=duplicate_n_gram_fraction_range,
                thresholds=duplicate_n_gram_fraction_thresholds,
            ),
        }

        if string_filter:
            self.filters["string_filter"] = partial(
                self.string_filter, string=string_filter
            )
        self.filtered = Counter()
        self.nlp.max_length = max_length

    def set_getters(self):
        # getters for quality filters
        set_dynamic_ext("len", func=lambda doc: len(doc))

        # getter for rep. text filters
        set_dynamic_ext("lines", func=lambda doc: doc.text.split("\n"))
        set_dynamic_ext("paragraphs", func=lambda doc: doc.text.split("\n\n"))

        set_dynamic_ext("lines_counter", func=lambda doc: Counter(doc._.lines))
        set_dynamic_ext(
            "paragraphs_counter", func=lambda doc: Counter(doc._.paragraphs)
        )

        set_dynamic_ext(
            "duplicate_lines_fraction",
            func=partial(duplicate_fraction_getter, attr="lines_counter"),
        )

        set_dynamic_ext(
            "duplicate_paragraph_fraction",
            func=partial(duplicate_fraction_getter, attr="paragraphs_counter"),
        )

        set_dynamic_ext(
            "duplicate_lines_chr_fraction",
            func=partial(duplicate_chr_fraction_getter, attr="lines_counter"),
        )
        set_dynamic_ext(
            "duplicate_paragraph_chr_fraction",
            func=partial(duplicate_chr_fraction_getter, attr="paragraphs_counter"),
        )

        set_dynamic_ext("chr_len", func=lambda doc: len(doc.text))

    def __call__(
        self, texts: Iterable[str], as_tuples: bool = False, **kwargs
    ) -> Iterable[str]:
        """
        Applies quality filter

        Args:
            texts (Iterable[str]): An iterable of strings of the text you wish to filter.
            as_tuples (bool, optional): If True doc is expected to be a tuple of size
                two with the first element being the text. The output of this function
                    will then also be a generator of tuples filtered based on the text.
                    Defaults to False.

        Yields:
            Generator: A Generator of either texts or tuples depending on the as_tuples
                argument.
        """
        texts = iter(texts)
        docs = self.nlp.pipe(texts, as_tuples=as_tuples, **kwargs)

        while docs:
            try:
                doc = next(docs)
                if as_tuples:
                    doc, context = doc

                is_filtered = self.is_filtered(doc)
                if is_filtered is not None:
                    continue

                if as_tuples:
                    yield doc, context
                else:
                    yield doc

            except ValueError:  # max length exceeded
                self.filtered["max_chr_length"] += 1
                docs = self.nlp.pipe(texts)
            except StopIteration:
                break

    def is_filtered(self, doc: Doc) -> Optional[str]:
        """
        Check if a single document is filtered

        Args:
            doc (Doc): A spaCy document

        Returns: the name of the filter which filtered out the document or None if the
            document wasn't filtered
        """
        for filter, filter_fn in self.filters.items():
            if not filter_fn(doc):
                # log filtered documents
                self.filtered[filter] += 1
                return filter

    def describe_filter(self, texts: Iterable[tuple], **kwargs) -> Iterable[str]:
        """
        Applies quality filter and return which filter (if any) each document was
        filtered by

        Args:
            texts (Iterable[tuple]): An iterable of tuples where the first element is a
            string of the text you wish to apply quality filter to

        Yields:
            Iterable: An Iterable strings of which filter was applied to the document
                "None" indicate not filtered.
        """

        texts = iter(texts)
        docs = self.nlp.pipe(texts, **kwargs)

        while docs:
            try:
                doc = next(docs)
                is_filtered = self.is_filtered(doc)
                if is_filtered is not None:
                    yield is_filtered
                else:
                    yield "None"
            except ValueError:  # max length exceeded
                yield "max_chr_length"
                docs = self.nlp.pipe(texts)
            except StopIteration:
                break

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

        return doc_length[0] <= doc._.len <= doc_length[1]

    @staticmethod
    def mean_word_length(doc: Doc, mean_word_length: Tuple[int, int]) -> bool:
        """
        Filter document whose mean word length is outside the range of
        {mean_word_length[0]} to {mean_word_length[1]} characters

        Args:
            doc (Doc): SpaCy document
            mean_word_length (Tuple[int, int]): Tuple indicate minimum and maximum
                mean word length of document

        Returns:
            bool: A boolean indicator of whether the text passed the filter.
        """
        w_len = 0
        for t in doc:
            w_len += len(t)
        mwl = w_len / doc._.len
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

        def contains_alpha_fn(token: str):
            for c in token:
                if c.isalpha():
                    return True
            return False

        # min number of word to satisfy the ratio
        min_alpha_token = int(doc._.len * ratio)

        n_alpha_tokens = 0
        for t in doc:
            if t.is_space:
                continue
            # checks if a non-space token contains a alphabetic character
            if contains_alpha_fn(t.text):
                n_alpha_tokens += 1
                if n_alpha_tokens >= min_alpha_token:
                    return True
        return False

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
        n_symbol = doc._.text.count(symbol)
        ratio_ = n_symbol / doc._.len
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
        lines = doc._.text.split("\n")
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

        n_stopwords = 0
        for t in doc:
            if t.text in stop_words:
                n_stopwords += 1
                if n_stopwords >= n:
                    return True
        return False

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
