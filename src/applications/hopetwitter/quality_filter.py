"""
Applies quality filters to tweets filtering on language tag.

Dependent on:
    src/applications/hopetwitter/flatten_ndjson.py

Authors:
    Kenneth Enevoldsen
"""

import glob
import os
from pathlib import Path
import multiprocessing

from wasabi import msg
from datasets import load_dataset

from dfm.cleaning import QualityFilter


def filter_batch(batch, i):
    """check whether sample i should be included"""
    return batch["lang"][i] in {"da"}


def q_filter(batch):
    """
    Quality filter which takes in a hf datasets batch and and applies a quality
    filter to all the texts which pass the filter_batch
    """
    qf = QualityFilter(
        min_stop_words=1,  # changed from 2
        mean_word_length=(2, 14),
        # extended from 3, 10 due to more variance in smaller texts
        doc_length=(10, 10_000),  # changed from 50-100,000
        alpha_ratio=0.6,
        duplicate_lines_chr_fraction=0.2,
        duplicate_paragraph_chr_fraction=0.2,
        top_ngram_chr_fraction_thresholds=[0.20, 0.18, 0.16],
        top_ngram_chr_fraction_range=(2, 4),
        duplicate_n_gram_fraction_thresholds=[
            0.25,
            0.24,
            0.23,
            0.22,
            0.21,
            0.20,
        ],
        duplicate_n_gram_fraction_range=(5, 10),
        ignore_filters=[
            "symbol_2_word_hashtag",  # this is tweets # is common
            "symbol_2_word_ellipsis",
            "line_bullets_or_ellipsis",
        ],
    )
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
    n_process: int = -1,
) -> None:
    if n_process == -1:
        n_process = multiprocessing.cpu_count()
    Path(write_path).mkdir(exist_ok=True, parents=True)

    path = os.path.join(read_path, "**", "*.ndjson")
    json_files = glob.glob(path, recursive=True)

    w_path = os.path.join(
        write_path, "twitter_da_stopwords_2019-01-01_2021-04-30.jsonl"
    )
    if os.path.exists(w_path):
        raise Exception(f"File {w_path} already exist")

    # load in batch
    dataset = load_dataset("json", data_files={"train": json_files})
    ds = dataset["train"]

    # apply quality filter to batch
    ds = ds.map(
        q_filter,
        batched=True,
        batch_size=1024,
        num_proc=n_process,
    )
    ds.shuffle()
    msg.info(f"Writing {w_path} to disk")
    ds.to_json(w_path)


if __name__ == "__main__":
    read_path = os.path.join("/work", "twitter_cleaned")
    write_path = os.path.join("/work", "twitter_cleaned")
    main(read_path, write_path)
    msg.good("Finished Processing")
