"""Filter on document level.

This is a Danish implementation of quality filter and repetitious text filter described
in [1], which has been extended with filters based on [2] (language detection) and [3]
(short/long sentence ratio).

Authors:
    Kenneth C. Enevoldsen (kennethcenevoldsen@gmail.com)
    Kasper Junge (kasper.junge@eb.dk)
    Malte Højmark-Bertelsen (hjb@kmd.dk)
    Philip Krejler (pk@capacit.com)
    Dan Saattrup Nielsen (dan.nielsen@alexandra.dk)

References:
    [1] Rae, J. W., Borgeaud, S., Cai, T., Millican, K., Hoffmann, J., Song, F., ... &
        Irving, G. (2021). Scaling language models: Methods, analysis & insights from
        training gopher. arXiv preprint arXiv:2112.11446.
    [2] Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M., ... &
        Liu, P. J. (2020). Exploring the limits of transfer learning with a unified
        text-to-text transformer. J. Mach. Learn. Res., 21(140), 1-67.
    [3] Abadji, Julien, et al. "Towards a Cleaner Document-Oriented Multilingual
        Crawled Corpus." arXiv preprint arXiv:2201.06642 (2022).
"""

from collections import Counter, defaultdict
from functools import partial
from typing import (
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    Any,
)

import spacy
from langdetect import detect_langs
from luga import language
from spacy.tokens import Doc


def duplicate_chr_fraction_getter(doc: Doc, attr: str) -> float:
    """Calculate the character fraction of duplicates based on a counter object.

    Args:
        doc (Doc):
            A spaCy Doc.
        attr (str):
            The document attribute to extract.

    Returns:
        float:
            The fraction of duplicate characters.
    """
    counter = getattr(doc._, attr)
    duplicate_chr = 0
    for t, c in counter.items():
        if c > 1:
            duplicate_chr += len(t) * (c - 1)
    frac = duplicate_chr / doc._.chr_len
    return frac


def n_gram_counter(doc: Doc, ngram_range: Tuple[int, int]) -> Dict[str, Counter]:
    """Calculate the counts of n-grams in the specified range.

    Args:
        doc (Doc):
            A spaCy Doc.
        ngram_range (pair of int):
            The n-gram range.

    Returns:
        dict with str keys and Counter values:
            A dictionary containing the counts of n-grams for a specific n.
    """
    max_len = doc._.len
    lower, upper = ngram_range
    shingles_count = defaultdict(lambda: Counter())
    for i, _ in enumerate(doc):
        for ngram_size in range(lower, upper + 1):
            end = i + ngram_size
            if end < max_len:
                span = doc[i:end]
                shingles_count[ngram_size][span.text.lower()] += 1
    return shingles_count


def duplicate_fraction_getter(doc: Doc, attr: str = "lines_counter") -> float:
    """Calculate the duplicate fraction of a Doc attribute based on a counter object.

    Args:
        doc (Doc):
            A spaCy Doc
        attr (str, optional):
            The attribute to be extracted. Defaults to "lines_counter".

    Returns:
        float: the duplicate fraction
    """
    counts = getattr(doc._, attr)
    counts = {k: v for k, v in counts.items() if k.strip()}
    n_lines = sum(counts.values())
    n_unique = len([k for k, c in counts.items() if c == 1])
    duplicate_fraction = (n_lines - n_unique) / n_lines
    return duplicate_fraction


def set_dynamic_ext(
    ext_name: str, func: Callable, dynamic_ext_prefix: str = "_", object=Doc
) -> None:
    """Sets a dynamic extension to reduce redundant computation.

    This only computes when the first time, and otherwise fetched the previous results.

    Args:
        ext_name (str):
            The extension name which should be set.
        func (Callable):
            The getter function for the specified extension.
        dynamic_ext_prefix (str, optional):
            The dynamic extension prefix where to store if the value is already
            calculated. Defaults to "_".
        object (optional):
            The spaCy object to set the extension to. Options include Token, Doc, Span.
            Defaults to Doc.
    """

    def __create_dynamic_getter(ext_name: str, func: Callable) -> Callable:
        def dynamic_getter(doc):
            attr = getattr(doc._, ext_name)
            if attr is None:
                attr = func(doc)
                setattr(doc._, ext_name, attr)
            return attr

        Doc.set_extension(ext_name, default=None, force=True)
        return dynamic_getter

    if not object.has_extension(ext_name):
        object.set_extension(
            ext_name,
            getter=__create_dynamic_getter(dynamic_ext_prefix + ext_name, func=func),
        )


