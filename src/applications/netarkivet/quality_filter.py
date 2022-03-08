"""
Filters Netarkivet based on the language tags

Dependent on:
    isn't dependent

Authors:
    Kenneth Enevoldsen
"""
from typing import Callable, Optional
import os
import sys
import shutil
from pathlib import Path
import multiprocessing as mp

import pandas as pd
from wasabi import msg

dfm_path = os.path.join("githubs", "danish-foundation-models")
sys.path.append(dfm_path)

from src.application.count_domains_netarkivet import (
    get_paths,
    split_mult_extension,
)

from src.dfm.cleaning import QualityFilter


def main(
    read_path: str,
    write_path: str,
    n_process: int = 32,
    ignore_processing=False,
) -> None:
    paths = get_paths(read_path=read_path)
    list(paths.keys())[0]

    msg.info(f"Using {n_process} cores")

    for folder, paths_ in paths.items():
        msg.info(f"Currently processing folder: {folder}")

        # create folder path
        _, year = os.path.split(folder)
        write_folder = os.path.join(write_path, year)
        write_folder = Path(write_folder)
        write_folder.mkdir(parents=True, exist_ok=True)
        s_path = os.path.join(write_folder, os.path.basename(__file__)+ "__SUCCESS")

        if os.path.isfile(s_path):
            msg.info("\tAlready processed - skipping")
        if os.path.isdir(write_folder):
            msg.info("\tProcessed started but unfinished - emptying folder")
            shutil.rmtree(write_folder)

        paths_ = [(t, write_folder) for t in paths_]
        with mp.Pool(n_process) as p:
            p.map(quality_filter, paths_)

        # create success file
        open(s_path, "a").close()


def quality_filter(paths):
    """
    Applies quality filter to the text column of a dataframe and them
    """
    df_path, write_folder = paths

    df = pd.read_parquet(df_path, engine="pyarrow")

    # filter df
    conditional = df["language"].isin({"da"})

    #
    df["quality"] = None
    texts = df["text"][conditional]

    qf = QualityFilter()
    df["quality_filter"][conditional] = qf.filter_describe(texts)

    save_path = os.path.join(write_folder, os.path.split(df_path)[-1])
    df.to_parquet(save_path, engine="pyarrow")


if __name__ == "__main__":
    read_path = os.path.join("/work", "netarchive")
    write_path = os.path.join("/work", "netarkivet-cleaned")

    main(read_path, write_path)