"""
Applies quality filters to tweets filtering on language tag.

Dependent on:
    src/applications/hopetwitter/quality_filter.py

Authors:
    Kenneth Enevoldsen
"""
import glob
import os
from pathlib import Path
import multiprocessing
from functools import partial

from wasabi import msg

from datasets import load_dataset

from dfm.cleaning import Deduper


def filter_batch(batch, i):
    """check whether sample i should be included"""
    return batch["lang"][i] in {"da"} and batch["passed_quality_filter"][i] is True


def dedupe(batch, deduper: Deduper):
    """
    dedupe a huggingface batch
    """
    is_filtered = [filter_batch(batch, i) for i, _ in enumerate(batch["text"])]
    texts = (t for t, is_f in zip(zip(batch["id"], batch["text"]), is_filtered) if is_f)

    texts = list(texts)
    # apply deduper
    dedupe_gen = deduper.deduplicate(
        texts,
        return_generator=True,
        overwrite=False,
        store_corpus_to_disk=False,
        store_mask_to_disk=False,
        store_lsh_cache_to_disk=False,
        store_config_to_disk=False,
    )

    def __extract_is_duplicate(mask):
        return mask["duplicate"]

    # merge with ignored texts
    batch["is_duplicate"] = [
        __extract_is_duplicate(next(dedupe_gen)) if is_f else None
        for is_f in is_filtered
    ]
    return batch


def main(
    read_path: str,
    write_path: str,
    n_process: int = -1,
) -> None:
    if n_process == -1:
        n_process = multiprocessing.cpu_count()
    Path(write_path).mkdir(exist_ok=True, parents=True)

    path = os.path.join(read_path, "**", "*.jsonl")
    json_files = glob.glob(path, recursive=True)

    w_path = os.path.join(
        write_path, "twitter_da_stopwords_2019-01-01_2021-04-30.arrow"
    )
    deduper = Deduper(ngram_size=10)

    dataset = load_dataset("json", data_files={"train": json_files})
    ds = dataset["train"]
    msg.info("Shuffling dataset")
    ds = ds.shuffle()

    msg.info("Starting deduping")
    deduper = partial(dedupe, deduper=deduper)
    # dedupe dataset
    ds = ds.map(
        deduper,
        batched=True,
        batch_size=2**19,
    )
    msg.info(f"Writing {w_path} to disk")
    ds.save_to_disk(w_path)


if __name__ == "__main__":
    read_path = os.path.join("/work", "twitter_cleaned")
    write_path = os.path.join("/work", "twitter_cleaned")
    main(read_path, write_path)
    msg.good("Finished Processing")
