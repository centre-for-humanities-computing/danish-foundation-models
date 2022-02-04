from dfm.cleaning import Deduper

import pytest
import tempfile
from pathlib import Path
import json
import re


def _aggresive_normalisation(doc: str) -> str:
    doc = re.sub("[^A-Z ]", "x", doc)
    doc = re.sub("[A-Z]", "X", doc)
    return doc


class TestDeduper:
    @pytest.fixture(scope="class")
    def basic_params(self):
        yield dict(random_seed=42, verbose=False)

    @pytest.fixture(scope="class")
    def duplicated_corpus(self):
        yield [
            "hej med dig min ven\n godt at se dig!",
            "hej med dig min ven, godt at se dig!",
            "Hej med dig min ven, godt at se dig!",
            "Hej med dig min ven!",
            "Hej med dig min ven?",
            "hej med dig min ven",
            "dav med dig min ven",
            "farvel du gamle",
        ]

    @pytest.fixture(scope="class")
    def temp_file(self):
        yield tempfile.NamedTemporaryFile()

    @pytest.mark.parametrize(
        "params,deduplicated_corpus",
        [
            (
                dict(),
                [
                    "hej med dig min ven\n godt at se dig!",
                    "hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven!",
                    "hej med dig min ven",
                    "dav med dig min ven",
                    "farvel du gamle",
                ],
            ),
            (
                dict(similarity_threshold=0.1),
                ["hej med dig min ven\n godt at se dig!", "farvel du gamle"],
            ),
            (
                dict(ngram_size=20),
                [
                    "hej med dig min ven\n godt at se dig!",
                    "hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven!",
                    "hej med dig min ven",
                    "dav med dig min ven",
                    "farvel du gamle",
                ],
            ),
            (
                dict(split_method="char_ngram", ngram_size=2),
                [
                    "hej med dig min ven\n godt at se dig!",
                    "Hej med dig min ven!",
                    "dav med dig min ven",
                    "farvel du gamle",
                ],
            ),
            (
                dict(split_method="word_ngram"),
                [
                    "hej med dig min ven\n godt at se dig!",
                    "hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven!",
                    "hej med dig min ven",
                    "dav med dig min ven",
                    "farvel du gamle",
                ],
            ),
            (
                dict(split_method="word_ngram", ngram_size=2),
                [
                    "hej med dig min ven\n godt at se dig!",
                    "Hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven!",
                    "hej med dig min ven",
                    "dav med dig min ven",
                    "farvel du gamle",
                ],
            ),
            (
                dict(split_method="word_ngram", ngram_size=50),
                [
                    "hej med dig min ven\n godt at se dig!",
                    "hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven!",
                    "hej med dig min ven",
                    "dav med dig min ven",
                    "farvel du gamle",
                ],
            ),
            (
                dict(split_method="paragraph"),
                [
                    "hej med dig min ven\n godt at se dig!",
                    "hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven!",
                    "hej med dig min ven",
                    "dav med dig min ven",
                    "farvel du gamle",
                ],
            ),
            (
                dict(split_method="paragraph", similarity_threshold=0.1),
                [
                    "hej med dig min ven\n godt at se dig!",
                    "hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven!",
                    "dav med dig min ven",
                    "farvel du gamle",
                ],
            ),
            (
                dict(split_method="none"),
                [
                    "hej med dig min ven\n godt at se dig!",
                    "hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven!",
                    "hej med dig min ven",
                    "dav med dig min ven",
                    "farvel du gamle",
                ],
            ),
            (
                dict(split_method=None),
                [
                    "hej med dig min ven\n godt at se dig!",
                    "hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven!",
                    "hej med dig min ven",
                    "dav med dig min ven",
                    "farvel du gamle",
                ],
            ),
            (
                dict(normalization_func=lambda x: x),
                [
                    "hej med dig min ven\n godt at se dig!",
                    "hej med dig min ven, godt at se dig!",
                    "Hej med dig min ven!",
                    "Hej med dig min ven?",
                    "hej med dig min ven",
                    "dav med dig min ven",
                    "farvel du gamle",
                ],
            ),
            (
                dict(normalization_func=_aggresive_normalisation),
                [
                    "hej med dig min ven\n godt at se dig!",
                    "Hej med dig min ven!",
                    "hej med dig min ven",
                    "farvel du gamle",
                ],
            ),
        ],
    )
    def test_deduplication(
        self, params, deduplicated_corpus, duplicated_corpus, basic_params, temp_file
    ):
        # Build the Deduper
        deduper = Deduper(**params, **basic_params)

        # Deduplicate the corpus
        deduper.deduplicate(
            duplicated_corpus, output_fname=temp_file.name, overwrite=True
        )

        # Open the deduplicated corpus
        with Path(temp_file.name).open("r") as f:
            deduplicated = [json.loads(line)["text"] for line in f]

        # Check that the deduplicated corpus is the same as the expected corpus
        assert deduplicated_corpus == deduplicated

    @pytest.mark.parametrize(
        "num_minhashes,miss_lower,miss_upper",
        [
            (2, 70, 75),
            (16, 40, 45),
            (32, 20, 25),
            (64, 15, 20),
            (128, 5, 10),
            (256, 0, 5),
        ],
    )
    def test_miss_percentage(
        self,
        basic_params,
        duplicated_corpus,
        temp_file,
        num_minhashes,
        miss_lower,
        miss_upper,
    ):
        # Build the Deduper
        deduper = Deduper(num_minhashes=num_minhashes, **basic_params)

        misses = 0
        for _ in range(100):
            deduper.random_seed += 1

            # Deduplicate the corpus
            deduper.deduplicate(
                duplicated_corpus, output_fname=temp_file.name, overwrite=True
            )

            # Open the deduplicated corpus
            with Path(temp_file.name).open("r") as f:
                deduplicated = [json.loads(line)["text"] for line in f]

            # Check if there were any misses
            if len(deduplicated) != 6:
                misses += 1

        assert miss_lower <= misses
        assert misses <= miss_upper

    @pytest.mark.parametrize(
        "params,correct_shingles",
        [
            (dict(), ["Hej med dig K", "ej med dig Ki", "j med dig Kim"]),
            (
                dict(ngram_size=5),
                [
                    "Hej m",
                    "ej me",
                    "j med",
                    " med ",
                    "med d",
                    "ed di",
                    "d dig",
                    " dig ",
                    "dig K",
                    "ig Ki",
                    "g Kim",
                ],
            ),
            (dict(ngram_stride=2), ["Hej med dig K", "j med dig Kim"]),
            (
                dict(ngram_size=3, split_method="word_ngram"),
                ["Hej med dig", "med dig Kim"],
            ),
        ],
    )
    def test_shingles(self, basic_params, params, correct_shingles):
        deduper = Deduper(**params, **basic_params)
        shingles = deduper._extract_shingles("Hej med dig Kim")
        assert shingles == correct_shingles
