"""
Preprocess (quality filter and deduplicate) the DFM compositite dataset consisting of
dagw and reddit-da dataset.
"""
import os
from pathlib import Path
from functools import partial


from datasets import load_dataset, concatenate_datasets
from wasabi import msg
from dfm.cleaning import Deduper, QualityFilter


def q_filter(batch):
    """
    Quality filter which takes in a hf datasets batch and and applies a quality
    filter
    """
    qf = QualityFilter()
    texts = batch["text"]

    # apply q_filter
    filtered = list(qf.describe_filter(texts, batch_size=1024))
    batch["passed_quality_filter"] = [
        None if is_filtered_by is None else is_filtered_by == "passed filters"
        for is_filtered_by in filtered
    ]

    # add colums for specific filters
    #   manually add max_chr_length as it is an exception handling filter
    prev_filters = {None}
    batch["filtered_by_max_chr_length"] = [
        None if is_f in prev_filters else is_f == "max_chr_length" for is_f in filtered
    ]
    prev_filters.add("max_chr_length")

    for qfilter in qf.filters:
        batch["filtered_by_" + qfilter] = [
            None if is_f in prev_filters else is_f == qfilter for is_f in filtered
        ]
        prev_filters.add(qfilter)
    return batch


def filter_batch_deduper(batch, i):
    """check whether sample i should be included"""
    return batch["passed_quality_filter"][i] is True


def dedupe_batch(batch, deduper: Deduper):
    """
    Applied deduper to a batch of texts and adds a new column called bat
    """
    is_filtered = [filter_batch_deduper(batch, i) for i, _ in enumerate(batch["text"])]
    texts = (
        t for t, is_f in zip(zip(batch["doc_id"], batch["text"]), is_filtered) if is_f
    )

    # apply deduper
    is_duplicates = deduper.deduplicate(
        texts,
        return_generator=True,
        store_corpus_to_disk=False,
        store_lsh_cache_to_disk=False,
        store_mask_to_disk=False,
        overwrite=True,
    )
    is_duplicates = iter(is_duplicates)

    # merge with unfiltered texts
    batch["is_13_gram_duplicate"] = [
        next(is_duplicates) if is_f else None for is_f in is_filtered
    ]
    return batch


def filter_categories(examples, remove_cat={"danavis"}):
    i = 0
    while i < len(examples["source"]):
        s = examples["source"][i]
        if s in remove_cat:
            for k in examples:
                examples[k].pop(i)
        else:
            i += 1
    return examples


def main(
    n_process: int = 16,
) -> None:
    # load in batch
    dagw = load_dataset("DDSC/partial-danish-gigaword-no-twitter")
    dagw = dagw["train"]

    reddit_da = load_dataset("DDSC/reddit-da")
    reddit_da = reddit_da["train"]
    reddit_da = reddit_da.rename_columns({"id": "doc_id"})
    reddit_da = reddit_da.add_column("LICENSE", ["MIT"] * len(reddit_da))
    reddit_da = reddit_da.add_column(
        "date_built", ["Wed Dec 15 00:00:00 2021 CEST +0200"] * len(reddit_da)
    )
    reddit_da = reddit_da.add_column("source", ["reddit-da"] * len(reddit_da))
    reddit_da = reddit_da.add_column("uri", ["NA"] * len(reddit_da))

    ds = concatenate_datasets([reddit_da, dagw])

    msg.info("Filter categories")
    ds = ds.map(filter_categories, batched=True)

    msg.info("Applying quality filter")
    # apply quality filter to batch
    ds = ds.map(
        q_filter,
        batched=True,
        batch_size=1024,
        num_proc=n_process,
    )

    deduper = Deduper(n_jobs=n_process)

    msg.info("Applying deduper")
    dedupe_batch_ = partial(dedupe_batch, deduper=deduper)
    ds = ds.map(dedupe_batch_, batched=True, batch_size=2**13)

    write_path = Path(os.path.join("/work", "dagw-clean"))
    write_path.mkdir(exist_ok=True, parents=True)
    write_path = write_path / "dagw_reddit.arrow"

    msg.info(f"Writing {write_path} to disk")
    ds.save_to_disk(str(write_path))


if __name__ == "__main__":
    main()
