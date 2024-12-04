"""
Convert from various file formats (pdf, docx, etc.).

To this format:
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
"""

import logging
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from dfm_data.document_processing.processors import process_files
from typer import Typer

if TYPE_CHECKING:
    import pandas as pd

APP = Typer(name="2JSONL Converter")


@APP.command(
    name="process_directory",
    help="Crawl a directory and process files of different types",
)
def crawl_directory(
    top_level_path: Path,
    output_path: Path,
    dsk_client: str,
    output_suffix: str = ".jsonl.gz",
    n_workers: int = 4,
):
    """Process a set of data delivered from a DSK organisation.

    Args:
        top_level_path: Path to a directory with the data delivered by the DSK organization
        output_path: Path to place the processed data
        dsk_client: What DSK organizations pages have been crawled
        output_suffix: What suffix to use. Defaults to ".jsonl.gz".
        n_workers: How many process to run in parallel. Defaults to 4.
    """
    files = list(top_level_path.glob("**/*.*"))

    files = list(filter(lambda x: x.is_file(), files))

    if len(files) == 0:
        logging.error("Something went wrong. No files to process")
        raise typer.Exit(code=1)

    process_files(files, output_path, dsk_client, output_suffix, n_workers)


@APP.command(
    name="process_web_crawl",
    help="Process output from a web crawl",
)
def process_web_crawl(
    path_to_crawl_log: Path,
    output_path: Path,
    data_path: Path,
    dsk_client: str,
    output_suffix: str = ".jsonl.gz",
    n_workers: int = 4,
):
    """Process a set of crawled data from a DSK organisation.

    Args:
        path_to_crawl_log: Path to a log file from the crawl
        output_path: Path to place the processed data
        data_path: Path where the crawled data is located
        dsk_client: What DSK organizations pages have been crawled
        output_suffix: What suffix to use. Defaults to ".jsonl.gz".
        n_workers: How many process to run in parallel. Defaults to 4.
    """
    # Define the command as a list of strings
    command = ["grep", "^--", path_to_crawl_log]
    failed = False
    # Run the command and capture the output
    try:
        result = subprocess.run(command, text=True, capture_output=True, check=True)
        # Filter the third column using Python (equivalent to `awk '{print $3}'`)
        main_folders = {
            line.split()[2].split("/")[2] for line in result.stdout.splitlines()
        }
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with error: {e}")
        failed = True

    if failed:
        raise typer.Exit(code=1)

    files: list[Path] = []
    for main_folder in main_folders:
        if not (data_path / main_folder).exists():
            continue
        files.extend(list((data_path / main_folder).glob("**/*.*")))

    files = list(filter(lambda x: x.is_file(), files))

    if len(files) == 0:
        logging.error("Something went wrong. No files to process")
        raise typer.Exit(code=1)

    process_files(files, output_path, dsk_client, output_suffix, n_workers)


if __name__ == "__main__":
    APP()
