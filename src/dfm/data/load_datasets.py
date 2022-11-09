"""
Datasets loaders for DFM datasets.
"""

import os
from functools import partial
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

from datasets import (
    DatasetDict,
    IterableDatasetDict,
    concatenate_datasets,
    interleave_datasets,
    load_dataset,
)


def __add_column(example, value, column: str):
    example[column] = value
    return example


def __select_columns(
    dataset: Union[IterableDatasetDict, DatasetDict], columns: List[str]
) -> Union[IterableDatasetDict, DatasetDict]:
    """Select columns in dataset to keep and removes the rest.

    Args:
        dataset (Union[IterableDatasetDict, DatasetDict]): dataset to filter columns
            from
        columns (List[str]): columns to keep.

    Returns:
        Union[IterableDatasetDict, DatasetDict]: The dataset containing only the
            desired columns.
    """
    # extract a sample from a subset (typically train) to get column names.
    subset = dataset[list(dataset.keys())[0]]
    sample = next(iter(subset))
    col_to_remove = [c_name for c_name in sample.keys() if c_name not in columns]

    return dataset.remove_columns(col_to_remove)


def load_hopetwitter(
    path_to_hopetwitter: Union[str, Path, None] = None,
    columns_to_keep: Optional[List[str]] = None,
    **kwargs,
) -> IterableDatasetDict:
    """
    Loads HopeTwitter.

    Args:
        path_to_hopetwitter (Union[str, Path, None], optional): path to HopeTwitter.
            Defaults to None in which case it uses the environment variable
            HOPETWITTER_PATH to find the dataset.
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to None
            in which case all columns are kept.
        kwargs: arguments to be passed forward to load_dataset

    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    if path_to_hopetwitter is None:
        # check if path is set in environment variable
        path_to_hopetwitter = os.getenv("HOPETWITTER_PATH")
        if path_to_hopetwitter is None:
            raise ValueError(
                "Path to danews dataset not specified. Please set the environment"
                + "variable HOPETWITTER_PATH to the path to the dataset or pass the path to"
                + " the dataset using the path_to_hopetwitter argument."
            )
    path_to_hopetwitter = Path(path_to_hopetwitter)

    test = (
        path_to_hopetwitter
        / "twitter_da_stopwords_2019-01-01_2021-04-30_v1.0.0_test.jsonl"
    )
    val = (
        path_to_hopetwitter
        / "twitter_da_stopwords_2019-01-01_2021-04-30_v1.0.0_val.jsonl"
    )
    train = (
        path_to_hopetwitter
        / "twitter_da_stopwords_2019-01-01_2021-04-30_filtered_v1.0.0_train.jsonl"
    )
    data_files = {
        "train": [str(train)],
        "test": [str(test)],
        "validation": [str(val)],
    }
    hopetwitter = load_dataset("json", data_files=data_files, streaming=True, **kwargs)

    _add_source = partial(__add_column, value="hopetwitter", column="source")
    hopetwitter = hopetwitter.map(_add_source)

    if columns_to_keep:
        hopetwitter = __select_columns(hopetwitter, columns_to_keep)

    return hopetwitter


def load_dagw_dfm(
    path_to_dagw: Union[str, Path, None] = None,
    columns_to_keep: Optional[List[str]] = None,
    **kwargs,
) -> IterableDatasetDict:
    """
    Loads DAGW_{DFM}.

    Args:
        path_to_dagw (Union[str, Path, None], optional): path to DAGW_DFM.
            Defaults to None in which case it uses the environment variable
            DAGW_DFM_PATH to find the dataset.
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to
            None in which case all columns are kept.
        kwargs: arguments to be passed forward to load_dataset

    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    if path_to_dagw is None:
        # check if path is set in environment variable
        path_to_dagw = os.getenv("DAGW_DFM_PATH")
        if path_to_dagw is None:
            raise ValueError(
                "Path to danews dataset not specified. Please set the environment"
                + "variable DAGW_DFM_PATH to the path to the dataset or pass the path to"
                + " the dataset using the path_to_dagw argument."
            )

    path_to_dagw = Path(path_to_dagw)

    test = path_to_dagw / "dagw_reddit_v1.0.0_test.jsonl"
    val = path_to_dagw / "dagw_reddit_v1.0.0_val.jsonl"
    train = path_to_dagw / "dagw_reddit_filtered_v1.0.0_train.jsonl"
    data_files = {
        "train": [str(train)],
        "test": [str(test)],
        "validation": [str(val)],
    }
    dagw = load_dataset("json", data_files=data_files, streaming=True, **kwargs)

    if columns_to_keep:
        dagw = __select_columns(dagw, columns_to_keep)

    return dagw


