"""loads the dataset used for the training the tokenizers"""

import os
import sys

from datasets import load_dataset


def load_tweets(dedupe=True):
    cwd = os.getcwd()
    f_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(f_path, "..", "data")
    sys.path.append(data_path)
    from dedupe import min_hash_deduper, duplicate_filter
    os.chdir(data_path)
    
    dataset = load_dataset("HopeTweet", streaming=True)
    ds = dataset["train"]
    if dedupe:
        ds = ds.map(min_hash_deduper, batched=True, batch_size=50_000)
    os.chdir(cwd)
    return ds    


def load_news(dedupe=True):
    cwd = os.getcwd()
    f_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(f_path, "..", "data")
    sys.path.append(data_path)
    from dedupe import min_hash_deduper, duplicate_filter
    os.chdir(data_path)
    
    dataset = load_dataset("DaNews", streaming=True)
    ds = dataset["train"]
    if dedupe:
        ds = ds.map(min_hash_deduper, batched=True, batch_size=50_000)
    os.chdir(cwd)
    return ds    


tweets = load_tweets(dedupe=True)
news = load_tweets(dedupe=True)
reddit