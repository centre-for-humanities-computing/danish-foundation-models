"""
Loading scripts for HF type datasets
"""
import os
import sys

from typing import Optional
from datasets import load_dataset, interleave_datasets, Dataset


def load_tweets(dedupe=False):
    cwd = os.getcwd()
    f_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(f_path, "..", "data")
    sys.path.append(data_path)
    from dedupe import min_hash_deduper, duplicate_filter
    from utils import to_datetime

    os.chdir(data_path)

    dataset = load_dataset("HopeTweet", streaming=True)
    ds = dataset["train"]

    ds = ds.map(to_datetime)
    if dedupe:
        ds = ds.map(min_hash_deduper, batched=True, batch_size=50_000)
        ds = ds.map(duplicate_filter, batched=True, batch_size=50_000)
    os.chdir(cwd)
    return ds


def load_news():
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


def load_dagw(filter_danavis: bool = True, streaming: bool = False):
    dataset = load_dataset(
        "DDSC/partial-danish-gigaword-no-twitter", streaming=streaming
    )
    ds = dataset["train"]
    if filter_danavis:
        def filter_(examples):
            i = 0
            while i < len(examples["source"]):
                s = examples["source"][i]
                if s == "danavis":
                    for k in examples:
                        examples[k].pop(i)
                else:
                    i += 1
            return examples

        # not possible to use filter with a streamed dataset
        ds = ds.map(
            filter_,
            batched=True,
        )
    return ds


def load_reddit(streaming=False):
    dataset = load_dataset("DDSC/reddit-da", streaming=streaming)
    ds = dataset["train"]
    return ds


def load_tokenizer_ds():
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
    n_reddit = len(reddit) # 1 908 887
    n_dagw = len(dagw) # 666 437

    reddit = load_reddit(streaming=True)  # use all tokens ~86M
    dagw = load_dagw(streaming=True)  # use all tokens (-danavis, -twitter) ~1 000M tokens


    # calculate proportion of each dataset
    arr = np.array([n_tweets, n_news, n_dagw, n_reddit])
    prob = arr / sum(arr)

    ds = interleave_datasets([tweets, news, dagw, reddit], probabilities=prob.tolist())
    ds.take(n_reddit + n_dagw + n_tweets, n_news)
    return ds

def load_dfm_dataset(dataset: str, **kwargs) -> Dataset:
    """load a predefined dfm dataset

    Args:
        dataset (str): A predefined dataset
    
    Returns:
        Dataset: a Huggingface dataset
    """
    dataset_loaders = {"tokenization": load_tokenizer_ds,
                       "hopetweets": load_tweets,
                       "reddit": load_reddit,
                       "danews": load_news,
                       "dagw": load_dagw}

    if dataset in dataset_loaders:
        return dataset_loaders[dataset.lower()](**kwargs)
    else:
        raise ValueError(f"invalid dataset. Valid datasets include {dataset_loaders.keys()}")
