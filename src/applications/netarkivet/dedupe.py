"""
Applies quality filters to Netarkivet filtering based on language tags.

Dependent on:
    isn't dependent

Authors:
    Kenneth Enevoldsen
"""
from typing import Iterable

import glob
import os
import sys
from itertools import islice
from pathlib import Path

from tqdm import tqdm
from wasabi import msg
import ndjson

from datasets import load_dataset

dfm_path = os.path.join("danish-foundation-models")
sys.path.append(dfm_path)

from src.dfm.cleaning import Deduper


def filter_batch(batch, i):
    """check whether sample i should be included"""
    return batch["language"][i] in {"da"}


def batch(dataset: Iterable, batch_size: int) -> Iterable:
    """Creates batches from an iterable.

    Args:
        dataset (Iterable): Your dataset you want to batch given as an iterable (e.g. a
            list).
        batch_size (int): Your desired batch size

    Returns:
        Iterable: An iterable of tuples of size equal to batch_size.

    Example:
        >>> batches = batch([1,2, 3, 4, 5], 2)
        >>> print(list(batches))
        [(1, 2), (3, 4), (5,)]
    """
    iterable_dataset = iter(dataset)
    while True:
        chunk = tuple(islice(iterable_dataset, batch_size))
        if not chunk:
            break
        yield chunk



def main(
    read_path: str,
    write_path: str,
    n_process: int = 32,
) -> None:

    deduper = Deduper()
    path = os.path.join(read_path, "**", "*.jsonl")
    jsonl_files = glob.glob(path, recursive=True)

    # create batches of files at time (approximately 10-30mb pr. file)
    batches = tqdm(list(batch(parquet_files, 64)))

    for i, p_files in enumerate(batches):
        w_path = os.path.join(write_path, f"{i}.jsonl")
        if os.path.exists(w_path):
            msg.info(f"File {w_path} already exist, skipping")
            continue

        # load in batch
        p_files = list(p_files)
        dataset = load_dataset("parquet", data_files={"train": p_files})
        ds = dataset["train"]

        # apply quality filter to batch
        ds = ds.rename_column("content", "text")
        ds = ds.map(
            q_filter,
            batched=True,
            batch_size=1024,
            num_proc=n_process,
        )
        msg.info(f"Writing {w_path} to disk")
        ds.to_json(w_path)


if __name__ == "__main__":
    for year in [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]:
        read_path = os.path.join("/work", "netarkivet-cleaned", f"{year}")
        write_path = os.path.join("/work", "netarkivet-cleaned", f"{year}")
        main(read_path, write_path)
        msg.good(f"Finished year {year}")
