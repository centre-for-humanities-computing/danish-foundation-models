"""
Applies quality filters to tweets filtering on language tag.

Dependent on:
    src/applications/nopenews/quality_filter.py

Authors:
    Kenneth Enevoldsen
"""

import os
from functools import partial

from datasets import load_from_disk
from wasabi import msg

from dfm.cleaning import Deduper


def filter_batch(batch, i):
    """check whether sample i should be included"""
    return batch["passed_quality_filter"][i] is True


def dedupe(batch, deduper: Deduper, dedupe_path: str):
    """ """
    is_filtered = [filter_batch(batch, i) for i, _ in enumerate(batch["text"])]
    texts = (t for t, is_f in zip(zip(batch["id"], batch["text"]), is_filtered) if is_f)

    texts = list(texts)
    # apply deduper
    dedupe_gen = deduper.deduplicate(
        texts,
        return_generator=True,
        overwrite=False,
        store_corpus_to_disk=False,
        store_mask_to_disk=True,
        store_lsh_cache_to_disk=False,
        store_config_to_disk=False,
        output_dir=dedupe_path,
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
    path,
) -> None:
    deduper = Deduper()

    msg.info("Loading Dataset")
    ds = load_from_disk(path)
    ds = ds.add_column("id", list(range(len(ds))))  # create custom id col

    msg.info("Starting deduping")
    deduper = partial(
        dedupe, deduper=deduper, dedupe_path=os.path.join(path, "deduplicated")
    )
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
    msg.good("Finished Processing")
