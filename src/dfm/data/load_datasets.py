"""
Datasets loaders for DFM datasets.
"""

from typing import Dict, Union, Iterable, List, Optional
from pathlib import Path
from functools import partial

from datasets import load_dataset, interleave_datasets, DatasetDict, IterableDatasetDict

HOPETWITTER_PATH = Path("/work") / "twitter_cleaned"
DAGW_DFM_PATH = Path("/work") / "dagw-clean"
DANEWS_PATH = Path("/work") / "hope-infomedia_cleaned"
NAT_PATH = Path("/work") / "netarkivet-cleaned"


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
    path_to_hopetwitter: Union[str, Path] = HOPETWITTER_PATH,
    columns_to_keep: Optional[List[str]] = None,
    n_training_repeats: int = 1,
    **kwargs,
) -> IterableDatasetDict:
    """
    Loads HopeTwitter.

    Args:
        path_to_hopetwitter (Union[str, Path, None], optional): path to HopeTwitter.
            Defaults to "/work/twitter_cleaned".
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to None
            in which case all columns are kept.
        n_training_repeats (int, optional): Number of times to repeat the dataset.
            Defaults to 1, indicating that the dataset is not repeated.
        kwargs: arguments to be passed forward to load_dataset

    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
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
        "train": [str(train)] * n_training_repeats,
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
    path_to_dagw: Union[str, Path] = DAGW_DFM_PATH,
    columns_to_keep: Optional[List[str]] = None,
    n_training_repeats: int = 1,
    **kwargs,
) -> IterableDatasetDict:
    """
    Loads DAGW_{DFM}.

    Args:
        path_to_dagw (Union[str, Path], optional): path to DAGW_DFM.
            Defaults to /work/dagw-clean.
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to
            None in which case all columns are kept.
        n_training_repeats (int, optional): Number of times to repeat the dataset.
            Defaults to 1, indicating that the dataset is not repeated.
        kwargs: arguments to be passed forward to load_dataset

    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    path_to_dagw = Path(path_to_dagw)

    test = path_to_dagw / "dagw_reddit_v1.0.0_test.jsonl"
    val = path_to_dagw / "dagw_reddit_v1.0.0_val.jsonl"
    train = path_to_dagw / "dagw_reddit_filtered_v1.0.0_train.jsonl"
    data_files = {
        "train": [str(train)] * n_training_repeats,
        "test": [str(test)],
        "validation": [str(val)],
    }
    dagw = load_dataset("json", data_files=data_files, streaming=True, **kwargs)

    if columns_to_keep:
        dagw = __select_columns(dagw, columns_to_keep)

    return dagw


def load_danews(
    path_to_danews: Union[str, Path] = DANEWS_PATH,
    columns_to_keep: Optional[List[str]] = None,
    n_training_repeats: int = 1,
    **kwargs,
) -> IterableDatasetDict:
    """
    Loads DaNews.

    Args:
        path_to_danews (Union[str, Path], optional): path to DaNews dataset.
            Defaults to /work/hope-infomedia_cleaned
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to
            None in which case all columns are kept.
        n_training_repeats (int, optional): Number of times to repeat the dataset.
            Defaults to 1, indicating that the dataset is not repeated.
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to
            None in which case all columns are kept.
        kwargs: arguments to be passed forward to load_dataset

    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    path_to_danews = Path(path_to_danews)

    test = path_to_danews / "infomedia_2000-2021_v1.0.0_test.jsonl"
    val = path_to_danews / "infomedia_2000-2021_v1.0.0_val.jsonl"
    train = path_to_danews / "infomedia_2000-2021_filtered_v1.0.0_train.jsonl"
    data_files = {
        "train": [str(train)] * n_training_repeats,
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
    path_to_nat: Union[str, Path] = NAT_PATH,
    years: Iterable[int] = range(2006, 2017),
    probabilities: Optional[List[float]] = None,
    columns_to_keep: Optional[List[str]] = None,
    n_training_repeats: int = 10,
    seed: Optional[int] = None,
    **kwargs,
) -> IterableDatasetDict:
    """
    Loads NetArkivet Text corpus (NAT).

    Args:
        path_to_nat (Union[str, Path], optional): path to NAT dataset.
            Defaults to /work/netarkivet-cleaned.
        columns_to_keep (Optional[List[str]], optional): Columns to keep. Default to
            None in which case all columns are kept.
        years (Iterable[int]): A list of years to include.
        probabilities (Optional[List[float]], optional): Interleave probabilites of
            years, i.e. the probability of sampling a from given year for each sample.
            Default to None, denoting equal probabilites.
        n_training_repeats (int, optional): Number of times to repeat the dataset.
            Defaults to 10, indicating that each year is repeated 10 times is not
            repeated.
        seed (Optional[int], optional): Seed used when interleaving datasets. Defaults
            to None.
        kwargs: arguments to be passed forward to load_dataset

    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    path_to_nat = Path(path_to_nat)

    datasets = []
    for year in years:
        train_path = path_to_nat / f"{year}_deduplicated_filtered.jsonl"
        dataset_ = load_dataset(
            "json",
            data_files={"train": [train_path] * n_training_repeats},
            streaming=True,
            split="train",
            **kwargs,
        )
        _add_year = partial(__add_column, value=year, column="year")
        dataset_ = dataset_.map(_add_year)
        datasets.append(dataset_)

    nat = interleave_datasets(datasets=datasets, probabilities=probabilities, seed=seed)
    nat = IterableDatasetDict({"train": nat})

    _add_source = partial(__add_column, value="nat", column="source")
    nat = nat.map(_add_source)

    if columns_to_keep:
        nat = __select_columns(nat, columns_to_keep)
    return nat


