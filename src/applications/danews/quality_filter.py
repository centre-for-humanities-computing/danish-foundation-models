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
import multiprocessing

from wasabi import msg

from datasets import load_dataset

dfm_path = os.path.join("danish-foundation-models")
sys.path.append(dfm_path)

from src.dfm.cleaning import QualityFilter
from src.dfm.utils import batch


def filter_batch(batch, i):
    """check whether sample i should be included. This does not filter anything"""
    return True


def q_filter(batch):
    """
    Quality filter which takes in a hf datasets batch and and applies a quality
    filter to all the texts which pass the filter_batch
    """
    qf = QualityFilter(
        min_stop_words=2,
        mean_word_length=(3, 10),
        doc_length=(50, 100_000),
        alpha_ratio=0.6,
        symbol_2_word_hashtag=0.1,
        symbol_2_word_ellipsis=0.1,
        max_p_begin_bullets=0.9,
        max_p_end_ellipsis=0.3,
        min_bullets=2,
        min_ellipsis=2,
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
        ignore_filters=[],
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


def add_text_col(example: dict) -> dict:
    """constructs text column to news article"""
    example["text"] = ""
    if example["Heading"].strip(" "):
        example["text"] = example["Heading"]
    if example["SubHeading"].strip(" "):
        example["text"] += f'\n {example["SubHeading"]}'
    # if example["PublishDate"]:
    #     example["text"] += f'\n {example["PublishDate"]}'
    # if example["Paragraph"].strip(" "):
    #     example["text"] += f'\n\n {example["Paragraph"]}'
    if example["BodyText"].strip(" "):
        example["text"] += f'\n\n {example["BodyText"]}'
    return example


def main(
    read_path: str,
    write_path: str,
    n_process: int = -1,
) -> None:
    if n_process == -1:
        n_process = multiprocessing.cpu_count() - 2

    print("n_process:", n_process)

    Path(write_path).mkdir(exist_ok=True, parents=True)

    path = os.path.join(read_path, "**", "*.ndjson")
    json_files = glob.glob(path, recursive=True)

    w_path = os.path.join(write_path, f"infomedia_2000-2021.jsonl")

    # load in batch
    dataset = load_dataset("json", data_files={"train": json_files})
    ds = dataset["train"]

    print("adding text col")
    ds = ds.map(add_text_col, num_proc=n_process)

    # apply quality filter to batch
    print("applying filter")
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
    read_path = os.path.join("/work", "hope-infomedia", "yearly")
    write_path = os.path.join("/work", "hope-infomedia_cleaned")
    main(read_path, write_path)
    msg.good(f"Finished Processing")
