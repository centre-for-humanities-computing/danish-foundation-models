"""
Loading newspaper dataset
"""
# %%
import os
import sys

from datasets import load_dataset

f_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(f_path, ".."))
sys.path.append(os.getcwd())

from dedupe import duplicate_filter, min_hash_deduper
from utils import to_datetime

dataset = load_dataset("DaNews", streaming=True)
ds = dataset["train"]

# ds = ds.map({to_datetime, 'publishdate'})
# ds = ds.map(
#     min_hash_deduper, batched=True, batch_size=50_000
# )

sources = set()
for i, example in enumerate(dataset["train"]):
    sources.add(example["source"])

    if i % 100_000 == 0:
        print(i)
