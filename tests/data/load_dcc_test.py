"""
Test that datasets load locally as intended.
"""

import pytest
from datasets import IterableDatasetDict

from dfm.data import load_dcc


@pytest.mark.skip(reason="This test is intended for local use only.")
def test_load_dcc():
    """Test that datasets load locally as intended."""

    import os

    # set environment variables (pytest doesn't
    os.environ[
        "NAT_PATH"
    ] = "/data-big-projects/danish-foundation-models/netarkivet_cleaned/"
    os.environ[
        "DAGW_DFM_PATH"
    ] = "/data-big-projects/danish-foundation-models/dagw_cleaned/"
    os.environ[
        "DANEWS_PATH"
    ] = "/data-big-projects/danish-foundation-models/hope-infomedia_cleaned/"
    os.environ[
        "HOPETWITTER_PATH"
    ] = "/data-big-projects/danish-foundation-models/twitter_cleaned/"

    dataset = load_dcc()
    assert isinstance(dataset, IterableDatasetDict)
    assert len(dataset) == 3
    assert "train" in dataset
    assert "validation" in dataset
    assert "test" in dataset

    train = dataset["train"]
    iter_train = iter(train)
    for i in range(100):
        next(iter_train)  # check that we can iterate through the dataset
