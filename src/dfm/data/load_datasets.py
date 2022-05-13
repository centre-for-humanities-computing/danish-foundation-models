
from typing import Union
import os
from pathlib import Path

from datasets import (
    load_dataset,
    interleave_datasets,
    DatasetDict,
    IterableDatasetDict,
    load_from_disk
)

HOPETWITTER_PATH = Path("/work") / "twitter_cleaned" /"twitter_da_stopwords_2019-01-01_2021-04-30_filtered_v1.0.0.jsonl"

def load_hopetwitter(path_to_hopetwitter: Union[str, Path]=HOPETWITTER_PATH, **kwargs) -> IterableDatasetDict:
    """
    Loads HopeTwitter.

    Args:
        path_to_hopetwitter (Union[str, Path, None]): path to the HopeTwitter.
            Defaults to "/work/twitter_cleaned".
        kwargs: arguments to be passed forward to load_dataset
    
    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    # TODO fix path add kwargs
    hopetwitter = load_dataset("json", data_files=str(HOPETWITTER_PATH), streaming=True, split="train")
    t = hopetwitter.take(20_000)
    s = next(iter(t))
    IterableDatasetDict()


    