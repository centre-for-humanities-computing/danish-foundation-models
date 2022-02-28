"""
Loading scripts for HF type datasets
"""
import os
import sys

from typing import Set, Union, List

from datasets import (
    load_dataset,
    interleave_datasets,
    Dataset,
    IterableDataset,
    Features,
    Value,
    DatasetDict,
)
from wasabi import msg
from dfm.data.utils import to_datetime

# Removed import below untill fixed.
# from text_dedup import min_hash_deduper, duplicate_filter


def load_tweets(dedupe=False) -> Union[Dataset, IterableDataset]:
    """Dataloader for tweets from the HOPE project.

    Args:
        dedupe (bool, optional): Whether to deplicate tweets or not. Defaults to False.

    Returns:
        Union[Dataset, IterableDataset]: A Hugging Face dataset for HOPE tweets.
    """
    cwd = os.getcwd()
    f_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(f_path, "..", "data")
    sys.path.append(data_path)

    os.chdir(data_path)

    dataset = load_dataset("HopeTweet", streaming=True)
    ds = dataset["train"]

    ds = ds.map(to_datetime)
    if dedupe:
        ds = ds.map(min_hash_deduper, batched=True, batch_size=50_000)
        ds = ds.map(duplicate_filter, batched=True, batch_size=50_000)
    os.chdir(cwd)
    return ds


def load_news() -> Union[Dataset, IterableDataset]:
    """Dataloader for news.

    Returns:
        Union[Dataset, IterableDataset]: A Hugging Face dataset for DaNews.
    """
    cwd = os.getcwd()
    f_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(f_path, "..", "data")
    os.chdir(data_path)
    dataset = load_dataset("DaNews", streaming=True)
    ds = dataset["train"]
    os.chdir(cwd)

    def format_news(example: dict) -> dict:
        example["text"] = ""
        if example["heading"].strip(" "):
            example["text"] = example["heading"]
        if example["subheading"].strip(" "):
            example["text"] += f'\n {example["subheading"]}'
        if example["publishdate"].strip(" "):
            example["text"] += f'\n {example["publishdate"]}'
        if example["publishdate"].strip(" "):
            example["text"] += f'\n\n {example["paragraph"]}'
        if example["body"].strip(" "):
            example["text"] += f'\n\n {example["body"]}'
        return example

    ds = ds.map(format_news)

    return ds


def load_dagw(
    remove_cat: Set[str] = {"danavis", "dannet"}, streaming: bool = False, **kwargs
) -> Union[Dataset, IterableDataset]:
    """Dataloader for Danish Gigaword.

    Args:
        remove_cat (bool, optional): Text categories to remove.
        streaming (bool, optional): Whether to stream the dataset. Defaults to False.

    Returns:
        Union[Dataset, IterableDataset]: A Hugging Face dataset for Danish Gigaword.
    """
    dataset = load_dataset(
        "DDSC/partial-danish-gigaword-no-twitter", streaming=streaming
    )

    def filter_(examples):
        i = 0
        while i < len(examples["source"]):
            s = examples["source"][i]
            if s in remove_cat:
                for k in examples:
                    examples[k].pop(i)
            else:
                i += 1
        return examples

    ds = dataset["train"]

    if remove_cat:
        # not possible to use filter with a streamed dataset
        ds = ds.map(filter_, batched=True, **kwargs)
    return ds


def load_reddit(streaming=False) -> Union[Dataset, IterableDataset]:
    """Dataloader for Danish reddit data.

    Args:
        streaming (bool, optional): Whether to stream the dataset. Defaults to False.

    Returns:
        Union[Dataset, IterableDataset]: A Hugging Face dataset for Danish reddit data.
    """
    dataset = load_dataset("DDSC/reddit-da", streaming=streaming)
    ds = dataset["train"]
    return ds


