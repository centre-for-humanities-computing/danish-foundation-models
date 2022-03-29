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
import multiprocessing
from functools import partial

from tqdm import tqdm
from wasabi import msg
import ndjson

from datasets import load_dataset

dfm_path = os.path.join("danish-foundation-models")
sys.path.append(dfm_path)

from src.dfm.cleaning import Deduper


def filter_batch(batch, i, already_checked):
    """check whether sample i should be included"""
    return batch["language"][i] in {"da"} and batch["passed_quality_filter"][i] is True and batch["id"] not in already_checked



def dedupe(batch, deduper: Deduper, already_checked):
    """
    """
    filter_batch_ = partial(filter_batch, already_checked=already_checked)
    is_filtered = [filter_batch_(batch, i) for i, _ in enumerate(batch["text"])]
    texts = (t for t, is_f in zip(zip(batch["id"], batch["text"]), is_filtered) if is_f)

    texts = list(texts)
    # apply deduper
    deduper.deduplicate(texts, return_generator=False, overwrite=True, store_corpus_to_disk = False, 
            store_mask_to_disk = True, store_lsh_cache_to_disk = True, store_config_to_disk = True)
    return batch


def main(
    read_path: str,
    write_path: str,
    year,
    n_process: int =-1,
) -> None:

    if n_process == -1:
        n_process = multiprocessing.cpu_count()

    if os.path.exists("deduplicated"):
        deduper = Deduper.load_from_disk("deduplicated")
        already_checked = deduper.mask
    else:
        deduper = Deduper(batch_size=2**20)
        already_checked = set()
    path = os.path.join(read_path, "**", "*.jsonl")
    jsonl_files = glob.glob(path, recursive=True)

    # create batches of files at time (approximately 10-30mb pr. file)
    batches = tqdm(jsonl_files)

    for i, j_files in enumerate(batches):
        w_path = os.path.join(write_path, f"{i}.jsonl")

        # load in batch
        if isinstance(j_files, str):
            j_files = [j_files]

        dataset = load_dataset("json", data_files={"train": j_files})
        ds = dataset["train"]

        #if "is_duplicate" in ds.features:
        #    msg.info(f"File {w_path} already deduplicated, skipping")
        #    continue
       
        ds = ds.add_column("id", [f"{year}_{i}_{id}" for id in range(len(ds))]) 
        
        msg.info("Starting deduping")
        deduper_fun = partial(dedupe, deduper=deduper)
        
        # dedupe dataset
        ds = ds.map(
            deduper_fun,
            batched=True,
            batch_size=2**20,
        )
        msg.info(f"Finished with {w_path}")
        # ds.to_json(w_path)


if __name__ == "__main__":
    for year in [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016]:
        read_path = os.path.join("/work", "netarkivet-cleaned", f"{year}")
        write_path = os.path.join("/work", "netarkivet-cleaned", f"{year}")
        main(read_path, write_path, year)
        msg.good(f"Finished year {year}")
