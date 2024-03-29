"""
Add is_duplicate column to NetArkivet Textcorpus (NAT)

Dependent on:
    src/applications/netarkivet/dedupe.py

Authors:
    Kenneth Enevoldsen
"""
import glob
import os
from pathlib import Path

from datasets import load_dataset
from wasabi import msg


def main(netarkivet_path=Path("/work/netarkivet-cleaned")):
    for year in range(2010, 2011):
        msg.info(f"At year: {year}")
        year_path = netarkivet_path / str(year) / "*.jsonl"
        jsonl_files = glob.glob(str(year_path))

        jsonl_files_ = [
            (int(os.path.split(file)[-1].split(".")[0]), file) for file in jsonl_files
        ]
        jsonl_files_ = sorted(jsonl_files_, key=lambda id_file: id_file[0])

        for id_, jsonl_file in jsonl_files_:
            msg.info(f"\tAt file {jsonl_file}")

            # check if duplicate column is already added:
            peak_ds = load_dataset("json", data_files=jsonl_file, streaming=True)
            if "is_duplicate" in next(iter(peak_ds["train"])):
                continue

            # if it isn't add it
            ds = load_dataset("json", data_files=jsonl_file)
            ds = ds["train"]

            meta_path = str(jsonl_file) + "_meta.csv"
            meta = load_dataset("csv", data_files=meta_path)
            meta = meta["train"]
            assert len(meta) == len(
                ds,
            ), "length of dataset and its metadata is not the same."
            ds = ds.add_column("is_duplicate", meta["is_duplicate"])
            ds.to_json(jsonl_file)


if __name__ == "__main__":
    main()
