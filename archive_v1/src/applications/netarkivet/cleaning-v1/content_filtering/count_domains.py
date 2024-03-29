"""
Counts domains and timestamps on netarkivet based on conditioned on a language tag
derived from https://github.com/optimaize/language-detector

Dependent on:
    isn't dependent

Authors:
    Kenneth Enevoldsen
"""

import json
import multiprocessing as mp
import os
import shutil
from collections import Counter
from pathlib import Path
from typing import Union

import pandas as pd
from wasabi import msg


def get_paths(
    path: str,
    nested: bool = True,
    folder_suffix=".parquet",
    file_suffix=".parquet",
) -> Union[list[str], dict]:
    """extracts paths from netarkivet either in a nested format"""
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


def split_mult_extension(path: str) -> tuple[str, str]:
    """An extension of os.path.splitext which splits extentions until there is none
    left"""
    ext = ""
    while True:
        path_, ext_ = os.path.splitext(path)
        ext = ext_ + ext
        if path == path_:
            return path, ext
        path = path_


def process(path, lang_codes=None):
    """process a single file path, calculating domain counts and timestamps"""
    if lang_codes is None:
        lang_codes = {"da"}
    df = pd.read_parquet(path, engine="pyarrow")

    # filter
    df = df[df["language"].isin(lang_codes)]

    # record domains and timestamps
    domain_counts = Counter(df["domain_key"])
    timestamps = Counter(df["timestamp"].apply(lambda x: x[:8]))

    return domain_counts, timestamps


def main(n_process: int, read_path: str, write_path: str):
    """Applied process to each file obtained using get_paths (all of netarkivet). Write
    {script_name}__SUCCESS file when finished. Will skill already processed folders."""
    paths = get_paths(read_path)
    next(iter(paths.keys()))

    if n_process == -1:
        n_process = mp.cpu_count()

    msg.info(f"Using {n_process} cores")

    for folder, paths_ in paths.items():
        msg.info(f"Currently processing folder: {folder}")

        _, year = os.path.split(folder)
        write_folder = os.path.join(write_path, year)
        Path(write_folder).mkdir(parents=True, exist_ok=True)
        s_path = os.path.join(write_folder, os.path.split(__file__)[-1] + "__SUCCESS")
        if os.path.isfile(s_path):
            msg.info("\tAlready processed - skipping")
        if os.path.isdir(write_folder):
            msg.info("\tProcessed started but unfinished - emptying folder")
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


if __name__ == "__main__":
    read_path = os.path.join("/work", "netarchive")
    write_path = os.path.join("/work", "netarkivet-cleaned")
    main(
        n_process=32,
        read_path=read_path,
        write_path=write_path,
    )
