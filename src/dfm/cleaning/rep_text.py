"""
Implementation of Repetitious text filter described in [1]

Authors:
    Kenneth C. Enevoldsen

References: 
    [1] Rae, J. W., Borgeaud, S., Cai, T., Millican, K., Hoffmann, J., Song, F.,
    Aslanides, J., Henderson, S., Ring, R., Young, S., Rutherford, E., Hennigan,
    T., Menick, J., Cassirer, A., Powell, R., Driessche, G. van den, Hendricks,
    L. A., Rauh, M., Huang, P.-S., … Irving, G. (2021).
    Scaling Language Models: Methods, Analysis & Insights from Training Gopher.
    https://arxiv.org/abs/2112.11446v2
"""
from functools import partial
from typing import Callable, List, Tuple

from spacy.tokens import Doc, Token

from collections import Counter, defaultdict
from functools import lru_cache


def create_dynamic_getter(ext_name: str, func: Callable):
    def dynamic_getter(doc):
        attr = getattr(doc._, ext_name)
        if attr is None:
            setattr(doc._, ext_name, func(doc))

    Doc.set_extension(ext_name, default=None, force=True)
    return dynamic_getter()


if not Doc.has_extension("lines_counter"):
    Doc.set_extension(
        "lines_counter",
        getter=create_dynamic_getter(
            "_lines_counter", func=lambda doc: Counter(doc._.lines)
        ),
    )

if not Doc.has_extension("lines"):
    Doc.set_extension(
        "lines",
        getter=create_dynamic_getter("_lines", func=lambda doc: doc.text.split("\n")),
    )


if not Doc.has_extension("paragraphs"):
    Doc.set_extension(
        "paragraphs",
        getter=create_dynamic_getter(
            "_paragraphs", func=lambda doc: doc.text.split("\n\n")
        ),
    )

if not Doc.has_extension("paragraphs_counter"):
    Doc.set_extension(
        "paragraphs_counter",
        getter=create_dynamic_getter(
            "_paragraphs_counter", func=lambda doc: Counter(doc._.paragraphs)
        ),
    )


def __duplicate_fraction(n_total, n_unique):
    return (n_total - n_unique) / n_total


if not Doc.has_extension("duplicate_lines_fraction"):

    def dlf_getter(doc):
        counts = doc._.lines_counter
        n_lines = sum(counts.values())
        n_unique = len(k for k, c in counts.items() if c == 1)
        return __duplicate_fraction(n_lines, n_unique)

    Doc.set_extension(
        "duplicate_lines_fraction",
        getter=create_dynamic_getter("_duplicate_lines_fraction", getter=dlf_getter),
    )


if not Doc.has_extension("duplicate_paragraph_fraction"):

    def dpf_getter(doc):
        counts = doc._.paragraphs_counter
        n_paragraphs = sum(counts.values())
        n_unique = len(k for k, c in counts.items() if c == 1)

        return __duplicate_fraction(n_paragraphs, n_unique)

    Doc.set_extension(
        "duplicate_paragraph_fraction",
        getter=create_dynamic_getter(
            "_duplicate_paragraph_fraction", getter=dpf_getter
        ),
    )


def duplicate_chr_fraction_getter(doc, attr: str):
    counter = getattr(doc._, attr)
    n_duplicate = 0
    cum_frac = 0
    for t, c in counter.items():
        if c > 1:
            duplicate_chr += len(t) * (c - 1)
    frac = duplicate_chr / doc._.chr_len
    return frac


if not Doc.has_extension("duplicate_lines_chr_fraction"):
    Doc.set_extension(
        "duplicate_lines_chr_fraction",
        getter=create_dynamic_getter(
            "_duplicate_lines_chr_fraction",
            getter=partial(duplicate_chr_fraction_getter, "lines_counter"),
        ),
    )

if not Doc.has_extension("chr_len"):
    Doc.set_extension(
        "chr_len",
        getter=create_dynamic_getter(
            "_chr_len",
            getter=lambda doc: len(doc.text),
        ),
    )