class QualityFilter:
    """Document-level filter.

    This is a Danish implementation of quality filter described in [1]. With some
    notable changes include removing duplicate line fraction as these typically would
    either also be filtered by the duplicate line chr. fraction (similar for duplicate
    paragraph fraction) or be false positive which could contain shorter lists with
    duplicate values. see addtional changes in arguments description.

    Args:
        min_stop_words (int, optional):
            The least amount of stop words a text should have before it is kept.
            Defaults to 2.
        mean_word_length (pair of int, optional):
            Upper and lower bound on the mean word length. Defaults to (3, 10).
        doc_length (pair of int, optional):
            Upper and lower bound on the documents length. Defaults to (50, 100_000).
        alpha_ratio (float, optional):
            The percentage of spacy tokens in this document which should contain
            alphabetic character. Defaults to 0.6.
        symbol_2_word_ellipsis (float, optional):
            The highest acceptable ratio of ellipsis to words. Defaults to 0.1.
        symbol_2_word_hashtag (float, optional):
            The highest acceptable ratio of symbols to words.. Defaults to 0.1.
        max_p_begin_bullets (float, optional):
            Maximum number of lines which begins with a bulletpoint. Defaults to 0.9.
        max_p_end_ellipsis (float, optional):
            Maximum number of lines which ends with an ellipsis. Defaults to 0.3.
        min_bullets (int):
            Minimum number of bullets there should be before the text is filtered. An
            addition from [1].
        min_ellipsis (int):
            Minimum number of ellipsis there should be before the text is filtered. An
            addition from [1].
        duplicate_lines_chr_fraction (float, optional):
            Max fraction of characters which is a part of a duplicate line. Defaults to
            0.2
        duplicate_paragraph_chr_fraction (float, optional): Max fraction of characters
            which is a part of a duplicate paragraph. Defaults to 0.2.
        top_ngram_chr_fraction_thresholds (list of float):
            The maximum fraction of characters which is a part of the top ngram. Should
            be a list of floats corresponding to the n-grams range
            top_ngram_chr_fraction_range, i.e., [0.20, 0.18, 0.16] with a range of (2,
            4) states that if the first top 20% of characters is contained within the
            top 2-gram then filter out the text. Defaults to [0.20, 0.18, 0.16].
        top_ngram_chr_fraction_range (pair of int, optional):
            Range of n-gram to check for top_ngram_chr_fraction_thresholds. Defaults to
            (2, 4).
        min_count (int):
            Minimum count of n-grams. Ignores n-grams below this threshold. This is to
            avoid filtering text with very large n-grams, which happens in legal text
            or languages with compound words. This is an extention to the existing
            filtering.
        duplicate_n_gram_fraction_thresholds (list of float, optional):
            The character fraction thresholds. Defaults to [0.25, 0.24, 0.23, 0.22,
            0.21, 0.20].
        duplicate_n_gram_fraction_range (pair of int, optional):
            The n-gram range. Defaults to (5, 11).
        max_length (int, optional):
            Maximum character length of a document. Defaults to 5_000_000.
        string (str or None, optional):
            String for filtering. Defaults to None.
        ignore_filters (list of str, optional):
            Filters which should be skipped. Options include:
                - "doc_length"
                - "mean_word_length"
                - "alpha_ratio"
                - "stop_word"
                - "symbol_2_word_hashtag"
                - "symbol_2_word_ellipsis"
                - "line_bullets_or_ellipsis"
                - "duplicate_lines_chr_fraction"
                - "duplicate_paragraph_chr_fraction"
                - "top_ngram_chr_fraction"
                - "duplicate_ngram_chr_fraction"
                - "string_filter"
        language_detection_tool (str, optional):
            The language detection tool to use. Options include "luga" or "langdetect".
            Defaults to "luga".
        language_threshold (float, optional):
            The threshold used for minimum confidence in langauge detection. If the
            language detection model outputs a probability lower than the threshold,
            then the document will be discarded. Defaults to 0.9.
        languages (list of str, optional):
            Sequence of languages to perform language detection for. Defaults to
            ['da'].
        short_long_sentence_length_split (int, optional):
            Number of characters to determine whether short or long sentence - if
            number of characters exceed short_long_sentence_length_split then it is
            classfied as a long sentence, and vice versa. Defaults to 30.
        short_long_sentence_ratio (float, optional):
            The threshold for minimum ratio between short and long sentences, with the
            short/long distinction defined by `short_long_sentence_length_split`. If
            the ratio n_long / (n_long + n_short)  is below the threshold, the document will be
            discarded. Defaults to 0.5.

    References:
        [1] Rae, J. W., Borgeaud, S., Cai, T., Millican, K., Hoffmann, J., Song, F.,
            ... & Irving, G. (2021). Scaling language models: Methods, analysis &
            insights from training gopher. arXiv preprint arXiv:2112.11446.
    """

    def __init__(
        self,
        min_stop_words: int = 2,
        mean_word_length: Tuple[int, int] = (3, 10),
        doc_length: Tuple[int, int] = (50, 100_000),
        alpha_ratio: float = 0.6,
        symbol_2_word_hashtag: float = 0.1,
        symbol_2_word_ellipsis: float = 0.1,
        max_p_begin_bullets: float = 0.9,
        max_p_end_ellipsis: float = 0.3,
        min_bullets: int = 2,
        min_ellipsis: int = 2,
        duplicate_lines_chr_fraction: float = 0.2,
        duplicate_paragraph_chr_fraction: float = 0.2,
        top_ngram_chr_fraction_thresholds: List[float] = [0.20, 0.18, 0.16],
        top_ngram_chr_fraction_range: Tuple[int, int] = (2, 4),
        top_ngram_min_count: int = 3,
        duplicate_n_gram_fraction_thresholds: List[float] = [
            0.25,
            0.24,
            0.23,
            0.22,
            0.21,
            0.20,
        ],
        duplicate_n_gram_fraction_range: Tuple[int, int] = (5, 10),
        max_length: int = 5_000_000,
        string_filter: Optional[str] = None,
        ignore_filters: List[str] = [],
        language_detection_tool: str = "luga",
        language_threshold: float = 0.90,
        languages: Sequence[str] = ["da"],
        short_long_sentence_length_split: int = 30,
        short_long_sentence_threshold: float = 0.5,
    ):

        __available_language_detection_tools = ["langdetect", "luga"]

        if language_detection_tool not in __available_language_detection_tools:
            raise AttributeError(
                f"{language_detection_tool} is not a valid language detection "
                f"packages - must be in {__available_language_detection_tools}"
            )

        # Load Danish spaCy model
        self.nlp = spacy.blank("da")

        # Required document extension for spaCy
        self.__set_extensions()

        # An ordered dictionary of which filters to apply
        self.filters = {
            "doc_length": partial(self.doc_length, doc_length=doc_length),
            "mean_word_length": partial(
                self.mean_word_length, mean_word_length=mean_word_length
            ),
            "alpha_ratio": partial(self.alpha, ratio=alpha_ratio),
            "stop_word": partial(self.stop_word, n=min_stop_words),
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
                min_bullets=min_bullets,
                min_ellipsis=min_ellipsis,
            ),
            "duplicate_lines_chr_fraction": partial(
                self.duplicate_lines_chr_filter, fraction=duplicate_lines_chr_fraction
            ),
            "duplicate_paragraph_chr_fraction": partial(
                self.duplicate_paragraph_chr_fraction_filter,
                fraction=duplicate_paragraph_chr_fraction,
            ),
            "top_ngram_chr_fraction": partial(
                self.top_ngram_chr_fraction_filter,
                ngram_range=top_ngram_chr_fraction_range,
                thresholds=top_ngram_chr_fraction_thresholds,
                min_count=top_ngram_min_count,
            ),
            "duplicate_ngram_chr_fraction": partial(
                self.duplicate_ngram_fraction_filter,
                ngram_range=duplicate_n_gram_fraction_range,
                thresholds=duplicate_n_gram_fraction_thresholds,
            ),
            "detect_language": partial(
                self.detect_language,
                language_detection_tool=language_detection_tool,
                languages=languages,
                language_threshold=language_threshold,
            ),
            "short_long_sentece": partial(
                self.short_long_sentence,
                short_long_sentence_length_split=short_long_sentence_length_split,
                short_long_sentence_threshold=short_long_sentence_threshold,
            ),
        }

        if string_filter:
            self.filters["string_filter"] = partial(
                self.string_filter, string=string_filter
            )

        for f in ignore_filters:
            self.filters.pop(f)

        # Create a counter for keeping track of how many times the specific filter
        # removed a document
        self.filtered = Counter()

        # Set maximum length for the nlp pipeline.
        self.nlp.max_length = max_length

    def __set_extensions(self) -> None:
        """Sets dynamic extension to avoid redundant calculations."""
        # Getters for quality filters
        set_dynamic_ext("len", func=lambda doc: len(doc))
        set_dynamic_ext(
            "n_words",
            func=lambda doc: len([t for t in doc if not (t.is_space or t.is_punct)]),
        )

        # Getter for rep. text filters
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

    def filter_corpus(
        self, texts: Iterable[str], as_tuples: bool = False, **kwargs
    ) -> Union[Iterable[str], Iterable[Tuple[str, Union[Any, None]]]]:
        """Applies quality filter.

        Args:
            texts (iter of str):
                An iterable of strings of the text you wish to filter.
            as_tuples (bool, optional):
                If True doc is expected to be a tuple of size two with the first
                element being the text. The output of this function will then also be a
                generator of tuples filtered based on the text. Defaults to False.

        Yields:
            str or pair:
                Either texts or tuples depending on the as_tuples argument.
        """
        texts = iter(texts)
        docs = self.nlp.pipe(texts, as_tuples=as_tuples, **kwargs)

        while docs:
            try:
                doc = next(docs)

                # Split tuple into doc and context
                if as_tuples:
                    doc, context = doc

                is_filtered = self.is_filtered(doc)

                # Don't yield texts which did not pass the filter
                if is_filtered is not None:
                    continue

                # Yield doc along with context
                if as_tuples:
                    yield doc, context
                else:
                    yield doc

            # Max length exceeded
            except ValueError:
                self.filtered["max_chr_length"] += 1
                docs = self.nlp.pipe(texts)
            except StopIteration:
                break

    def __call__(
        self, *args, **kwargs
    ) -> Union[Iterable[str], Iterable[Tuple[str, Union[Any, None]]]]:
        """Applies quality filter.

        Args:
            *args:
                Positional arguments to be passed to `filter_corpus`.
            **kwargs:
                Keyword arguments to be passed to `filter_corpus`.

        Yields:
            str or pair:
                Either texts or tuples depending on the as_tuples argument.
        """
        return self.filter_corpus(*args, **kwargs)

    def is_filtered(self, doc: Doc) -> Optional[str]:
        """Check if a single document is filtered

        Args:
            doc (Doc):
                A spaCy document

        Returns:
            str or None:
                The name of the filter which filtered out the document or None if the
                document wasn't filtered.
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
                ""passed filters"" indicate not filtered.
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
                    yield "passed filters"
            except ValueError:  # max length exceeded
                yield "max_chr_length"
                docs = self.nlp.pipe(texts)
            except StopIteration:
                break

    @staticmethod
    def short_long_sentence(
        doc: Doc,
        short_long_sentence_length_split: int,
        short_long_sentence_threshold: float,
    ) -> bool:
        """Checks that the ratio long sentences is above the minimum threshold.

        Inspired by implementation:
        https://github.com/oscar-corpus/ungoliant/blob/master/src/filtering/record.rs

        Args:
            doc (Doc):
                Document to check

        Returns:
            bool:
                True if the ratio long sentences is above the minimum threshold
        """
        sentences = [
            sentence.strip()
            for sentence in doc.text.split("\n")
            if len(sentence.strip()) > 0
        ]
        _long_count = 0
        _short_count = 0
        for sentence in sentences:
            if len(sentence) > short_long_sentence_length_split:
                _long_count += 1
            else:
                _short_count += 1
        ratio = _long_count / (_long_count + _short_count)
        return ratio >= short_long_sentence_threshold

    @staticmethod
    def detect_language(
        doc: Doc,
        language_detection_tool: str,
        languages: Sequence[str],
        language_threshold: float,
    ) -> bool:
        """Detects if a specified (or sequence of languages) is detected.

        Args:
            language_detection_tool (str):
                Two toolboxes are currently supported, `luga` and `langdetect`.
            languages (sequence of str):
                Sequence of languages to detect for.
            language_threshold (float):
                Minimum threshold for detection probability.

        Returns:
            bool:
                Boolean whether one of the specified languages is detected with
                probability higher than threshold.
        """

        def luga_detect(
            doc: Doc, languages: Sequence[str], language_threshold: float
        ) -> bool:
            doc_joined = " ".join(
                [
                    sentence.strip()
                    for sentence in doc.text.split("\n")
                    if len(sentence.strip()) > 0
                ]
            )
            detected = language(doc_joined)  # type: ignore
            lang, score = detected.name, detected.score
            if score >= language_threshold and lang in languages:
                return True
            else:
                return False

        def langdetect_detect(
            doc: Doc, languages: Sequence[str], language_threshold: float
        ) -> bool:
            detected = detect_langs(doc.text)  # type: ignore
            for l in detected:
                if l.lang in languages and l.prob >= language_threshold:
                    return True
            return False

        detectors: Dict[str, Callable[[Doc, Sequence[str], float], bool]] = {
            "luga": luga_detect,
            "langdetect": langdetect_detect,
        }

        return detectors[language_detection_tool](doc, languages, language_threshold)

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
        return doc_length[0] <= doc._.n_words <= doc_length[1]

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
            if t.is_space or t.is_punct:
                continue
            w_len += len(t)
        mwl = w_len / doc._.n_words
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
        min_alpha_token = int(doc._.n_words * ratio)

        n_alpha_tokens = 0
        for t in doc:
            if t.is_space or t.is_punct:
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
        n_symbol = doc.text.count(symbol)
        ratio_ = n_symbol / doc._.n_words
        return ratio_ < ratio

    @staticmethod
    def line_bullets_or_ellipsis(
        doc: Doc,
        max_p_bullets: float,
        max_p_ellipsis: float,
        min_bullets: int,
        min_ellipsis: int,
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
            min_bullets (int): Minimum number of bullets there should be before the text
                is filtered
            min_ellipsis (int): Minimum number of ellipsis there should be before the text
                is filtered

        Returns:
            bool: A boolean indicator of whether the text passed the filter.
        """
        lines = doc.text.split("\n")
        if lines:
            n_bullets = sum(
                1 for line in lines if line.strip(" ").startswith(("-", "*"))
            )
            n_lines = len(lines)
            if (n_bullets / n_lines) > max_p_bullets and n_bullets > min_bullets:
                return False
            n_ellipsis = sum(
                1 for line in lines if line.strip(" ").endswith(("…", "..."))
            )
            if (n_ellipsis / n_lines) > max_p_ellipsis and n_ellipsis > min_ellipsis:
                return False
            return True
        return False

    @staticmethod
    def stop_word(doc: Doc, n: int) -> bool:
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
            if t.is_stop:
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

    @staticmethod
    def duplicate_ngram_fraction_filter(
        doc: Doc,
        ngram_range: Tuple[int, int],
        thresholds: List[float],
    ) -> bool:
        """calculates the character fraction of duplicate n-gram over the overall text,
        taking care not to count overlapping n-grams twice.

        Args:
            doc (Doc): a spacy Doc
            ngram_range (Tuple[int, int], optional): The n-gram range.
            thresholds (List[float], optional): The character fraction thresholds.

        Returns:
            bool: a boolean indicating whether the doc passed the filter. True
                indicating it was not surpass any of the thresholds.
        """
        max_len = doc._.len
        lower, upper = ngram_range

        chr_len = doc._.chr_len
        if chr_len == 0:
            return False

        # calcuate maximum chr. limits according to thresholds
        max_duplicate_chr = {
            ng: t * chr_len for ng, t in zip(range(lower, upper + 1), thresholds)
        }
        ngrams = defaultdict(set)
        duplicate_char = defaultdict(int)
        minmax = defaultdict(lambda: [0, 0])

        for i, _ in enumerate(doc):
            for ngram_size in range(lower, upper + 1):

                min_, max_ = minmax[ngram_size]
                end = i + ngram_size

                if end < max_len:
                    span = doc[i:end]
                    ngram = span.text.lower()  # create n-gram from span

                    if ngram in ngrams[ngram_size]:
                        # if it doesn't overlap with other ngrams of the same size
                        # update
                        if span.start_char > max_:
                            duplicate_char[ngram_size] += max_ - min_
                            minmax[ngram_size] = [span.start_char, span.end_char]

                            # early stopping if duplicate char. is higher than allowed
                            if (
                                max_duplicate_chr[ngram_size]
                                < duplicate_char[ngram_size]
                            ):
                                return False
                        else:
                            # extend range of duplicates
                            minmax[ngram_size][1] = span.end_char
                    else:
                        ngrams[ngram_size].add(ngram)

        # empty buffer for of duplicate chr. which have yet to be added.
        for ngram_size in range(lower, upper + 1):
            min_, max_ = minmax[ngram_size]
            duplicate_char[ngram_size] += max_ - min_
            if max_duplicate_chr[ngram_size] < duplicate_char[ngram_size]:
                return False
        return True

    @staticmethod
    def top_ngram_chr_fraction_filter(
        doc: Doc,
        ngram_range: Tuple[int, int],
        thresholds: List[float],
        min_count: int,
    ) -> bool:
        """Calculated whether the character fraction of the top n-grams is below the
        given thresholds

        Args:
            doc (Doc): A spaCy doc
            ngram_range (Tuple[int, int], optional): Range of n grams to examine.
            thresholds (List[float], optional): Maximum character fraction of n-gram.
            min_count (int): Minimum count of n-grams. Ignores n-grams below this
                threshold. This is to avoid filtering text with very large n-grams,
                which happens in legal text or languages with compound words.

        Returns:
            bool: a boolean indicator returns True if the Doc is not filtered.
        """
        ngram_counter = n_gram_counter(doc, ngram_range=ngram_range)
        for n, threshold in zip(ngram_counter, thresholds):
            ngram, count = ngram_counter[n].most_common(1)[0]
            frac = len(ngram) * count / doc._.chr_len
            if frac > threshold and count > min_count:
                return False
        return True

    @staticmethod
    def duplicate_paragraph_chr_fraction_filter(doc: Doc, fraction: float) -> bool:
        """Filters if the fraction of characters in duplicate paragraphs exceeds
        the specified threshold

        Args:
            doc (Doc): A spaCy Doc
            fraction (float): The maximum fraction of duplicate characters

        Returns:
            bool: A boolean indicator of whether the text passed the filter.
        """
        return doc._.duplicate_paragraph_chr_fraction < fraction

    @staticmethod
    def duplicate_lines_chr_filter(doc: Doc, fraction: float) -> bool:
        """Filters if the fraction of characters in duplicate lines exceeds
        the specified threshold

        Args:
            doc (Doc): A spaCy Doc
            fraction (float): The maximum fraction of duplicate characters

        Returns:
            bool: A boolean indicator of whether the text passed the filter.
        """
        return doc._.duplicate_lines_chr_fraction < fraction

    @staticmethod
    def duplicate_paragraph_filter(doc: Doc, fraction: float) -> bool:
        """Filters if the fraction of duplicate paragraphs exceeds
        the specified threshold

        Args:
            doc (Doc): A spaCy Doc
            fraction (float): The maximum fraction of duplicate paragraphs

        Returns:
            bool: A boolean indicator of whether the text passed the filter.
        """
        return doc._.duplicate_paragraph_fraction < fraction

    @staticmethod
    def duplicate_line_filter(doc: Doc, fraction: float) -> bool:
        """Filters if the fraction of duplicate lines exceeds
        the specified threshold

        Args:
            doc (Doc): A spaCy Doc
            fraction (float): The maximum fraction of duplicate lines

        Returns:
            bool: A boolean indicator of whether the text passed the filter.
        """
        return doc._.duplicate_lines_fraction < fraction


if __name__ == "__main__":
    # Benchmarking script on cleaned DAGW + Reddit.
    # Took x hours and xx minutes on xxx.
    # Previously took 6 hours and 25 minutes with 10 cores.

    from datasets import load_dataset
    import time

    # Initialise the filter
    doc_filter = QualityFilter()

    # Load the dataset
    dagw = load_dataset(
        "DDSC/dagw_reddit_filtered_v1.0.0",
        split="train",
        use_auth_token=True,
    )

    # Create filter generator
    filtered_docs = doc_filter(dagw["text"])

    # Initialise timer
    t0 = time.time()

    # Filter the texts
    for doc in filtered_docs:
        pass

    # Record the time taken
    time_taken = time.time() - t0

    # Print the time taken
    print(f"Time taken: {time_taken} seconds.")