def load_lexdk(streaming: bool = False) -> Union[Dataset, IterableDataset]:
    """Load the Lex.dk dataset as a Hugging Face Dataset object.

    Args:
        streaming (bool, optional):
            Whether to stream the dataset. Defaults to False.

    Returns:
        Dataset or IterableDataset: The loaded Hugging Face dataset.
    """
    features = Features(
        dict(
            url=Value("string"),
            title=Value("string"),
            clarification=Value("string"),
            authors=[Value("string")],
            date=Value("string"),
            text=Value("string"),
        )
    )
    return load_dataset(
        path="dfm/data/lexdk", features=features, streaming=streaming, split="train"
    )


def load_tokenizer_ds() -> Dataset:
    """
    script used for training the tokenizer. Load a balances set of data to train the tokenizer on.
    """

    def word_count(example):
        example["n_words"] = len(list(filter(lambda x: x, example["text"].split(" "))))
        return example

    import numpy as np

    tweets = load_tweets(dedupe=False)
    avg_words_pr_tweet = np.mean(
        [a["n_words"] for a in list(tweets.map(word_count).take(100_000))]
    )
    tweet_n_words = 300_000_000
    n_tweets = tweet_n_words // avg_words_pr_tweet

    news = load_news()

    avg_words_pr_article = np.mean(
        [a["n_words"] for a in list(news.map(word_count).take(100_000))]
    )
    news_n_words = 300_000_000
    n_news = news_n_words // avg_words_pr_article

    reddit = load_reddit(streaming=False)
    dagw = load_dagw(streaming=False)
    n_reddit = len(reddit)  # 1 908 887
    n_dagw = len(dagw)  # 666 437

    reddit = load_reddit(streaming=True)  # use all tokens ~86M
    dagw = load_dagw(
        streaming=True
    )  # use all tokens (-danavis, -twitter) ~1 000M tokens

    # calculate proportion of each dataset
    arr = np.array([n_tweets, n_news, n_dagw, n_reddit])
    prob = arr / sum(arr)

    ds = interleave_datasets([tweets, news, dagw, reddit], probabilities=prob.tolist())
    n = 10_000_000
    msg.info(f"Limiting dataset to {n} samples.")
    ds = ds.take(n)
    return ds


def load_dfm_dataset(dataset: str, **kwargs) -> Dataset:
    """load a predefined dfm dataset

    Args:
        dataset (str): A predefined dataset

    Returns:
        Dataset: a Huggingface dataset
    """
    dataset_loaders = {
        "tokenization": load_tokenizer_ds,
        "hopetweets": load_tweets,
        "reddit": load_reddit,
        "danews": load_news,
        "dagw": load_dagw,
        "lexdk": load_lexdk,
        # "all": load_concatenated_datasets
    }

    if dataset in dataset_loaders:
        return dataset_loaders[dataset.lower()](**kwargs)
    else:
        raise ValueError(
            f"invalid dataset. Valid datasets include {dataset_loaders.keys()}"
        )


def load_multiple_dfm_datasets(datasets: List[str], **kwargs) -> Dataset:
    """Dataloader for loading multiple Danish Foundation Models datasets.

    Args:
        datasets (List[str]): List of strings containing the names of the datasets

    Returns:
        Dataset: A concatenated Hugging Face dataset containing the given DFM datasets.
    """
    datasets = [load_dfm_dataset(dataset, **kwargs) for dataset in datasets]
    return datasets.concatenate_datasets(datasets)


#### TEMPORARY TO TEST TRAIN SCRIPT
def dfm_load_dataset(dataset: str) -> DatasetDict:
    """loads a single dataset from the Hugging Face Datasets hub.

    Args:
        dataset (str): string for Hugging Face dataset.

    Returns:
        DatasetDict: Dataset with train, test and validation split.
    """

    ds = load_dataset(dataset, streaming=False)

    if "validation" not in ds or "test" not in ds:
        train_test = ds["train"].train_test_split(test_size=0.1)

        # Split the 10% test + valid in half test, half valid
        test_valid = train_test["test"].train_test_split(test_size=0.5)

        # gather everyone if you want to have a single DatasetDict
        ds = DatasetDict(
            {
                "train": train_test["train"],
                "test": test_valid["test"],
                "val": test_valid["train"],
            }
        )

    return ds
