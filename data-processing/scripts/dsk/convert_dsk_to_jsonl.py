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

import gzip
from pathlib import Path
from typing import TYPE_CHECKING

from joblib import Parallel, delayed
from tqdm import tqdm
from typer import Typer

from dfm_data.document_processing.processors import process_file
from dfm_data.document_processing.utils import (
    build_document_converter,
)

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
    files = list(top_level_path.glob("**/*.*"))

    save_file = output_path
    if "".join(output_path.suffixes) != ".jsonl.gz":
        save_file = output_path / (dsk_client + output_suffix)

    converter = build_document_converter()
    parallel = Parallel(n_jobs=n_workers, return_as="generator_unordered")
    save_file.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(save_file, mode="wb") as out_file:
        # with (output_path / output_name).open("w+") as out_file:
        for doc in parallel(
            delayed(process_file)(file, dsk_client, converter=converter)
            for file in tqdm(files)
        ):
            if doc is None:
                continue
            out_file.write(f"{doc}\n".encode())


if __name__ == "__main__":
    APP()