def load_danews(
    path_to_danews: Union[str, Path, None] = None,
    columns_to_keep: Optional[List[str]] = None,
    **kwargs,
) -> IterableDatasetDict:
    """
    Loads DaNews.

    Args:
        path_to_danews (Union[str, Path, None], optional): path to DaNews dataset.
            Defaults to None, in which case it uses the environment variable
            DANEWS_PATH.
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to
            None in which case all columns are kept.
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to
            None in which case all columns are kept.
        kwargs: arguments to be passed forward to load_dataset

    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    if path_to_danews is None:
        # check if path is set in environment variable
        path_to_danews = os.getenv("DANEWS_PATH")
        if path_to_danews is None:
            raise ValueError(
                "Path to danews dataset not specified. Please set the environment"
                + "variable DANEWS_PATH to the path to the dataset or pass the path to"
                + " the dataset using the path_to_danews argument."
            )
    path_to_danews = Path(path_to_danews)

    test = path_to_danews / "infomedia_2000-2021_v1.0.0_test.jsonl"
    val = path_to_danews / "infomedia_2000-2021_v1.0.0_val.jsonl"
    train = path_to_danews / "infomedia_2000-2021_filtered_v1.0.0_train.jsonl"
    data_files = {
        "train": [str(train)],
        "test": [str(test)],
        "validation": [str(val)],
    }
    danews = load_dataset("json", data_files=data_files, streaming=True, **kwargs)

    _add_source = partial(__add_column, value="danews", column="source")
    danews = danews.map(_add_source)

    if columns_to_keep:
        danews = __select_columns(danews, columns_to_keep)
    return danews


def load_nat(
    version: str = "2.0.0",
    path_to_nat: Union[str, Path, None] = None,
    years: Iterable[int] = range(2006, 2017),
    probabilities: Optional[List[float]] = None,
    columns_to_keep: Optional[List[str]] = None,
    seed: Optional[int] = None,
    **kwargs,
) -> IterableDatasetDict:
    """
    Loads NetArkivet Text corpus (NAT).

    Args:
        version (str, optional): Version of NAT to load. Defaults to "2.0.0".
        path_to_nat (Union[str, Path], optional): path to NAT dataset.
            Defaults to None, in which case the dataset it uses the environment
            variable NAT_PATH.
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to
            None in which case all columns are kept.
        years (Iterable[int]): A list of years to include.
        probabilities (Optional[List[float]], optional): Interleave probabilites of
            years, i.e. the probability of sampling a from given year for each sample.
            Default to None, denoting equal probabilites.
        seed (Optional[int], optional): Seed used when interleaving datasets. Defaults
            to None.
        kwargs: arguments to be passed forward to load_dataset

    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    if path_to_nat is None:
        # check if path is set in environment variable
        path_to_nat = os.getenv("NAT_PATH")
        if path_to_nat is None:
            raise ValueError(
                "Path to NAT dataset not specified. Please set the environment variable"
                + "NAT_PATH to the path to the dataset or pass the path to the dataset"
                + "using the path_to_nat argument."
            )

    path_to_nat = Path(path_to_nat)

    valid_version = ["1.0.0", "2.0.0"]
    if version not in valid_version:
        raise ValueError(f"Version must be one of {valid_version}, got {version}.")

    datasets = []
    for year in years:
        if version == "1.0.0":
            train_path = path_to_nat / f"{year}_deduplicated_filtered.jsonl"
        else:
            train_path = path_to_nat / f"nat_{year}_v{version}.jsonl"
        dataset_ = load_dataset(
            "json",
            data_files={"train": [str(train_path)]},
            streaming=True,
            split="train",
            **kwargs,
        )
        if version != "1.0.0":
            # rename column content to text
            dataset_ = dataset_.rename_column("content", "text")
        _add_year = partial(__add_column, value=year, column="year")
        dataset_ = dataset_.map(_add_year)
        datasets.append(dataset_)

    nat = interleave_datasets(
        datasets=datasets,
        probabilities=probabilities,
        seed=seed,
        stopping_strategy="all_exhausted",
    )
    nat = IterableDatasetDict({"train": nat})

    _add_source = partial(__add_column, value="nat", column="source")
    nat = nat.map(_add_source)

    if columns_to_keep:
        nat = __select_columns(nat, columns_to_keep)
    return nat


