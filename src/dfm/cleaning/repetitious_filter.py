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

from typing import Callable, List, Tuple

from spacy.tokens import Doc

from collections import Counter, defaultdict


def set_dynamic_ext(
    ext_name: str, func: Callable, dynamic_ext_prefix: str = "_", object=Doc
) -> None:
    if not object.has_extension(ext_name):
        object.set_extension(
            ext_name,
            getter=create_dynamic_getter(dynamic_ext_prefix + ext_name, func=func),
        )


def create_dynamic_getter(ext_name: str, func: Callable) -> None:
    def dynamic_getter(doc):
        attr = getattr(doc._, ext_name)
        if attr is None:
            setattr(doc._, ext_name, func(doc))

    Doc.set_extension(ext_name, default=None, force=True)
    return dynamic_getter()


def __duplicate_fraction(n_total, n_unique):
    return (n_total - n_unique) / n_total


def duplicate_fraction_getter(doc, attr: str = "lines_counter"):
    counts = getattr(doc._, attr)
    n_lines = sum(counts.values())
    n_unique = len(k for k, c in counts.items() if c == 1)
    return __duplicate_fraction(n_lines, n_unique)


def duplicate_chr_fraction_getter(doc, attr: str):
    counter = getattr(doc._, attr)
    duplicate_chr = 0
    for t, c in counter.items():
        if c > 1:
            duplicate_chr += len(t) * (c - 1)
    frac = duplicate_chr / doc._.chr_len
    return frac


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


def top_ngram_chr_fraction(
    doc,
    ngram_range: Tuple[int, int] = (2, 4),
    thresholds: List[float] = [0.20, 0.18, 0.16],
):
    ngram_counter = n_gram(doc, ngram_range=ngram_range)
    for n, threshold in zip(ngram_counter, thresholds):
        ngram, count = ngram_counter[n].most_common(1)[0]
        frac = len(ngram) * count / doc._.chr_len
        if frac > threshold:
            return False
    return True


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
        thresholds (List[float], optional): The character fraction thresholds.
            Defaults to [0.15, 0.14, 0.13, 0.12, 0.11, 0.10], which for example denote
            that the any text with duplicate 5 grams constituting more than 15% of the
            text characters is filtered, 14% for 6-grams and so on.

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


import spacy

nlp = spacy.blank("da")
doc = nlp("Hej jeg hedder kenneth, hej jeg")
doc[1:3].end_char
shingles = n_gram(doc, ngram_range=(2, 11))
shingles[2].most_common(1)[0][0]
