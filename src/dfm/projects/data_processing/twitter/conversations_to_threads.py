"""
Convert Twitter conversations to threads.
"""

import json
import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Generator, Iterable, Union

Tweet = dict[str, Any]
Tweets = list[Tweet]
TweetWithResponses = dict[str, Any]
TweetId = str


def load_conversation(file: Path) -> Iterable[Tweet]:
    with open(file, "r") as f:
        for line in f:
            yield json.loads(line)


def get_conversation_paths() -> Generator[Path, None, None]:
    folder = Path("/work/dfm-data/v3.0.0/twitter/twitter_threads")
    files = os.scandir(folder)
    for file in files:
        yield Path(file.path)


def get_replied_to(tweet: Tweet) -> Union[str, None]:
    ref_tweets = tweet.get("referenced_tweets", [])
    assert isinstance(ref_tweets, list)
    for meta in ref_tweets:  # type: ignore
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


def check_root(root_tweet: Tweet) -> None:
    ref_tweets = root_tweet.get("referenced_tweets", [])
    if ref_tweets:
        logging.warning(
            f"Root tweet has referenced tweets \n {root_tweet['referenced_tweets']} created at {root_tweet['created_at']}"
        )


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
            f"There is no root tweet (conversation length: {len(conversation)})"
        )
        return
    check_root(root_tweet)

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
        user = tweet["author_id"]
        thread = f"{'    ' * indent}{user}: {text}\n"
        if "responses" in tweet:
            for response in tweet["responses"]:
                thread += convert_tweet_to_thread(response, indent + 1)
        return thread

    thread = convert_tweet_to_thread(root_tweet)
    return thread


def main():
    conversations = get_conversation_paths()

    for i, conv in enumerate(conversations):
        print(i)

        conversation = load_conversation(conv)
        conv = list(conversation)

        root_tweet = process_conversation(conv)

        if root_tweet is None:
            continue

        thread = convert_conversation_to_thread(root_tweet)
        print(thread)

        if len(conv) > 2:
            break


if __name__ == "__main__":
    main()