def load_dcc(
    version: str = "1.1.0",
    probabilities: Dict[str, float] = {
        "danews": 0.06,
        "dagw_dfm": 0.06,
        "hopetwitter": 0.03,
        "nat": 0.85,
    },
    path_to_hopetwitter: Union[str, Path, None] = None,
    path_to_dagw: Union[str, Path, None] = None,
    path_to_danews: Union[str, Path, None] = None,
    path_to_nat: Union[str, Path, None] = None,
    columns_to_keep: List[str] = ["text", "source"],
    stopping_strategy: str = "all_exhausted",
    **kwargs,
):
    """
    Loads Danish collosal corpus (DCC).

    Args:
        version (str, optional): Version of DCC to load. Defaults to "1.1.0".
        probabilities (Optional[Dict[str, float], optional): Interleave probabilites of
            the subdatasets. Defualts to {"danews": 0.06, "dagw_dfm": 0.06,
            "hopetwitter": 0.03, "nat": 0.85}.
        path_to_hopetwitter (Union[str, Path, None], optional): path to Hopetwitter.
            Defalt to None in which case it uses the environment variable which can be
            set using `export HOPETWITTER_PATH=/path/to/hopetwitter`.
        path_to_dagw (Union[str, Path, None], optional): path to DAGW_DFM.
            Defalt to None in which case it uses the environment variable which can be
            set using `export DAGW_DFM_PATH=/path/to/dagw_dfm`.
        path_to_danews (Union[str, Path, None], optional): path to DaNews.
            Defalt to None in which case it uses the environment variable which can be
            set using `export DANEWS_PATH=/path/to/danews`.
        path_to_nat (Union[str, Path, None], optional): path to NAT dataset.
            Defalt to None in which case it uses the environment variable which can be
            set using `export NAT_PATH=/path/to/nat`.
        columns_to_keep (List[str], optional): Columns to keep across the datasets.
        stopping_strategy (str, optional): Stopping strategy. Defaults to
            "all_exhausted".
        kwargs: arguments to be passed forward to load_dataset

    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    versions_options = ["1.0.0", "1.1.0"]
    if version not in versions_options:
        raise ValueError(f"Version must be one of {versions_options}, got {version}.")
    datasets = {}

    datasets["danews"] = load_danews(
        columns_to_keep=columns_to_keep,
        path_to_danews=path_to_danews,
        **kwargs,
    )
    datasets["dagw_dfm"] = load_dagw_dfm(
        columns_to_keep=columns_to_keep,
        path_to_dagw=path_to_dagw,
        **kwargs,
    )
    datasets["hopetwitter"] = load_hopetwitter(
        columns_to_keep=columns_to_keep,
        path_to_hopetwitter=path_to_hopetwitter,
        **kwargs,
    )

    if version == "1.1.0":
        nat_version = "2.0.0"
    else:
        nat_version = "1.0.0"

    datasets["nat"] = load_nat(
        version=nat_version,
        columns_to_keep=columns_to_keep,
        path_to_nat=path_to_nat,
        **kwargs,
    )
    dataset_names = ["danews", "dagw_dfm", "hopetwitter", "nat"]

    _probabilities = [probabilities[k] for k in dataset_names]
    train_datasets = [datasets[k]["train"] for k in dataset_names]

    train = interleave_datasets(
        train_datasets,
        probabilities=_probabilities,
        stopping_strategy=stopping_strategy,
        **kwargs,
    )
    # Note: NAT does not include a test, val set
    eval_names = ["danews", "dagw_dfm", "hopetwitter"]
    val = concatenate_datasets([datasets[k]["validation"] for k in eval_names])
    test = concatenate_datasets([datasets[k]["test"] for k in eval_names])
    return IterableDatasetDict({"train": train, "validation": val, "test": test})
