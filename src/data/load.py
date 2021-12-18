"""
A minimal example of how to load the datasets
"""
import os
f_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(f_path, ".."))

from datasets import load_dataset, interleave_datasets

tweets = load_dataset('HopeTweet', streaming=True)
news = load_dataset('DaNews', streaming=True)
dagw = load_dataset("dagw", streaming=True)
reddit = load_dataset("reddit-da", streaming=True)

# None have train test splits
train_tweets = tweets["train"]
train_news = news["train"]
train_dagw = dagw["train"]
train_reddit = reddit["train"]


ds = interleave_datasets([train_tweets, train_news, train_dagw, train_reddit])

ds = ds.shuffle(buffer_size=10_000, seed=42)

test_size = 100_000
test = ds.take(test_size)
train = ds.skip(test_size)