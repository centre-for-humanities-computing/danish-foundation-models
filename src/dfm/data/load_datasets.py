
from typing import Union, Iterable, List, Optional
import os
from pathlib import Path
from functools import partial

from datasets import (
    load_dataset,
    interleave_datasets,
    DatasetDict,
    IterableDatasetDict,
    load_from_disk,
    interleave_datasets,
    concatenate_datasets
)

HOPETWITTER_PATH = Path("/work") / "twitter_cleaned"
DAGW_DFM_PATH = Path("/work") / "dagw-clean"
DANEWS_PATH = Path("/work") / "hope-infomedia_cleaned"
NAT_PATH = Path("/work") / "netarkivet-cleaned"



def __add_source(example, source):
    example["source"] = source
    return example

def keep_columns(
    dataset: Union[IterableDatasetDict, DatasetDict], 
    columns_to_keep: List[str]
) -> Union[IterableDatasetDict, DatasetDict]:
    subset = dataset[list(dataset.keys())[0]]
    sample = next(iter(subset))
    col_to_remove = [c_name for c_name in sample.keys() if c_name not in columns_to_keep]
    
    return dataset.remove_columns(col_to_remove)



def load_hopetwitter(
        path_to_hopetwitter: Union[str, Path]=HOPETWITTER_PATH, 
        columns_to_keep: Optional[List[str]]=None, 
        **kwargs
    ) -> IterableDatasetDict:
    """
    Loads HopeTwitter.

    Args:
        path_to_hopetwitter (Union[str, Path, None], optional): path to the HopeTwitter.
            Defaults to "/work/twitter_cleaned".
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to None
            in which case all columns are kept.
        kwargs: arguments to be passed forward to load_dataset
    
    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    path_to_hopetwitter = Path(path_to_hopetwitter)

    test = path_to_hopetwitter / "twitter_da_stopwords_2019-01-01_2021-04-30_v1.0.0_test.jsonl"
    val = path_to_hopetwitter / "twitter_da_stopwords_2019-01-01_2021-04-30_v1.0.0_val.jsonl"
    train = path_to_hopetwitter / "twitter_da_stopwords_2019-01-01_2021-04-30_filtered_v1.0.0_train.jsonl"
    data_files = {"train": [str(train)], "test": [str(test)], "validation": [str(val)]}
    hopetwitter = load_dataset("json", data_files=data_files, streaming=True)

    _add_source = partial(__add_source, source = "hopetwitter")
    hopetwitter = hopetwitter.map(_add_source)

    if columns_to_keep:
        hopetwitter = keep_columns(hopetwitter, columns_to_keep)

    return hopetwitter


def load_dagw_dfm(
        path_to_dagw: Union[str, Path]=DAGW_DFM_PATH,
        columns_to_keep: Optional[List[str]]=None,
        **kwargs
    ) -> IterableDatasetDict:
    """
    Loads DAGW_{DFM}.

    Args:
        path_to_dagw (Union[str, Path], optional): path to the DAGW_DFM.
            Defaults to /work/dagw-clean.
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to None
            in which case all columns are kept.
        kwargs: arguments to be passed forward to load_dataset
    
    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    path_to_dagw = Path(path_to_dagw)

    test = path_to_dagw / "dagw_reddit_v1.0.0_test.jsonl"
    val = path_to_dagw / "dagw_reddit_v1.0.0_val.jsonl"
    train = path_to_dagw / "dagw_reddit_filtered_v1.0.0_train.jsonl"
    data_files = {"train": [str(train)], "test": [str(test)], "validation": [str(val)]}
    dagw = load_dataset("json", data_files=data_files, streaming=True)
    
    next(iter(dagw["train"]))
    
    if columns_to_keep:
        dagw = keep_columns(dagw, columns_to_keep)

    return dagw


