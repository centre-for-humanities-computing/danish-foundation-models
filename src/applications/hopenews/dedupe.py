"""
Applies quality filters to tweets filtering on language tag.

Dependent on:
    isn't dependent

Authors:
    Kenneth Enevoldsen
"""

import glob
import os
import sys
from pathlib import Path
import multiprocessing
from functools import partial

from tqdm import tqdm
from wasabi import msg

from datasets import load_from_disk

dfm_path = os.path.join("danish-foundation-models")
sys.path.append(dfm_path)

from src.dfm.cleaning import Deduper


def filter_batch(batch, i):
    """check whether sample i should be included"""
    return batch["passed_quality_filter"][i] is True



def dedupe(batch, deduper: Deduper):
    """
    """
    is_filtered = [filter_batch(batch, i) for i, _ in enumerate(batch["text"])]
    texts = (t for t, is_f in zip(zip(batch["id"], batch["text"]), is_filtered) if is_f)

    texts = list(texts)
    # apply deduper
    dedupe_gen = deduper.deduplicate(texts, return_generator=True, overwrite=False, store_corpus_to_disk = False, 
            store_mask_to_disk = False, store_lsh_cache_to_disk = False, store_config_to_disk = False)
    
    def __extract_is_duplicate(mask):
        return mask["duplicate"]

    # merge with ignored texts
    batch["is_duplicate"] = [__extract_is_duplicate(next(dedupe_gen)) if is_f else None for is_f in is_filtered]
    return batch


def main(
    path,
    n_process: int =-1,
) -> None:
    if n_process == -1:
        n_process = multiprocessing.cpu_count()

    deduper = Deduper(ngram_size=10)
    
    msg.info("Loading Dataset")
    ds = load_from_disk(path)
    ds = ds.add_column("id", list(range(len(ds))))  # create custom id col

    msg.info("Starting deduping")
    deduper = partial(dedupe, deduper=deduper)
    # dedupe dataset
    ds = ds.map(
        deduper,
        batched=True,
        batch_size=2**19,
    )
    msg.info(f"Writing {path} to disk")
    ds.save_to_disk(path)


if __name__ == "__main__":
    path = os.path.join("/work", "hope-infomedia_cleaned", "infomedia_2000-2021")
    main(path)
    msg.good(f"Finished Processing")

