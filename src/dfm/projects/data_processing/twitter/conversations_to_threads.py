"""
Convert Twitter conversations to threads.
"""

from collections import defaultdict
from pathlib import Path
import json
from typing import Any, Generator, Iterable, Union
import logging

Tweet = dict[str, Any]
Tweets = list[Tweet]
TweetWithResponses = dict[str, Any]
TweetId = str
        


def load_conversation(file: Path) -> Iterable[Tweet]:
    with open(file, "r") as f:
        for line in f:
            yield json.loads(line)


def get_conversation_paths() -> Generator[Path, None, None]:
    folder = Path("/data-big-projects/twitter_threads")
    files = folder.glob("*")
    return files


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


def add_replies(tweet: Tweet, tweet_id2responses: dict[str, list[str]], tweet_id2tweet: dict[str, Tweet]) -> None:
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
        logging.warning(f"Root tweet has referenced tweets \n {root_tweet['referenced_tweets']} created at {root_tweet['created_at']}")



def process_conversation(conversation: Iterable[Tweet]) -> Union[Tweet, None]:
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
        logging.warning(f"There is no root tweet (conversation length: {len(conversation)})")
        return 
    check_root(root_tweet)

    # create tweet_id to response mapping
    tweet_id2responses: dict[str, list[str]] = defaultdict(list)
    for tweet_id, responded_to_tweet_id in tweet_id2responded_to_tweet_id.items():
        tweet_id2responses[responded_to_tweet_id].append(tweet_id)
    
    # add responses to tweets
    add_replies(root_tweet, tweet_id2responses, tweet_id2tweet)

    return root_tweet


def main():
    conversations = get_conversation_paths()

    for conv in conversations:

        conversation = load_conversation(conv)
        
        conv = list(conversation)

        root_tweet = process_conversation(conv)

        if len(conv) > 2:
            break

if __name__ == "__main__":
    main()