def load_danews(
        path_to_danews: Union[str, Path]=DANEWS_PATH,
        columns_to_keep: Optional[List[str]]=None,
        **kwargs
    ) -> IterableDatasetDict:
    """
    Loads DaNews.

    Args:
        path_to_danews (Union[str, Path], optional): path to the DaNews dataset.
            Defaults to /work/hope-infomedia_cleaned
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to None
            in which case all columns are kept.
        kwargs: arguments to be passed forward to load_dataset
    
    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    path_to_danews = Path(path_to_danews)

    test = path_to_danews / "infomedia_2000-2021_v1.0.0_test.jsonl"
    val = path_to_danews / "infomedia_2000-2021_v1.0.0_val.jsonl"
    train = path_to_danews / "infomedia_2000-2021_filtered_v1.0.0_train.jsonl"
    data_files = {"train": [str(train)], "test": [str(test)], "validation": [str(val)]}
    danews = load_dataset("json", data_files=data_files, streaming=True)
    
    _add_source = partial(__add_source, source = "danews")
    danews = danews.map(_add_source)

    if columns_to_keep:
        danews = keep_columns(danews, columns_to_keep)
    return danews


def load_nat(
        path_to_nat: Union[str, Path]=NAT_PATH, 
        years: Iterable[int]=range(2006, 2017), 
        probabilities: Optional[List[float]] = None, 
        seed: Optional[int] = None,
        columns_to_keep: Optional[List[str]]=None, 
        **kwargs
    ) -> IterableDatasetDict:
    """
    Loads NetArkivet Text corpus (NAT).

    Args:
        path_to_nat (Union[str, Path], optional): path to the NAT dataset.
            Defaults to /work/netarkivet-cleaned.
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to None
            in which case all columns are kept.
        years (Iterable[int]): A list of years to include.
        probabilities (Optional[List[float]], optionak): Interleave probabilites of years.
            Default to None, denoting equal probabilites.
        kwargs: arguments to be passed forward to load_dataset
    
    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    path_to_nat = Path(path_to_nat)

    train_paths = []
    for year in years:
        train_path = path_to_nat / f"{year}_deduplicated_filtered.jsonl"
        train_paths.append(str(train_path))
    datasets = [load_dataset("json", data_files={"train": path}, streaming=True, split="train", **kwargs) 
                for path in train_paths]
    nat = interleave_datasets(datasets=datasets, probabilities=probabilities, seed=seed)
    nat = IterableDatasetDict({"train": nat})
    
    _add_source = partial(__add_source, source = "nat")
    nat = nat.map(_add_source)

    if columns_to_keep:
        nat = keep_columns(nat, columns_to_keep)
    return nat

def load_dcc_v1(
    probabilities=[0.10, 0.20, 0.20, 0.50],
    path_to_hopetwitter: Union[str, Path]=HOPETWITTER_PATH,
    path_to_dagw: Union[str, Path]=DAGW_DFM_PATH,
    path_to_danews: Union[str, Path]=DANEWS_PATH,
    path_to_nat: Union[str, Path]=NAT_PATH
):
    columns_to_keep = ["text", "source"]
    danews = load_danews(columns_to_keep=columns_to_keep, path_to_danews=path_to_danews)
    dagw_dfm = load_dagw_dfm(columns_to_keep=columns_to_keep, path_to_dagw=path_to_dagw)
    hopetwitter = load_hopetwitter(columns_to_keep = columns_to_keep, path_to_hopetwitter=path_to_hopetwitter)
    nat = load_nat(columns_to_keep=columns_to_keep, path_to_nat=path_to_nat)
    train = interleave_datasets([danews["train"], dagw_dfm["train"], hopetwitter["train"], nat["train"]], probabilities=probabilities)
    # Note: NAT does not include a test, val set
    # val = concatenate_datasets([danews["validation"], dagw_dfm["validation"], hopetwitter["validation"]])
    # test = concatenate_datasets([danews["test"], dagw_dfm["test"], hopetwitter["test"]])

    # as concatenate_datasets is not yet implemented for IterableDatasets:
    dagw_test = Path(path_to_dagw) / "dagw_reddit_v1.0.0_test.jsonl"
    dagw_val = Path(path_to_dagw) / "dagw_reddit_v1.0.0_val.jsonl"
    danews_test = Path(path_to_danews) / "infomedia_2000-2021_v1.0.0_test.jsonl"
    danews_val = Path(path_to_danews) / "infomedia_2000-2021_v1.0.0_val.jsonl"
    twitter_test = Path(path_to_hopetwitter) / "twitter_da_stopwords_2019-01-01_2021-04-30_v1.0.0_test.jsonl"
    twitter_val = Path(path_to_hopetwitter) / "twitter_da_stopwords_2019-01-01_2021-04-30_v1.0.0_val.jsonl"
    data_files = {"test": [str(dagw_test), str(danews_test), str(twitter_test)], 
                  "validation": [str(dagw_val), str(danews_val), str(twitter_val)]
    }
    dcc_test_val = load_dataset("json", data_files =data_files, streaming=True)
    return IterableDatasetDict({"train": train, "validation": dcc_test_val["validation"], "test": dcc_test_val["test"]})
