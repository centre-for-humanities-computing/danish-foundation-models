"""This script converts the raw Netarkivet data to the jsonl.gz format that
Dolma expects"""

import gzip
import json
from collections.abc import Generator
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


def convert_nat_to_standard_format(nat_df: pl.LazyFrame, year: str) -> list[NatEntry]:
    """Convert Netarkivet entries to the standard format:
        {
    "id": "...",             # MANDATORY: source-specific identifier
    "text": "foo",           # MANDATORY: textual content of the document
    "source": "...",         # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
    "added": "...",          # OPTIONAL: timestamp we acquired this data (time file was created), specified as YYYY-MM-DDTHH:MM:SS.TIMEZONE e.g 2021-04-13T12:52:46.000Z
    "created": "..."         # OPTIONAL: timestamp when orig document was created (best-guess if not available), should be specified as a range; "YYYY-MM-DDTHH:MM:SS.TIMEZONE, YYYY-MM-DDTHH:MM:SS.TIMEZONE"
    "metadata": {            # OPTIONAL: source-specific metadata
            "sub-source": "...", # OPTIONAL: E.g. "newspaper_ocr"
            ...
            }
    }
    Handles conversion of the timestamp format and adds 'domain_key'
    (main domain, e.g. 'dr.dk') and 'uri' (full url) to metadata along with the
    year of the scrape as sub-source
    """
    return (
        nat_df.select(
            pl.col("sha1").alias("id"),
            pl.col("content").alias("text"),
            pl.col("timestamp")
            .str.strptime(dtype=pl.Datetime, format="%Y%m%d%H%M%S")
            .dt.strftime("%Y-%m-%d %H:%M:%S.000Z, %Y-%m-%d %H:%M:%S.000Z")
            .alias("created"),
            pl.lit("NAT").alias("source"),
            pl.lit("2017-01-01 00:00:00.000Z").alias("added"),
            pl.struct(pl.col("domain_key"), pl.col("uri")).alias("metadata"),
            pl.lit(year).alias("sub-source"),
        )
        .with_columns(
            pl.col("timestamp"),
        )
        .collect()
        .to_dicts()
    )


def main(save_dir: Path) -> None:
    for path in get_nat_paths():
        print(f"Processing {path}")
        year = path.parent.name.split("_")[0]
        part_id = path.with_suffix("").with_suffix(
            "",
        )  # call twice to remove both .parquet and .snappy
        save_path = save_dir / year / part_id
        save_path.parent.mkdir(parents=True, exist_ok=True)

        data = lazyframe_from_parquet(path)
        processed = convert_nat_to_standard_format(data, year=year)

        with gzip.open(save_path.with_suffix(".jsonl.gz"), "wt") as f:
            for entry in processed:
                f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    base_save_dir = Path("/work/dfm-data/v3.0.0/nat/documents")
    main(base_save_dir)
