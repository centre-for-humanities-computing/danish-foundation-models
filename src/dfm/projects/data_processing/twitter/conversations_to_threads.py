"""
Convert Twitter conversations to threads.
"""

import gzip
import json
import logging
import os
from collections import defaultdict
from collections.abc import Generator, Iterable
from pathlib import Path
from typing import Any, Union

Tweet = dict[str, Any]
Tweets = list[Tweet]
TweetWithResponses = dict[str, Any]
TweetId = str


def _load_conversation(file: Path) -> Iterable[Tweet]:
    """
    Load conversation from a jsonl.gz file
    """
    with gzip.open(file, "rt") as f:
        for line in f:
            yield json.loads(line)


def load_conversation(file: Path) -> list[Tweet]:
    try:
        return list(_load_conversation(file))
    except:  # noqa
        logging.warning(f"Failed to load conversation {file}")
        return []


def get_conversation_paths() -> Generator[Path, None, None]:
    folder = Path("/work/dfm-data/v3.0.0/twitter/twitter_threads")
    files = os.scandir(folder)
    for file in files:
        yield Path(file.path)


def get_replied_to(tweet: Tweet) -> Union[str, None]:
    ref_tweets = tweet.get("referenced_tweets", [])
    assert isinstance(ref_tweets, list)
    for meta in ref_tweets:  # type: ignore # noqa
        if meta["type"] == "replied_to":
            return meta["id"]  # type: ignore


def sort_tweets_by_time(tweets: Tweets) -> Tweets:
    """
    Sort tweets by created_at
    """
    return sorted(tweets, key=lambda x: x["created_at"])


def add_replies(
    tweet: Tweet,
    tweet_id2responses: dict[str, list[str]],
    tweet_id2tweet: dict[str, Tweet],
) -> None:
    tweet_id = tweet["id"]
    responses = tweet_id2responses[tweet_id]
    tweets = [tweet_id2tweet[response] for response in responses]
    tweets = sort_tweets_by_time(tweets)
    tweet["responses"] = tweets
    for tweet in tweets:
        add_replies(tweet, tweet_id2responses, tweet_id2tweet)


def is_quote_tweet(root_tweet: Tweet) -> bool:
    ref_tweets = root_tweet.get("referenced_tweets", [])
    if ref_tweets:
        for ref in ref_tweets:
            if ref["type"] == "quoted":
                logging.info("tweet is qoute tweet")
                return True

        logging.warning(
            f"Root tweet has referenced tweets \n {root_tweet['referenced_tweets']} created at {root_tweet['created_at']}",
        )
    return False


def process_conversation(conversation: list[Tweet]) -> Union[Tweet, None]:
    tweet_id2tweet: dict[str, Tweet] = {}
    tweet_id2responded_to_tweet_id: dict[str, str] = {}
    root_tweet = None
    for tweet in conversation:
        tweet_id = tweet["id"]
        tweet_id2tweet[tweet_id] = tweet

        replied_to = get_replied_to(tweet)
        if replied_to:
            tweet_id2responded_to_tweet_id[tweet_id] = replied_to
        else:
            root_tweet = tweet

    if root_tweet is None:
        logging.warning(
            f"There is no root tweet (conversation length: {len(conversation)})",
        )
        return None
    if is_quote_tweet(root_tweet):
        return None

    # create tweet_id to response mapping
    tweet_id2responses: dict[str, list[str]] = defaultdict(list)
    for tweet_id, responded_to_tweet_id in tweet_id2responded_to_tweet_id.items():
        tweet_id2responses[responded_to_tweet_id].append(tweet_id)

    # add responses to tweets
    add_replies(root_tweet, tweet_id2responses, tweet_id2tweet)

    return root_tweet


def convert_conversation_to_thread(root_tweet: TweetWithResponses) -> str:
    """
    Convert the conversation to a thread on the format:

    User1: root_tweet
        User2: response to root_tweet
            User1: response to response to root_tweet
        User3: response to root_tweet
            User1: response to response to root_tweet
                User3: response to response to response to root_tweet
    """

    def convert_tweet_to_thread(tweet: TweetWithResponses, indent: int = 0) -> str:
        text = tweet["text"]
        user = root_tweet["includes"]["users"][0]["username"]
        thread = f"{'    ' * indent}{user}: {text}\n"
        if "responses" in tweet:
            for response in tweet["responses"]:
                thread += convert_tweet_to_thread(response, indent + 1)
        return thread

    thread = convert_tweet_to_thread(root_tweet)
    return thread


def convert_to_standard_format(root_tweet: TweetWithResponses) -> dict[str, Any]:
    """
    Convert the tweets to the standard format:
    {
    "id": "...",             # MANDATORY: source-specific identifier
    "text": "foo",           # MANDATORY: textual content of the document
    "source": "...",         # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
    "added": "...",          # OPTIONAL: timestamp we acquired this data (time file was created), specified as YYYY-MM-DD HH:MM:SS
    "created": "..."         # OPTIONAL: timestamp when orig document was created (best-guess if not available), should be specified as a range; "YYYY-MM-DD HH:MM:SS, YYYY-MM-DD HH:MM:SS"
    "metadata": {            # OPTIONAL: source-specific metadata
                                                                                "sub-source": "...", # OPTIONAL: E.g. "newspaper_ocr"
                                                                                ...
                                                                }
    }
    """

    id_ = root_tweet["conversation_id"]
    text = convert_conversation_to_thread(root_tweet)
    source = "HopeTwitter"
    added = "2019-01-01 00:00:00"
    created = created_at_to_timestamp(root_tweet["created_at"])
    metadata = {
        "root_tweet_id": root_tweet["id"],
        "possibly_sensitive": root_tweet["possibly_sensitive"],
        "root_tweet_lang": root_tweet["lang"],
        "root_tweet_retweet_count": root_tweet["public_metrics"]["retweet_count"],
        "root_tweet_reply_count": root_tweet["public_metrics"]["reply_count"],
        "root_tweet_like_count": root_tweet["public_metrics"]["like_count"],
        "root_tweet_quote_count": root_tweet["public_metrics"]["quote_count"],
    }
    return {
        "id": id_,
        "text": text,
        "source": source,
        "added": added,
        "created": created,
        "metadata": metadata,
    }


def created_at_to_timestamp(created_at: str) -> str:
    """
    Convert created_at to timestamp
    created_at: "2021-04-13T12:52:46.000Z" -->
    timestamp: "2021-04-13 12:52:46"
    """
    return created_at.replace("T", " ").replace(".000Z", "")


def main(overwrite: bool = True):
    logging.basicConfig(
        filename="conversations_to_threads.log",
        filemode="w",
        level=logging.INFO,
    )
    write_file = Path("/work/dfm-data/v3.0.0/twitter/data.jsonl.gz")
    if write_file.exists():
        if overwrite:
            logging.info(f"Deleting {write_file}")
            write_file.unlink()
        else:
            raise FileExistsError(f"{write_file} already exists")

    conversations = get_conversation_paths()

    for i, conv in enumerate(conversations):
        if i % 1000 == 0:
            logging.info(f"Processed {i} conversations")

        conversation = load_conversation(conv)

        root_tweet = process_conversation(conversation)

        if root_tweet is None:
            continue

        standard_format = convert_to_standard_format(root_tweet)

        with gzip.open(write_file, "at") as f:
            f.write(json.dumps(standard_format) + "\n")


if __name__ == "__main__":
    main()
