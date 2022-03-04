"""
Filters Netarkivet based on the language tags

Dependent on:
    isn't dependent

Authors:
    Kenneth Enevoldsen
"""
from typing import Callable
import os
import sys

from functools import partial

from pathlib import Path
import shutil

import multiprocessing as mp

import pandas as pd
from wasabi import msg

dfm_path = os.path.join("githubs", "danish-foundation-models")
sys.path.append(dfm_path)

from src.application.content_filter_lang_netarkivet import (
    get_paths,
    split_mult_extension,
)


def filter_df(df, lang_codes):
    return df[df["language"].isin(lang_codes)]


def filter_copy(path, write_path: str, filter: Callable, clean_code="") -> None:
    folder, fname = os.path.split(path)
    fname_, ext = split_mult_extension(fname)
    fname = fname_ + clean_code + ext
    _, year = os.path.split(folder)
    write_folder = os.path.join(write_path, year)
    write_path_ = os.path.join(write_folder, fname)

    df = pd.read_parquet(path, engine="pyarrow")

    # filter
    df = filter(df)

    # record domains and timestamps
    Path(write_folder).mkdir(parents=True, exist_ok=True)
    df.to_parquet(write_path_, engine="pyarrow")


def main(read_path, write_path, n_process=32, lang_codes={"da"}):
    paths = get_paths(read_path=read_path)
    list(paths.keys())[0]

    msg.info(f"Using {n_process} cores")

    for folder, paths_ in paths.items():
        msg.info(f"Currently processing folder: {folder}")

        _, year = os.path.split(folder)
        write_folder = os.path.join(write_path, year)
        Path(write_folder).mkdir(parents=True, exist_ok=True)
        s_path = os.path.join(write_folder, os.path.split(__file__)[-1] + "__SUCCESS")

        if os.path.isfile(s_path):
            msg.info(f"\tAlready processed - skipping")
        if os.path.isdir(write_folder):
            msg.info(f"\tProcessed started but unfinished - emptying folder")
            shutil.rmtree(write_folder)

        filter_ = partial(filter_df, lang_codes=lang_codes)
        filter_copy_ = partial(filter_copy, filter=filter_, write_path=write_path)

        with mp.Pool(n_process) as p:
            counts = p.map(filter_copy_, paths_)
        domain, timestamp = list(zip(*counts))

        # create success file
        open(s_path, "a").close()


if __name__ == "__main__":
    read_path = os.path.join("/work", "netarchive")
    write_path = os.path.join("/work", "netarkivet-cleaned")

    main(read_path, write_path)