if not Doc.has_extension("duplicate_paragraph_chr_fraction"):
    Doc.set_extension(
        "duplicate_lines_chr_fraction",
        getter=create_dynamic_getter(
            "_duplicate_lines_chr_fraction",
            getter=partial(duplicate_chr_fraction_getter, "paragraph_counter"),
        ),
    )


filters = {
    "duplicate_line_fraction": lambda doc: doc._.duplicate_lines_fraction > 0.3,
    "duplicate_paragraph_fraction": lambda doc: doc._.duplicate_paragraph_fraction
    > 0.3,
    "duplicate_lines_chr_fraction": lambda doc: doc._.duplicate_lines_chr_fraction
    > 0.2,
    "duplicate_paragraph_chr_fraction": lambda doc: doc._.duplicate_paragraph_chr_fraction
    > 0.2,
}


def n_gram(doc: Doc, ngram_range: Tuple[int, int]):
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


def top_ngram_chr_fraction(doc, ngram):
    shingles = doc._.n_gram_counts
    ngram, count = shingles[ngram].most_common(1)[0]
    return len(ngram) * count / doc._.chr_len


def duplicate_n_gram_fraction(
    doc: Doc,
    ngram_range: Tuple[int, int] = (5, 11),
    thresholds: List[float] = [0.15, 0.14, 0.13, 0.12, 0.11, 0.10],
) -> bool:
    """calculates the character fraction of duplicate n-gram over the overall text,
    taking care not to count overlapping n-grams twice.

    Args:
        doc (Doc): a spacy Doc
        ngram_range (Tuple[int, int], optional): The n-gram range. Defaults to (5, 11).
        thresholds (List[float], optional): The character fraction thresholds. Defaults
        to [0.15, 0.14, 0.13, 0.12, 0.11, 0.10], which for example denote that the
        any text with duplicate 5 grams constituting more than 15% of the text
        characters is filtered, 14% for 6-grams and so on.

    Returns:
        bool: a boolean indicating whether the doc passed the filter. True indicating it
        was not surpass any of the thresholds.
    """
    max_len = len(doc)  # doc._.len
    lower, upper = ngram_range

    chr_len = doc._.chr_len
    if chr_len == 0:
        return False

    max_duplicate_chr = {
        ng: t * chr_len for ng, t in zip(range(lower, upper + 1), thresholds)
    }
    ngrams = defaultdict(set)
    overlapping_char = defaultdict(int)
    minmax = defaultdict(lambda x: (0, 0))
    for i, _ in enumerate(doc):
        for ngram_size in range(lower, upper + 1):

            min_, max_ = minmax[ngram_size]

            end = i + ngram_size
            if end < max_len:
                span = doc[i:end]
                ngram = span.text.lower()
                if ngram in ngrams[ngram_size]:
                    # if it doesn't overlap update count
                    if span.start_char > max_:
                        overlapping_char[ngram_size] += max_ - min_
                        minmax[ngram_size] = span.start_char, span.end_char

                        # early stopping if invalid text
                        if max_duplicate_chr[ngram_size] < overlapping_char[ngram_size]:
                            return False
                    else:
                        # extend range of duplicates
                        minmax[ngram_size][1] = span.end_char

    for ngram_size in range(lower, upper + 1):
        min_, max_ = minmax[ngram_size]
        overlapping_char[ngram_size] += max_ - min_
        if max_duplicate_chr[ngram_size] < overlapping_char[ngram_size]:
            return False
    return True


# def n_gram_character_fraction(doc):

#     shingles = n_gram(doc, (2, 11))

#     for n, threhold in [(2, 0.2), (3, 0.18), (4, 0.16)]:
#         top_n_gram_chr_fraction = chr_fraction(
#             shingles[n].most_common(1)[0][0])
#         if top_n_gram_chr_fraction > threhold:
#             return False


import spacy

nlp = spacy.blank("da")
doc = nlp("Hej jeg hedder kenneth, hej jeg")
doc[1:3].end_char
shingles = n_gram(doc, ngram_range=(2, 11))
shingles[2].most_common(1)[0][0]
