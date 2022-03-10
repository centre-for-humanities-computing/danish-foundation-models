"""
Filters Netarkivet based on the language tags

Dependent on:
    isn't dependent

Authors:
    Kenneth Enevoldsen
"""

import glob
import os
import sys
from pathlib import Path
from functools import partial

from wasabi import msg

from datasets import load_dataset

dfm_path = os.path.join("githubs", "danish-foundation-models")
sys.path.append(dfm_path)

from src.dfm.cleaning import Deduper


def filter_batch(batch, i):
    """check whether sample i should be included"""
    return batch["lang"][i] in {"da"} and batch["passed_quality_filter"] is True


def dedupe_batch(batch, deduper: Deduper):
    """
    Applied deduper to a batch of texts and adds a new column called bat
    """
    is_filtered = [filter_batch(batch, i) for i, _ in enumerate(batch["text"])]
    texts = (t for t, is_f in zip(batch["text"], is_filtered) if is_f)

    # apply deduper
    is_duplicates = deduper.is_duplicate(texts)
    is_duplicates = iter(is_duplicates)

    # merge with unfiltered texts
    batch["is_13_gram_duplicate"] = [
        next(is_duplicates) if is_f else None for is_f in is_filtered
    ]
    return batch


def main(
    read_path: str,
    write_path: str,
    n_process: int = 60,
) -> None:
    Path(write_path).mkdir(exist_ok=True, parents=True)

    path = os.path.join(read_path, "**", "*.ndjson")
    json_files = glob.glob(path, recursive=True)

    deduper = Deduper(n_jobs=n_process)

    for i, j_files in enumerate(json_files):
        w_path = os.path.join(write_path, f"{i}.jsonl")

        # load in batch
        dataset = load_dataset("json", data_files={"train": [j_files]})
        ds = dataset["train"]
        if "is_13_gram_duplicate" in ds.features:
            msg.info(f"File {w_path} already processed, skipping")
            continue

        # apply quality filter to batch
        dedupe_batch_ = partial(dedupe_batch, deduper=deduper)
        ds = ds.map(
            dedupe_batch_,
            batched=True,
            batch_size=2**13,
            num_proc=n_process,
        )
        msg.info(f"Writing {w_path} to disk")
        ds.to_json(w_path)


if __name__ == "__main__":
    for year in [2015, 2016]:
        read_path = os.path.join("/work", "netarkivet-cleaned", f"{year}")
        write_path = os.path.join("/work", "netarkivet-cleaned", f"{year}")
        main(read_path, write_path)
        msg.good(f"Finished year {year}")
