"""
A minimal example of how to load the dataset
"""
import os
import sys

from datasets import load_dataset


f_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(f_path, ".."))
sys.path.append(os.getcwd())

from dedupe import min_hash_deduper, duplicate_filter
from utils import to_datetime

dataset = load_dataset("HopeTweet", streaming=True)
ds = dataset["train"]

ds = ds.map(to_datetime)
ds = ds.map(
    min_hash_deduper, batched=True, batch_size=50_000
)  # a day consist of approximately ~15k tweets
# ds = ds.filter(lambda example: example['is_min_hash_duplicate'] is False)


import json

users = {}
for i, example in enumerate(ds):
    if example["is_min_hash_duplicate"]:
        if example["author_id"] in users:
            users[example["author_id"]] += 1
        else:
            users[example["author_id"]] = 1
    if i % 100_000 == 0:
        print(i)
        with open("duplicate_authors", "w") as f:
            json.dump(users, f)


# for i in Counter(auth).most_common()[:10]:
#     try:
#         import ndjson
#         data_path = os.path.join("/work", "data", "twitter")
#         filepaths = [os.path.join(data_path, p) for p in os.listdir(data_path)]
#         row_n = 0
#         id = set()
#         for fp in filepaths:
#             with open(fp) as f:
#                 reader = ndjson.reader(f)
#                 for row in reader:
#                     if i[0] == row["author_id"]:
#                         raise ValueError
#     except ValueError:
#         print(row["includes"]["users"][0]["username"])
