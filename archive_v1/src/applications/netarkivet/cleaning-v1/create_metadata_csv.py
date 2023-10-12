"""
Create a metadata csv for netarkivet datasets to make obtaining metadata faster.

Authors:
    Kenneth Enevoldsen
"""

import glob
import os
from pathlib import Path

import spacy
from datasets import load_dataset
from datasets.utils import disable_progress_bar
from wasabi import msg

disable_progress_bar()


def word_count(batch):
    nlp = spacy.blank("da")
    batch["n_tokens"] = [len(doc) for doc in nlp.pipe(batch["text"])]
    return batch


if __name__ == "__main__":
    path = Path("/work/netarkivet-cleaned")
    for year in range(2006, 2017):
        msg.info(f"Started year: {year}")
        y_path = path / str(year) / "*.jsonl"
        j_files = glob.glob(str(y_path))
        j_files = sorted(
            j_files, key=lambda path: int(os.path.splitext(path)[0].split("/")[-1])
        )
        for f in j_files:
            f_, ext = os.path.splitext(f)
            s_path = f + "_meta.csv"

            if os.path.exists(s_path):
                msg.warn(f"file already exist, skipping: {s_path}")
                continue

            ds = load_dataset("json", data_files=f)
            ds = ds["train"]
            ds_subset = ds.remove_columns(
                [
                    c
                    for c in ds.features.keys()
                    if c
                    not in {
                        "text",
                        "n_tokens",
                        "is_duplicate",
                        "passed_quality_filter",
                        "timestamp",
                        "language",
                        "domain_key",
                    }
                ]
            )
            ds_subset = ds_subset.map(
                word_count,
                batched=True,
                batch_size=1024 * 2 * 2,
                num_proc=32,
                remove_columns=["text"],
            )
            ds_subset.to_csv(s_path)
            msg.info(f"   Saved file to {s_path}")
