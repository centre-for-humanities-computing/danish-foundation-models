
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

HOPETWITTER_PATH = Path("/work") / "twitter_cleaned"
DAGW_DFM_PATH = Path("/work") / "dagw-clean"
DANEWS_PATH = Path("/work") / "hope-infomedia_cleaned"
NAT_PATH = Path("/work") / "netarkivet-cleaned"


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
    path_to_hopetwitter = Path(path_to_hopetwitter)

    test = path_to_hopetwitter / "twitter_da_stopwords_2019-01-01_2021-04-30_v1.0.0_test.jsonl"
    val = path_to_hopetwitter / "twitter_da_stopwords_2019-01-01_2021-04-30_v1.0.0_val.jsonl"
    train = path_to_hopetwitter / "twitter_da_stopwords_2019-01-01_2021-04-30_filtered_v1.0.0_train.jsonl"
    hopetwitter = load_dataset("json", data_files={"train": [str(train)], "test": [str(test)], "validation": [str(val)]}, streaming=True)
    return hopetwitter


    HOPETWITTER_PATH = Path("/work") / "twitter_cleaned"


def load_dagw_dfm(path_to_dagw: Union[str, Path]=HOPETWITTER_PATH, **kwargs) -> IterableDatasetDict:
    """
    Loads DAGW_{DFM}.

    Args:
        path_to_dagw (Union[str, Path]): path to the DAGW_DFM.
            Defaults to /work/dagw-clean.
        kwargs: arguments to be passed forward to load_dataset
    
    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    path_to_dagw = Path(path_to_dagw)

    test = path_to_dagw / "dagw_reddit_v1.0.0_test.jsonl"
    val = path_to_dagw / "dagw_reddit_v1.0.0_val.jsonl"
    train = path_to_dagw / "dagw_reddit_filtered_v1.0.0_train.jsonl"
    dagw = load_dataset("json", data_files={"train": [str(train)], "test": [str(test)], "validation": [str(val)]}, streaming=True)
    return dagw



def load_danews(path_to_danews: Union[str, Path]=DANEWS_PATH, **kwargs) -> IterableDatasetDict:
    """
    Loads DaNews.

    Args:
        path_to_danews (Union[str, Path]): path to the DaNews dataset.
            Defaults to /work/hope-infomedia_cleaned
        kwargs: arguments to be passed forward to load_dataset
    
    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    path_to_danews = Path(path_to_danews)

    test = path_to_danews / ""
    val = path_to_danews / ""
    train = path_to_danews / ""
    danews = load_dataset("json", data_files={"train": [str(train)], "test": [str(test)], "validation": [str(val)]}, streaming=True)
    return danews


def load_nat(path_to_nat: Union[str, Path]=NAT_PATH, years: Iterable[int]=range(2006, 2017), **kwargs) -> IterableDatasetDict:
    """
    Loads DaNews.

    Args:
        path_to_nat (Union[str, Path]): path to the NAT dataset.
            Defaults to /work/netarkivet-cleaned.
        years (Iterable[int]): A list of years to include.
        kwargs: arguments to be passed forward to load_dataset
    
    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    NAT_PATH = Path(NAT_PATH)

    train_paths = []
    for year in years:
        train_path = NAT_PATH / f"{year}_deduplicated_filtered.jsonl"
        train_paths.append(str(train_path))
    nat = load_dataset("json", data_files={"train": train_paths}, streaming=True)
    return nat

