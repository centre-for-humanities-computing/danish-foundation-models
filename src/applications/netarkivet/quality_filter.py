"""
Applies quality filters to Netarkivet filtering based on language tags.

Dependent on:
    isn't dependent

Authors:
    Kenneth Enevoldsen
"""

import glob
import os
import sys
from pathlib import Path

from tqdm import tqdm
from wasabi import msg

from datasets import load_dataset

dfm_path = os.path.join("danish-foundation-models")
sys.path.append(dfm_path)

from src.dfm.cleaning import QualityFilter
from src.dfm.utils import batch


def filter_batch(batch, i):
    """check whether sample i should be included"""
    return batch["language"][i] in {"da"}


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
    merge_filter = [next(filter_gen) if is_f else None for is_f in is_filtered]
    batch["passed_quality_filter"] = [
        None if is_filtered_by is None else is_filtered_by == "passed filters"
        for is_filtered_by in merge_filter
    ]

    # add colums for specific filters
    #   manually add max_chr_length as it is an exception handling filter
    prev_filters = {None}
    batch["filtered_by_max_chr_length"] = [
        None if is_f in prev_filters else is_f == "max_chr_length"
        for is_f in merge_filter
    ]
    prev_filters.add("max_chr_length")

    for qfilter in qf.filters:
        batch["filtered_by_" + qfilter] = [
            None if is_f in prev_filters else is_f == qfilter for is_f in merge_filter
        ]
        prev_filters.add(qfilter)
    return batch


def main(
    read_path: str,
    write_path: str,
    n_process: int = 60,
) -> None:
    Path(write_path).mkdir(exist_ok=True, parents=True)

    path = os.path.join(read_path, "**", "*.parquet")
    parquet_files = glob.glob(path, recursive=True)

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
    for year in range(2006, 2017):
        read_path = os.path.join("/work", "netarchive", f"{year}_textcorpus.parquet")
        write_path = os.path.join("/work", "netarkivet-cleaned", f"{year}")
        main(read_path, write_path)
        msg.good(f"Finished year {year}")
