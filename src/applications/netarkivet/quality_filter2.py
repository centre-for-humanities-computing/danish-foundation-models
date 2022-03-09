"""
Filters Netarkivet based on the language tags

Dependent on:
    isn't dependent

Authors:
    Kenneth Enevoldsen
"""

import argparse
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

dfm_path = os.path.join("githubs", "danish-foundation-models")
sys.path.append(dfm_path)

from src.dfm.cleaning import QualityFilter


def filter_batch(batch, i):
    """check whether sample i should be included"""
    return batch["lang"][i] in {"da"}


def q_filter(batch):
    """
    Quality filter which takes in a hf datasets batch and and applies a quality
    filter to all the texts which pass the filter_batch
    """
    qf = QualityFilter()
    is_filtered = [filter_batch(batch, i) for i, _ in enumerate(batch["text"])]
    texts = (t for t, is_f in zip(batch["text"], is_filtered) if is_f)

    # apply q_filter
    filter_gen = qf.describe_filter(texts, batch_size=1024)

    # merge with unfiltered texts
    batch["filtered"] = [next(filter_gen) if is_f else None for is_f in is_filtered]
    return batch


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


def write_to_ndjson(path, ds):
    with open(path, "w") as f:
        writer = ndjson.writer(f, ensure_ascii=False)
        for sample in ds:
            writer.writerow(sample)


def main(
    read_path: str,
    write_path: str,
    n_process: int = 32,
) -> None:
    Path(write_path).mkdir(exist_ok=True, parents=True)

    path = os.path.join(read_path, "**", "*.parquet")
    parquet_files = glob.glob(path, recursive=True)

    # create batches of 20 files at time (approximately 10-30mb pr. file)
    batches = tqdm(list(batch(parquet_files, 20)))

    for i, p_files in enumerate(batches):
        w_path = os.path.join(write_path, f"{i}.jsonl")
        if os.path.exists(w_path):
            msg.info(f"File {w_path} already exist, skipping")
            continue

        # load in batch
        dataset = load_dataset("parquet", data_files={"train": [p_files]})
        ds = dataset["train"]

        # apply quality filter to batch
        ds = ds.map(
            q_filter,
            batched=True,
            batch_size=1024,
            num_proc=n_process,
            load_from_cache_file=False,
        )
        msg.info(f"Writing {w_path} to disk")
        write_to_ndjson(w_path, ds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # read_path = os.path.join("/work", "netarchive", "2009_textcorpus.parquet")
    # write_path = os.path.join("/work", "netarkivet-cleaned", "2009_textcorpus")

    parser.add_argument("--rpath", help="path where to search for parquet files", default=)
    parser.add_argument("--wpath", help="path where to save for ndjson files")
    args = parser.parse_args()

    read_path = args["rpath"]
    write_path = args["wpath"]

    main(read_path, write_path)
    msg.good("Done")
