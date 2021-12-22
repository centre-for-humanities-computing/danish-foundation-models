"""
Loading scripts for HF type datasets
"""
import os
import sys

from datasets import load_dataset, interleave_datasets


def load_tweets(dedupe=True):
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
    return ds


def load_dagw(filter_danavis=True):
    dataset = load_dataset("ddsc/danish-gigaword-no-twitter")
    ds = dataset["train"]
    if filter_danavis:
        ds = ds.filter(lambda example: example["source"] != "danavis")
    return ds


def load_reddit():
    dataset = load_dataset("DDSC/reddit-da")
    ds = dataset["train"]
    return ds


if __name__ == "__main__":

    def word_count(example):
        example["n_words"] = len(list(filter(lambda x: x, example["text"].split(" "))))
        return example

    avg_words_pr_tweet = 26
    n_tweet_words = 300_000_000
    n_tweets = n_tweet_words//avg_words_pr_tweet

    tweets = load_tweets(dedupe=False)
    tweets = tweets.take(n_tweets) # only use 300M tokens

    news = load_news()
    import numpy as np
    avg_words_pr_article = np.mean([a["n_words"] for a in list(news.take(10_000).map(word_count))])
    n_news_words = 300_000_000
    n_news = n_news_words//avg_words_pr_article
    news = news.take(n_news)
    
    reddit = load_reddit() # use all tokens ~86M
    dagw = load_dagw() # use all tokens (-danavis, -twitter) ~1 000M tokens
    ds = interleave_datasets([dagw, tweets, reddit, news])
