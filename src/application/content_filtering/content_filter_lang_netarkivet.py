"""
Filter the netarkivet based on its language tag derived from https://github.com/optimaize/language-detector

Order:
    Assumed run after content_filter_lang_netarkivet.py

Authors:
    Kenneth Enevoldsen
"""
from typing import List, Tuple

import os
from pathlib import Path
import shutil

import json
import multiprocessing as mp
from collections import Counter

import pandas as pd
from wasabi import msg

read_path = os.path.join("/work", "netarchive")
write_path = os.path.join("/work", "netarkivet-cleaned")
lang_codes = {"da"}
clean_code = "_filtered-lang"
write_filtered = False
n_process = (
    32  # 32 actual cores on 64 CPU Ucloud instance (we get Brokenpipe error with >32)
)


def get_paths(
    path=read_path,
    nested: bool = True,
    folder_suffix=".parquet",
    file_suffix=".parquet",
) -> List[str]:
    folders = [
        os.path.join(path, f) for f in os.listdir(path) if f.endswith(folder_suffix)
    ]
    if nested:
        return {
            f: [os.path.join(f, p) for p in os.listdir(f) if p.endswith(file_suffix)]
            for f in folders
        }
    return [
        os.path.join(f, p)
        for f in folders
        for p in os.listdir(f)
        if p.endswith(file_suffix)
    ]


def split_mult_extension(path: str) -> Tuple[str, str]:
    ext = ""
    while True:
        path_, ext_ = os.path.splitext(path)
        ext = ext_ + ext
        if path == path_:
            return path, ext
        path = path_


def process(path):
    folder, fname = os.path.split(path)
    fname_, ext = split_mult_extension(fname)
    fname = fname_ + clean_code + ext
    _, year = os.path.split(folder)
    write_folder = os.path.join(write_path, year)
    write_path_ = os.path.join(write_folder, fname)

    df = pd.read_parquet(path, engine="pyarrow")

    # filter
    df = df[df["language"].isin(lang_codes)]

    # record domains and timestamps
    domain_counts = Counter(df["domain_key"])
    timestamps = Counter(df["timestamp"].apply(lambda x: x[:8]))

    Path(write_folder).mkdir(parents=True, exist_ok=True)
    if write is True:
        df.to_parquet(write_path_, engine="pyarrow")

    return domain_counts, timestamps


def main(n_process=n_process):
    paths = get_paths()
    list(paths.keys())[0]

    if n_process == -1:
        n_process = mp.cpu_count()

    msg.info(f"Using {n_process} cores")

    for folder, paths_ in paths.items():
        msg.info(f"Currently processing folder: {folder}")

        _, year = os.path.split(folder)
        write_folder = os.path.join(write_path, year)
        s_path = os.path.join(write_folder, os.path.split(__file__)[-1] + "__SUCCESS")
        if os.path.isfile(s_path):
            msg.info(f"\tAlready processed - skipping")
        if os.path.isdir(write_folder):
            msg.info(f"\tProcessed started but unfinished - emptying folder")
            shutil.rmtree(write_folder)

        with mp.Pool(n_process) as p:
            counts = p.map(process, paths_)
        domain, timestamp = list(zip(*counts))

        with open(os.path.join(write_folder, "domain_counts.json"), "w") as f:
            json.dump(domain, f)
        with open(os.path.join(write_folder, "timestamp_counts.json"), "w") as f:
            json.dump(timestamp, f)

        with open(os.path.join(write_folder, "timestamp_counts.json"), "w") as f:
            json.dump(timestamp, f)

        # create success file
        open(s_path, "a").close()


# def parse_arguments():
#    args =

if __name__ == "__main__":
    main()