def load_dcc(
    version: str = "1.0.0",
    probabilities: Dict[str, float] = {
        "danews": 0.06,
        "dagw_dfm": 0.06,
        "hopetwitter": 0.03,
        "nat": 0.85,
    },
    n_training_repeats: Dict[str, int] = {
        "danews": 1_000,
        "dagw_dfm": 1_000,
        "hopetwitter": 1_000,
        "nat": 100,
    },
    path_to_hopetwitter: Union[str, Path] = HOPETWITTER_PATH,
    path_to_dagw: Union[str, Path] = DAGW_DFM_PATH,
    path_to_danews: Union[str, Path] = DANEWS_PATH,
    path_to_nat: Union[str, Path] = NAT_PATH,
    columns_to_keep: List(str) = ["text", "source"],
    **kwargs,
):
    """
    Loads Danish collosal corpus (DCC) version 1.

    Args:
        probabilities (Optional[Dict[str, float], optional): Interleave probabilites of the
            subdatasets. Defualts to {"danews": 0.06, "dagw_dfm": 0.06, "hopetwitter":
            0.03, "nat": 0.85}.
        n_training_repeats (Dict[str, int], optional): Number of times to repeat the
            training dataset of each dataset.
        path_to_hopetwitter (Union[str, Path], optional): path to Hopetwitter.
            Defaults to /work/twitter_cleaned.
        path_to_dagw (Union[str, Path], optional): path to DAGW_DFM.
            Defaults to /work/dagw-clean.
        path_to_danews (Union[str, Path], optional): path to DaNews.
            Defaults to /work/hope-infomedia_cleaned.
        path_to_nat (Union[str, Path], optional): path to NAT dataset.
            Defaults to /work/netarkivet-cleaned.
        columns_to_keep (List[str], optional): Columns to keep across the datasets.
        kwargs: arguments to be passed forward to load_dataset

    Returns:
        IterableDatasetDict: A datasets IterableDatasetDict
    """
    versions_options = ["1.0.0"]
    if version != "1.0.0":
        raise ValueError(
            "Version {version} is not available. Available versions"
            + f": {versions_options}"
        )

    danews = load_danews(
        columns_to_keep=columns_to_keep,
        path_to_danews=path_to_danews,
        n_training_repeats=n_training_repeats["danews"],
        **kwargs,
    )
    dagw_dfm = load_dagw_dfm(
        columns_to_keep=columns_to_keep,
        path_to_dagw=path_to_dagw,
        n_training_repeats=n_training_repeats["dagw_dfm"],
        **kwargs,
    )
    hopetwitter = load_hopetwitter(
        columns_to_keep=columns_to_keep,
        path_to_hopetwitter=path_to_hopetwitter,
        n_training_repeats=n_training_repeats["hopetwitter"],
        **kwargs,
    )
    nat = load_nat(
        columns_to_keep=columns_to_keep,
        path_to_nat=path_to_nat,
        n_training_repeats=n_training_repeats["nat"],
        **kwargs,
    )
    probabilities = [
        probabilities[k] for k in ["danews", "dagw_dfm", "hopetwitter", "dfm"]
    ]
    train = interleave_datasets(
        [danews["train"], dagw_dfm["train"], hopetwitter["train"], nat["train"]],
        probabilities=probabilities,
        **kwargs,
    )
    # Note: NAT does not include a test, val set
    # val = concatenate_datasets([danews["validation"], dagw_dfm["validation"], hopetwitter["validation"]])
    # test = concatenate_datasets([danews["test"], dagw_dfm["test"], hopetwitter["test"]])

    # as concatenate_datasets is not yet implemented for IterableDatasets:
    dagw_test = Path(path_to_dagw) / "dagw_reddit_v1.0.0_test.jsonl"
    dagw_val = Path(path_to_dagw) / "dagw_reddit_v1.0.0_val.jsonl"
    danews_test = Path(path_to_danews) / "infomedia_2000-2021_v1.0.0_test.jsonl"
    danews_val = Path(path_to_danews) / "infomedia_2000-2021_v1.0.0_val.jsonl"
    twitter_test = (
        Path(path_to_hopetwitter)
        / "twitter_da_stopwords_2019-01-01_2021-04-30_v1.0.0_test.jsonl"
    )
    twitter_val = (
        Path(path_to_hopetwitter)
        / "twitter_da_stopwords_2019-01-01_2021-04-30_v1.0.0_val.jsonl"
    )
    data_files = {
        "test": [str(dagw_test), str(danews_test), str(twitter_test)],
        "validation": [str(dagw_val), str(danews_val), str(twitter_val)],
    }
    dcc_test_val = load_dataset("json", data_files=data_files, streaming=True)
    return IterableDatasetDict(
        {
            "train": train,
            "validation": dcc_test_val["validation"],
            "test": dcc_test_val["test"],
        }
    )
