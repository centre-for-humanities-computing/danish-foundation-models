"""
Danish implementation of quality filter and repetitious text filter described in [1]

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

from typing import Dict, Iterable, Optional, Tuple, List, Callable
from collections import Counter, defaultdict
from functools import partial

import spacy
from spacy.tokens import Doc


def duplicate_chr_fraction_getter(doc: Doc, attr: str) -> float:
    """Calculate the character fraction of duplicates based on a counter object

    Args:
        doc (Doc): A spaCy doc
        attr (str): The document attribute to extraxct

    Returns:
        float: the fraction of duplicate chr
    """
    counter = getattr(doc._, attr)
    duplicate_chr = 0
    for t, c in counter.items():
        if c > 1:
            duplicate_chr += len(t) * (c - 1)
    frac = duplicate_chr / doc._.chr_len
    return frac


def n_gram_counter(doc: Doc, ngram_range: Tuple[int, int]) -> Dict[str, Counter]:
    """Calculate the counts of n-grams in the specified range

    Args:
        doc (Doc): a spaCy Doc
        ngram_range (Tuple[int, int]): The n-gram range

    Returns:
        Dict[str, Counter]: A dict. containing the counts of n-grams for a specific n.
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
    """Calculate the duplicate fraction of a Doc attribute based on a counter object

    Args:
        doc (Doc): A spaCy Doc
        attr (str, optional): The attribute to be extracted.
            Defaults to "lines_counter".

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
    """Set a dynamic extension which only computes when the first time otherwise fetched
    the previous results.

    Args:
        ext_name (str): The extension name which should be set
        func (Callable): The getter function for the specified extension
        dynamic_ext_prefix (str, optional): The dynamic extension prefix where to store
            if the value is already calculated. Defaults to "_".
        object (optional): The spaCy object to set the extension to. Options include
            Token, Doc, Span. Defaults to Doc.
    """

    def __create_dynamic_getter(ext_name: str, func: Callable) -> None:
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
    """
    Danish implementation of quality filter described in (Rae et al., 2021). With some
    notable changes include removing duplicate line fraction as these typically would
    either also be filtered by the duplicate line chr. fraction (similar for duplicate
    paragraph fraction) or be false positive which could contain shorter lists with
    duplicate values. see addtional changes in arguments description.

    Args:
        min_stop_words (int, optional): The least amount of stop words a text
            should have before it is kept. Defaults to 2.
        mean_word_length (Tuple[int, int], optional): Upper and lower bound on the
            mean word length. Defaults to (3, 10).
        doc_length (Tuple[int, int], optional): Upper and lower bound on the
            documents length. Defaults to (50, 100_000). The 50 words threshold is
            quite high filtering texts in general, but for filtering text for e.g.
            language modelling it ensures longer dependencies.
        alpha_ratio (float, optional): the percentage of spacy tokens in this document
            which should contain alphabetic character. Defaults to 0.6, changed from 0.8
            in [1], estimated from Danish Gigaword. Likely both due to the spaCy
            tokenizer and the relatively fewer words in languages using compound words.
        symbol_2_word_ellipsis (float, optional): The highest acceptable ratio of
            ellipsis to words. Defaults to 0.1.
        symbol_2_word_hashtag (float, optional): The highest acceptable ratio of
            symbols to words.. Defaults to 0.1.
        max_p_begin_bullets (float, optional): Maximum number of lines which begins
            with a bulletpoint. Defaults to 0.9.
        max_p_end_ellipsis (float, optional): Maximum number of lines which ends
            with an ellipsis. Defaults to 0.3.
        min_bullets (int): Minimum number of bullets there should be before the text
                is filtered. An addition from [1].
        min_ellipsis (int): Minimum number of ellipsis there should be before the text
                is filtered. An addition from [1].
        duplicate_lines_chr_fraction (float, optional): Max fraction of characters which
            is a part of a duplicate line. Defaults to 0.2
        duplicate_paragraph_chr_fraction (float, optional): Max fraction of characters
            which is a part of a duplicate paragraph. Defaults to 0.2.
        top_ngram_chr_fraction_thresholds: The maximum fraction of characters which is a
            part of the top ngram. Should be a list of floats corresponding to the
            n-grams range top_ngram_chr_fraction_range. I.e. [0.20, 0.18, 0.16] with a
            range of (2, 4) states that if the first top 20% of characters is contained
            within the top 2-gram then filter out the text. Defaults to [0.20, 0.18, 0.16].
        top_ngram_chr_fraction_range (Tuple[int, int], optional): Range of n-gram to
            check for top_ngram_chr_fraction_thresholds. Defaults to (2, 4).
        min_count (int): Minimum count of n-grams. Ignores n-grams below this
            threshold. This is to avoid filtering text with very large n-grams,
            which happens in legal text or languages with compound words. This is an
            extention to the existing filtering.
        duplicate_n_gram_fraction_thresholds (List[float], optional): The character
            fraction thresholds. Defaults to [0.25, 0.24, 0.23, 0.22, 0.21, 0.20],
            changed from [0.15, 0.14, 0.13, 0.12, 0.11, 0.10], which for example denote
            that the any text with duplicate 5 grams constituting more than 15% of the
            text characters is filtered, 14% for 6-grams and so on. The reason for the
            change is that seemingly valid text where still excluded, especially in the
            n-gram included compound words and thus where longer.
        duplicate_n_gram_fraction_range (Tuple[int, int], optional): The n-gram range.
            Defaults to (5, 11).
        max_length (int, optional): max_length in characters. Defaults to 5_000_000
        string (str, optional): String for filtering. Defaults to None.
        ignore_filters (List[str], optional): Filters which should be skipped. Options
            include: "doc_length", "mean_word_length", "alpha_ratio", "stop_word",
            "symbol_2_word_hashtag", "symbol_2_word_ellipsis",
            "line_bullets_or_ellipsis", "duplicate_lines_chr_fraction",
            "duplicate_paragraph_chr_fraction", "top_ngram_chr_fraction",
            "duplicate_ngram_chr_fraction", "string_filter"
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
    ):

        self.nlp = spacy.blank("da")

        # required docuement extension for spaCy
        self.__set_extensions()

        # a ordered dictionary of which filters to apply
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
        }

        if string_filter:
            self.filters["string_filter"] = partial(
                self.string_filter, string=string_filter
            )

        for f in ignore_filters:
            self.filters.pop(f)

        # create a counter for keeping track of how many times the specific filter
        # removed a document
        self.filtered = Counter()

        # set maximum length for the nlp pipeline.
        self.nlp.max_length = max_length

    def __set_extensions(self) -> None:
        """Sets dynamic extension such that certain values aren't calculated multiple
        times."""
        # getters for quality filters
        set_dynamic_ext("len", func=lambda doc: len(doc))
        set_dynamic_ext(
            "n_words",
            func=lambda doc: len([t for t in doc if not (t.is_space or t.is_punct)]),
        )

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
            texts (Iterable[str]): An iterable of strings of the text you wish to
                filter.
            as_tuples (bool, optional): If True doc is expected to be a tuple of size
                two with the first element being the text. The output of this function
                    will then also be a generator of tuples filtered based on the text.
                    Defaults to False.

        Yields:
            str: Either texts or tuples depending on the as_tuples
                argument.
        """
        texts = iter(texts)
        docs = self.nlp.pipe(texts, as_tuples=as_tuples, **kwargs)

        while docs:
            try:
                doc = next(docs)
                if as_tuples:  # split tuple into doc and context
                    doc, context = doc

                is_filtered = self.is_filtered(doc)

                # don't yield texts which did not pass the filter
                if is_filtered is not None:
                    continue

                if as_tuples:  # yield doc along with context
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
        n_words = 0
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


# *** Time taken to filter DAGW with 10 cores: 23077 sec ***
