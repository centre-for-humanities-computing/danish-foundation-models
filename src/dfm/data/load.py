"""Dataset loading script for Danish Foundation Models
"""
from typing import List
from datasets import load_dataset


def load_dataset(datasets: List[str]):
    # parse dataset names
    # load required dataset
    # interleave if necessary
    # apply relevant filters
    # train test, validation split
    # (dont to shuffling, tokenization etc. here)

    # dummy dataset for testing
    ds = load_dataset("DDSC/reddit-da")
    ds.shuffle(seed=42)
    ds_dict = ds.train_test_split(test_size=0.1)
