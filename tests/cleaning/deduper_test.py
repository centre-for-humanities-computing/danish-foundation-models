"""Tests for the deduplication module"""

from dfm.cleaning import Deduper
import tempfile
from pathlib import Path
import json
import re


def word_shape(doc: str) -> str:
    '''Aggressive normalization function used in unit tests.

    Args:
        doc (str): The document to normalize.

    Returns:
        str: The normalized document.
    '''
    return re.sub("[A-Z]", "X", re.sub("[^A-Z ]", "x", doc))


def identity_fn(doc: str) -> str:
    '''Identity function used in unit tests.

    Args:
        doc (str): The document to normalize.

    Returns:
        str: The normalized document.
    '''
    return doc


class TestDeduper:
    def deduper(self, **kwargs):
        default_test_args = dict(ngram_size=1, random_seed=42, verbose=False)
        return Deduper(**dict(default_test_args, **kwargs))

    def dedup(self, corpus, **kwargs):
        temp = tempfile.TemporaryDirectory()
        deduper = self.deduper(**kwargs)
        deduper.deduplicate(corpus, output_dir=str(temp), overwrite=True)
        deduped_corpus = Path(str(temp)) / "deduplicated_corpus.jsonl"
        return [json.loads(line)["text"] for line in deduped_corpus.open("r")]

    def miss_percentage(self, corpus=None, iterations=100, **kwargs):
        corpus = corpus or [
            "Der kom en soldat marcherende hen ad landevejen:\n "
            "én, to, tre! én, to, tre!",
            "Da kom en soldat marcherende hen ad landevejen:\n "
            "én, to, tre! én, to, tre!",
        ]
        misses = 0
        for i in range(0, iterations):
            if len(self.dedup(corpus, random_seed=i, **kwargs)) == 2:
                misses += 1
        return (100.0 * misses) / iterations

    def test_removes_exact_duplicates(self):
        assert self.dedup(
            ["hej med dig min ven", "hej med dig min ven", "farvel du gamle"]
        ) == ["hej med dig min ven", "farvel du gamle"]

    def test_removes_near_duplicates(self):
        assert self.dedup(
            [
                "Der kom en soldat marcherende hen ad landevejen:\n "
                "én, to, tre! én, to, tre!",
                "Da kom en soldat marcherende hen ad landevejen:\n "
                "én, to, tre! én, to, tre!",
            ]
        ) == [
            "Der kom en soldat marcherende hen ad landevejen:\n "
            "én, to, tre! én, to, tre!"
        ]

    def test_document_shorter_than_shingles(self):
        assert self.dedup(
            ["Hej med dig", "Hej med dig", "Gå din vej"], ngram_size=13
        ) == ["Hej med dig", "Gå din vej"]

    def test_split_by_word_ngram(self):
        assert self.dedup(
            [
                "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
                "Er kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
            ],
            split_method="word_ngram",
            ngram_size=5,
        ) == ["Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!"]

    def test_split_by_paragraph(self):
        assert self.dedup(
            [
                "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
                "Er kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
            ],
            split_method="paragraph",
        ) == [
            "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
            "Er kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
        ]

    def test_do_not_split(self):
        assert self.dedup(
            [
                "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
                "Er kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
            ],
            split_method="none",
        ) == [
            "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
            "Er kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
        ]

    def test_no_normalization(self):
        identity = lambda doc: doc
        assert self.dedup(
            [
                "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
                "Der kom en soldat marcherende hen ad landevejen!\n én. to? én; to?",
            ],
            normalization_func=identity,
        ) == [
            "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
            "Der kom en soldat marcherende hen ad landevejen!\n én. to? én; to?",
        ]

    def test_aggresive_normalization(self):
        word_shape = lambda doc: re.sub("[A-Z]", "X", re.sub("[^A-Z ]", "x", doc))
        assert self.dedup(
            [
                "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
                "Den var jo typisk påtrængende pæn og overrasket:\n et, tu! et, tu!",
            ],
            normalization_func=word_shape,
        ) == ["Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!"]

    def test_2_minhashes(self):
        miss = self.miss_percentage(num_minhashes=2)
        assert miss >= 35
        assert miss <= 40

    def test_128_minhashes(self):
        miss = self.miss_percentage(num_minhashes=128)
        assert miss >= 30
        assert miss <= 35

    def test_256_minhashes(self):
        miss = self.miss_percentage(num_minhashes=256)
        assert miss >= 20
        assert miss <= 30

    def test_2_ngram_shingles(self):
        shingles = self.deduper(ngram_size=2)._get_shingles("Hej med dig Kim")
        assert shingles == ["Hej med", "med dig", "dig Kim"]

    def test_3_ngram_shingles(self):
        shingles = self.deduper(ngram_size=3)._get_shingles("Hej med dig Kim")
        assert shingles == ["Hej med dig", "med dig Kim"]

    def test_double_stride_shingles(self):
        shingles = self.deduper(ngram_stride=2)._get_shingles("Hej med dig Kim")
        assert shingles == ["Hej", "dig"]