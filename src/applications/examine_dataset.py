from datasets import load_from_disk
from pathlib import Path
path = Path("/work/twitter_cleaned/twitter_da_stopwords_2019-01-01_2021-04-30")
twitter = load_from_disk(path)

import spacy 

def word_count(batch):
    nlp = spacy.blank("da")
    batch["n_tokens"] = [len(doc) for doc in nlp.pipe(batch["text"])]
    return batch

twitter = twitter.map(word_count, batched = True, batch_size=1024*2*2, num_proc=32)

print(sum(twitter["n_tokens"]))
# 973_892_104
print(sum(n_tok for n_tok, is_dup in zip(twitter["n_tokens"], twitter["is_duplicate"]) if is_dup is False))
# 463_943_640
twitter_sub = twitter.remove_columns([c for c in twitter.features.keys() if c not in {"n_tokens", "is_duplicate", "passed_quality_filter", "lang"}])
twitter_sub.to_csv("twitter_meta.csv")

path = Path("/work/hope-infomedia_cleaned/infomedia_2000-2021")
news = load_from_disk(path)

news = news.map(word_count, batched = True, batch_size=1024*2*2, num_proc=32)

print(sum(news["n_tokens"]))
# 9 296 359 450
print(sum(n_tok for n_tok, is_dup in zip(news["n_tokens"], news["is_duplicate"]) if is_dup is False))
# 8 667 100 588
news_sub = news.remove_columns([c for c in news.features.keys() if c not in {"n_tokens", "is_duplicate", "passed_quality_filter", "Source"}])
news_sub.to_csv("news_meta.csv")