'''Tests for the dataset loading scripts'''

import pytest
from dfm.data.load import load_tweets, load_news, load_dagw, load_reddit, load_tokenizer_ds
from datasets import IterableDataset, Dataset

@pytest.mark.skip(reason="Dataset not publicly available")
def test_load_tweets():
    ds = load_tweets()
    assert isinstance(ds, IterableDataset)
    tweet = list(ds.take(2))
    assert isinstance(tweet, list)
    assert isinstance(tweet[0], dict)
    assert "text" in tweet[0]

@pytest.mark.skip(reason="Dataset not publicly available")
def test_load_news():
    ds = load_news()
    assert isinstance(ds, IterableDataset)
    samples = list(ds.take(2))
    assert isinstance(samples, list)
    assert isinstance(samples[0], dict)
    assert "text" in samples[0]


def test_load_dagw():
    ds = load_dagw(streaming=True)
    assert isinstance(ds, IterableDataset)
    ds = load_dagw(streaming=False, filter_danavis=True)
    assert isinstance(ds, Dataset)
    assert isinstance(ds[0], dict)
    assert "text" in ds[0]
    assert "danavis" not in set(ds["source"])


def test_load_reddit():
    ds = load_reddit(streaming=True)
    assert isinstance(ds, IterableDataset)
    ds = load_reddit(streaming=False)
    assert isinstance(ds, Dataset)
    assert isinstance(ds[0], dict)
    assert "text" in ds[0]

@pytest.mark.skip(reason="Some of the dataset not publicly available")
def test_load_tokenizer_ds():
    ds = load_tokenizer_ds()
    samples = list(ds.take(10))
    assert isinstance(ds, IterableDataset)
    assert isinstance(samples, list)
    assert isinstance(samples[0], dict)