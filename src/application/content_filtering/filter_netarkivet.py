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


def main(read_path, write_path, filters: dict, n_process: int = 32):
    for name, filter_ in filters:
        process(
            read_path,
            write_path,
            filer_name=name,
            add_filter_column=filter_,
            n_process=n_process,
            ignore_processing=False,
        )


def process(
    read_path: str,
    filter_name: str,
    add_filter_column: Callable,
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
        write_folder = os.path.join(read_path, year)
        Path(write_folder).mkdir(parents=True, exist_ok=True)
        path = os.path.join(write_folder, os.path.split(__file__)[-1])

        # create processing file
        p_path = os.path.join(path + "__PROCESS")
        if os.path.isfile(p_path) and ignore_processing is False:
            msg.info("\t Folder is being processed - skipping")
        open(p_path, "a").close()

        with mp.Pool(n_process) as p:
            p.map(add_filter_column, paths_)

        # create success file
        s_path = os.path.join(path + "_" + filter_name + "__SUCCESS")
        open(s_path, "a").close()
        os.remove(p_path)


def quality_filter(df_path):
    """
    Applies quality filter to the text column of a dataframe and them
    """
    df = pd.read_parquet(df_path, engine="pyarrow")

    # filter df
    conditional = df["language"].isin({"da"})

    df["quality"] = None
    texts = df["text"][conditional]

    qf = QualityFilter()
    df["quality_filter"][conditional] = qf.filter_describe(texts)
    df.to_parquet(df_path, engine="pyarrow")


def domain_filter(
    df_path,
    DNS_unsafe_domains_path: Optional[str] = None,
    safebrowsing_unsafe_domains_path: Optional[str] = None,
):
    """
    Applies quality filter to the text column of a dataframe and them
    """
    if DNS_unsafe_domains_path is None:
        path = os.path.join("/work", "netarkivet_cleaned", "")
        with open(path, "r") as f:
            DNS_f_unsafe_domains = f.read()
    if safebrowsing_unsafe_domains_path is None:
        path = os.path.join("/work", "netarkivet_cleaned", "")
        with open(path, "r") as f:
            sb_domains = f.read()

    df = pd.read_parquet(df_path, engine="pyarrow")

    # filter df
    conditional = df["language"].isin({"da"})

    # TODO read in domains lists

    df["DNS_filter"] = None
    df["SafeBrowsning_filter"] = None
    df["DNS_filter"][conditional] = df["domains"][conditional].isin(
        DNS_f_unsafe_domains
    )
    df["SafeBrowsing_filter"][conditional] = df["domains"][conditional].isin(sb_domains)
    df.to_parquet(df_path, engine="pyarrow")


if __name__ == "__main__":
    read_path = os.path.join("/work", "netarkivet-cleaned")

    filters = [{"quality": quality_filter, "domain_filter": domain_filter}, ""]
    main(read_path)
