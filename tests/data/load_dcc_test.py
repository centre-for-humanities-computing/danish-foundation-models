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

    dataset = load_dcc(columns_to_keep=["text", "source"])
    assert isinstance(dataset, IterableDatasetDict)
    assert len(dataset) == 3
    assert "train" in dataset
    assert "validation" in dataset
    assert "test" in dataset

    for split in dataset:
        ds_split = dataset[split]
        iter_split = iter(ds_split)
        # check that we can iterate through the dataset
        for _ in range(1000):
            sample = next(iter_split)
            # check that the columns are as expected
            for i in sample:
                assert i in ["text", "source"]
