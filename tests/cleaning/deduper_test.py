from dfm.cleaning import Deduper

import pytest
import tempfile
from pathlib import Path
import json

class TestDeduper:
    def dedup(self, corpus, **kwargs):
        temp = tempfile.NamedTemporaryFile()
        default_args = {
            'random_seed': 42,
            'split_method': "char_ngram",
        }
        args = dict(default_args, **kwargs)
        deduper = Deduper(**args)
        deduper.deduplicate(corpus, output_fname=temp.name, overwrite=True)
        return [json.loads(line)['text'] for line in Path(temp.name).open("r")]

    def test_removes_exact_duplicates(self):
        assert (
            self.dedup([
                "hej med dig min ven",
                "hej med dig min ven",
                "farvel du gamle"
            ]) == ["hej med dig min ven", "farvel du gamle"]
        )

    def test_removes_near_duplicates(self):
        assert (
            self.dedup([
                "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
                "Er kom en soldat marcherende hen ad landevejen:\n én, to! én, to!"
            ]) == ["Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!"]
        )

    def test_document_shorter_than_shingles(self):
        assert (
            self.dedup([
                "Hej med dig",
                "Hej med dig",
                "Gå din vej"
            ], ngram_size=13) == ["Hej med dig", "Gå din vej"]
        )

    def test_split_by_5_char_ngram(self):
        pass

    def test_split_by_13_char_ngram(self):
        pass


    def test_split_by_5_word_ngram(self):
        pass

    def test_split_by_13_word_ngram(self):
        pass

    def test_split_by_paragraph(self):
        assert (
            self.dedup([
                "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
                "Er kom en soldat marcherende hen ad landevejen:\n én, to! én, to!"
            ], split_method='paragraph') == [
                "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
                "Er kom en soldat marcherende hen ad landevejen:\n én, to! én, to!"
            ]
        )

    def test_do_not_split(self):
        assert (
            self.dedup([
                "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
                "Er kom en soldat marcherende hen ad landevejen:\n én, to! én, to!"
            ], split_method='paragraph') == [
                "Der kom en soldat marcherende hen ad landevejen:\n én, to! én, to!",
                "Er kom en soldat marcherende hen ad landevejen:\n én, to! én, to!"
            ]
        )

    def test_split_with_double_stride(self):
        pass

    def test_2_minhashes(self):
        pass

    def test_128_minhashes(self):
        pass

    def test_2048_minhashes(self):
        pass

    def test_seed_stability(self):
        pass

    def test_no_normalization(self):
        pass

    def test_aggresive_normalization(self):
        pass
