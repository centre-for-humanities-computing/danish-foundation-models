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
from typing import Callable, Tuple

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
            cum_frac += chr_fraction(t) * (c - 1)
            n_duplicate += c - 1
    frac = cum_frac / n_duplicate
    return frac


if not Doc.has_extension("duplicate_lines_chr_fraction"):
    Doc.set_extension(
        "duplicate_lines_chr_fraction",
        getter=create_dynamic_getter(
            "_duplicate_lines_chr_fraction",
            getter=partial(duplicate_chr_fraction_getter, "lines_counter"),
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


def chr_fraction(text: str):
    return sum(t.isalpha() for t in text)


filters = {
    "duplicate_line_fraction": lambda doc: doc._.duplicate_lines_fraction > 0.3,
    "duplicate_paragraph_fraction": lambda doc: doc._.duplicate_paragraph_fraction
    > 0.3,
    "duplicate_lines_chr_fraction": lambda doc: doc._.duplicate_lines_chr_fraction
    > 0.2,
    "duplicate_paragraph_chr_fraction": lambda doc: doc._.duplicate_paragraph_chr_fraction
    > 0.2,
}

import re
from unicodedata import normalize
from collections import defaultdict



def n_gram(doc: Doc, ngram_range: Tuple[int, int]):
    max_len = len(doc) #doc._.len
    lower, upper = ngram_range
    shingles = defaultdict(lambda: Counter())
    for i, _ in enumerate(doc):
        for ngram_size in range(lower, upper+1):
            end = i + ngram_size
            if end <= max_len:
                shingles[ngram_size][doc[i:end]] += 1
    return shingles
    


def token_chr_fraction(token: Token):
    return sum(t.isalpha() for t in text)


def n_gram_character_fraction(doc):

    shingles = n_gram(doc, (2, 11))

    for n, threhold in [(2, 0.2), (3, 0.18), (4, 0.16)]:
        top_n_gram_chr_fraction = chr_fraction(
            shingles[n].most_common(1)[0][0])
        if top_n_gram_chr_fraction > threhold:
            return False

    for n in zip(range(5, 11), [0.15, 0.14, 0.13, 0.12, 0.11, 0.10]):
        duplicate_ngram = {ng: c for ng, c in shingles[n] if c > 1}
        n_duplicates = sum(duplicate_ngram.values())

        duplicate_c_fraction = [chr_fraction(ng) for c in ] 


import spacy
nlp = spacy.blank("da")
doc = nlp("Hej jeg hedder kenneth")
shingles = n_gram(doc, ngram_range=(2, 11))
shingles[2].most_common(1)[0][0].text