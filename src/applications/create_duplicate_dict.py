"""
Create a pickle file of duplicates from the duplicate mask.
"""

import ndjson
import pickle
import glob
from datasets import load_dataset

mask_files = glob.glob("/work/netarkivet-cleaned/deduplicated/*/mask.jsonl")


for file in mask_files:
    print(f"on file: {file}")
    year = int(file.split("/")[-2])
    
    ds = load_dataset("json", data_files=file)
    ds = ds["train"]
    ids = ds["id"]

    is_duplicate = {}
    for i in ds:
        is_duplicate[i["id"]] = i["duplicate"]
    with open(f"/work/netarkivet-cleaned/deduplicated/{year}_duplicate_ids", "wb") as f:
        pickle.dump(is_duplicate, f)