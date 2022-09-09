"""a quick script for generating a temporary jsonl file
"""

import random

from datasets import load_dataset

path = "/Users/au561649/Desktop/Github/danish-foundation-models/data/test/train-00000-of-00002.parquet"
ds = load_dataset("parquet", data_files=path)


lang = ["da", "en"]
langs = [lang[random.randint(0, 1)] for i in range(ds.num_rows["train"])]

ds = ds["train"].add_column("lang", langs)
ds.to_parquet(path)