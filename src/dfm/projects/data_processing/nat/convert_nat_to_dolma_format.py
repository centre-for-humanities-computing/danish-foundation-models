"""This script converts the raw Netarkivet data to the jsonl.gz format that
Dolma expects"""

import gzip
import json
import os
from collections.abc import Generator, Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

import polars as pl

NatEntry = dict[str, Any]


def lazyframe_from_parquet(path: Path) -> pl.LazyFrame:
    return pl.scan_parquet(path)


def get_nat_paths() -> Generator[Path, None, None]:
    folder = Path("/work/netarchive")
    year_subfolders = folder.glob("*.parquet")
    for year_subfolder in year_subfolders:
        yield from year_subfolder.glob("*.parquet")
        # for file in year_subfolder.glob("*.parquet"):
        #    yield file


def convert_nat_to_standard_format(nat_df: pl.LazyFrame) -> list[NatEntry]:
    """Convert Netarkivet entries to the standard format:
        {
        "id": "...",             # MANDATORY: source-specific identifier
        "text": "foo",           # MANDATORY: textual content of the document
        "source": "...",         # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
        "added": "...",          # OPTIONAL: timestamp ai2 acquired this data
        "created": "..."         # OPTIONAL: timestamp when orig document was created (best-guess if not available)
        "metadata": {...}        # OPTIONAL: source-specific metadata
    }
        Handles conversion of the timestamp format
    """
    nat_df = nat_df.select(
        pl.col("sha1").alias("id"),
        pl.col("content").alias("text"),
        pl.col("timestamp")
        .str.strptime(dtype=pl.Datetime, format="%Y%m%d%H%M%S")
        .dt.strftime("%Y-%m-%d %H:%M:%S.000Z")
        .alias("created"),
        pl.lit("NAT").alias("source"),
        pl.lit("2017-01-01 00:00:00.000Z").alias("added"),
        pl.struct(pl.col("domain_key"), pl.col("uri")).alias("metadata"),
    ).collect()
    return nat_df.to_dicts()


BASE_SAVE_DIR = Path("/work/dfm-data/v3.0.0/nat/documents")

if __name__ == "__main__":
    for path in get_nat_paths():
        print(f"Processing {path}")
        data = lazyframe_from_parquet(path)
        processed = convert_nat_to_standard_format(data)

        year = path.parent.name.split("_")[0]
        part_id = path.with_suffix("").with_suffix(
            ""
        )  # call twice to remove both .parquet and .snappy
        save_path = BASE_SAVE_DIR / year / part_id
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with gzip.open(save_path.with_suffix(".jsonl.gz"), "wt") as f:
            for entry in processed:
                f.write(json.dumps(entry) + "\n")
