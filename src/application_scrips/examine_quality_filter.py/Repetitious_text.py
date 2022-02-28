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
from collections import Counter


def __duplicate_fraction(text: str, split: str):
    lines = list(filter(lambda x: x.strip(), text.split(split)))
    n_lines = len(lines)
    n_unique_lines = len(set(lines))
    duplicate = n_lines - n_unique_lines
    return duplicate / n_lines


def duplicate_line_fraction(text):
    return __duplicate_fraction(text, split="\n")


def duplicate_paragraph_fraction(text):
    return __duplicate_fraction(text, split="\n\n")


def character_fraction(text):
    """what exactly is character fraction?"""
    n_chr = 0
    for n, c in enumerate(text):
        if not c.isalpha():
            n_chr += 1
    return n_chr / n


def test_duplicate_line_fraction():
    text = "Hej mit navn er kenneth. \n "
    assert duplicate_line_fraction(text * 3) > 0.30
    assert duplicate_line_fraction(text) < 0.30


def __duplicate_line_character_fraction(text: str, split: str):
    lines = Counter(filter(lambda x: x.strip(), text.split(split)))

    duplicates = {line: c for line, c in lines.items() if c > 1}
    n_lines = sum(lines.values())
    n_duplicates = sum(duplicates.values())

    # duplicate fraction too high
    if n_duplicates / n_lines > 0.30:
        return False

    # duplicate character fraction
    c_fraction = (
        sum(character_fraction(line) * c for line, c in duplicates.items())
        / n_duplicates
    )
    if c_fraction > 0.20:
        return False
    return True


# Counter for n-grams
#   check top
#   check duplicates

import re
from unicodedata import normalize
from collections import defaultdict

doc = "Hej mit navn er kenneth, men mit navn er Arne og hans havn er svend!"


def n_gram_character_fraction(doc):
    doc = normalize("NFKC", doc)
    doc = re.sub(r"[\.\,\:\;\!\?\(\)\[\]\{\}]", " ", doc)
    doc = re.sub(" +", " ", doc)

    words = list(filter(lambda x: x, doc.split(" ")))

    shingles = defaultdict(lambda: Counter())
    max_len = len(words)
    for i, _ in enumerate(words):
        for ngram_size in range(2, 11):
            end = i + ngram_size
            if end <= max_len:
                shingles[ngram_size][tuple(words[i:end])] += 1

    for n, threhold in [(2, 0.2), (3, 0.18), (4, 0.16)]:
        top_n_gram_chr_fraction = character_fraction(
            "".join(shingles[n].most_common(1)[0][0])
        )
        if top_n_gram_chr_fraction > threhold:
            return False

    for n in zip(range(5, 11), [0.15, 0.14, 0.13, 0.12, 0.11, 0.10]):
        duplicate_ngram = {ng: c for ng, c in shingles[n] if c > 1}
        n_duplicates = sum(duplicate_ngram.values())

        duplicate_c_fraction = [character_fraction(ng) for c in ] 


import time
for i in [10, 100, 1000, 10000, 100000, 1000000, 10000000, 100000000]:
    text = "Hej mit navn er kenneth, men mit navn er Arne og hans havn er svend!"*i
    s = time.time()
    "test" in text
    print(i, ":", time.time()-s)