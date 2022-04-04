import os
# from src.dfm.utils import batch
from pathlib import Path

from datasets import load_dataset
from wasabi import msg
from src.dfm.cleaning import Deduper, QualityFilter

from functools import partial


def filter_batch(batch, i):
    """check whether sample i should not be included"""
    return batch["source"][i] not in {"cc", "danavis", "dannet"} # cc, danavis, dannet

def filter_batch_deduper(batch, i):
    """check whether sample i should be included"""
    return batch["source"][i] not in {"cc", "danavis", "dannet"} and batch["passed_quality_filter"][i] is True


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


def dedupe_batch(batch, deduper: Deduper):
    """
    Applied deduper to a batch of texts and adds a new column called bat
    """
    is_filtered = [filter_batch_deduper(batch, i) for i, _ in enumerate(batch["text"])]
    texts = (t for t, is_f in zip(batch["text"], is_filtered) if is_f)

    # apply deduper
    is_duplicates = deduper.deduplicate(texts)
    is_duplicates = iter(is_duplicates)

    # merge with unfiltered texts
    batch["is_13_gram_duplicate"] = [
        next(is_duplicates) if is_f else None for is_f in is_filtered
    ]
    return batch




def main(
    n_process: int = 60,
) -> None:
    # load in batch
    ds = load_dataset("DDSC/partial-danish-gigaword-no-twitter")
    ds = ds["train"].select([0, 10, 20, 30, 40, 50])

    msg.info("Applying quality filter")
    # apply quality filter to batch
    ds = ds.map(
        q_filter,
        batched=True,
        batch_size=1024,
        num_proc=n_process,
    )

    deduper = Deduper(n_jobs=n_process)

    msg.info("Applying deduper...")
    dedupe_batch_ = partial(dedupe_batch, deduper=deduper)
    ds = ds.map(
        dedupe_batch_,
        batched=True,
        batch_size=2**13,
        num_proc=n_process,
    )

    write_path = os.path.join("/work", "data", "dagw-clean")
    Path(write_path).mkdir(exist_ok=True, parents=True)
    write_path = write_path / "dagw_clean.jsonl"

    msg.info(f"Writing {write_path} to disk")
    ds.to_json(write_path)

if __name__ == "__main__":
    main()