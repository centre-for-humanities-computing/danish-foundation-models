"""
This script convert the twitter data to threads.
"""

from functools import partial
from pathlib import Path
import json
from typing import Iterable, Any
import multiprocessing
from tqdm import tqdm
import gzip
Tweet = dict[str, Any]



def is_retweet(tweet: Tweet) -> bool:
    ref_tweets = tweet.get("referenced_tweets", [])
    assert isinstance(ref_tweets, list)
    for meta in ref_tweets:  # type: ignore
        if meta["type"] == "retweeted":
            return True
    return False

def generator_from_file(path: Path) -> Iterable[Tweet]:
    with path.open("r") as f:
        for line in f:
            yield json.loads(line)

def get_conversation_id(tweet: Tweet) -> str:
    return tweet["conversation_id"]



def write_tweets_to_conversation_folder(tweets: Iterable[Tweet], folder: Path) -> None:
    """
    for each tweet in the iterable get the conversation id 
    and then write it to a file using a jsonl format with a gzip compression
    """
    for tweet in tweets: # type: ignore
        if is_retweet(tweet):
            continue

        conversation_id = get_conversation_id(tweet)
        write_path = folder / (conversation_id + ".jsonl")
        
        with gzip.open(write_path, "at") as f:
            f.write(json.dumps(tweet) + "\n")


def create_done_file(done_path: Path) -> None:
    with done_path.open("w") as f:
        f.write("")


def process_file(file: Path, write_folder: Path, progress_folder: Path) -> None:
    done_path = progress_folder / (file.name + "-done.txt")

    if done_path.exists():
        print(f"Skipping {file} because it is done")
        return
    tweets = generator_from_file(file)
    write_tweets_to_conversation_folder(tweets, write_folder)
    create_done_file(done_path)

def main(n_processes: int = 32):
    path = Path("/work/dfm-data/v3.0.0/twitter/005_twitter-stopword")
    write_folder = Path("/work/dfm-data/v3.0.0/twitter/twitter_threads")
    write_folder.mkdir(exist_ok=True, parents=True)
    progress_folder = Path("progress_folder")
    progress_folder.mkdir(exist_ok=True, parents=True)

    files = list(path.glob("*.ndjson"))

    _process_files = partial(process_file, write_folder=write_folder, progress_folder=progress_folder)
    
    with multiprocessing.Pool(n_processes) as pool:
        for _ in tqdm(pool.imap_unordered(_process_files, files), total=len(files)):
            pass


if __name__ == "__main__":
    main()
