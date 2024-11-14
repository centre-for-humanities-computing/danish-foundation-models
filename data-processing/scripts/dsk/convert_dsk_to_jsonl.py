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
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from joblib import Parallel, delayed
from loguru import logger
from pdfminer.high_level import extract_text as extract_pdf_text
from pypandoc import convert_file
from tqdm import tqdm
from trafilatura import extract as extract_html_text
from typer import Typer
from utils import create_JSONL

APP = Typer(name="2JSONL Converter")


# @APP.command(name="PDF2JSONL", no_args_is_help=True, help="Convert PDF file to JSONL string", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def process_pdf(file_path: Path, source: str, **kwargs: dict[str, Any]) -> str:
    text = extract_pdf_text(file_path)
    text = re.sub(r"(\n\s)+", "\n", text)
    metadata = {**kwargs, "file_path": str(file_path)}
    return json.dumps(asdict(create_JSONL(text, source, metadata)), ensure_ascii=False)


# @APP.command(name="DOCX2JSONL", no_args_is_help=True, help="Convert DOCX file to JSONL string", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def process_docx(file_path: Path, source: str, **kwargs: dict[str, Any]) -> str:
    text = convert_file(file_path, to="plain", format="docx")
    text = re.sub(r"(\n\s)+", "\n", text)
    metadata = {**kwargs, "file_path": str(file_path)}
    return json.dumps(asdict(create_JSONL(text, source, metadata)), ensure_ascii=False)


# @APP.command(name="HTML2JSONL", no_args_is_help=True, help="Convert HTML file to JSONL string", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def process_html(file_path: Path, source: str, **kwargs: dict[str, Any]) -> str:
    text = extract_html_text(file_path.read_text())
    text = re.sub(r"(\n\s)+", "\n", text)
    metadata = {**kwargs, "file_path": str(file_path)}
    return json.dumps(asdict(create_JSONL(text, source, metadata)), ensure_ascii=False)


# @APP.command(name="EPUB2JSONL", no_args_is_help=True, help="Convert EPUB file to JSONL string", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def process_epub(file_path: Path, source: str, **kwargs: dict[str, Any]) -> str:
    text = convert_file(file_path, to="plain", format="epub")
    text = re.sub(r"(\n\s)+", "\n", text)
    metadata = {**kwargs, "file_path": str(file_path)}
    return json.dumps(asdict(create_JSONL(text, source, metadata)), ensure_ascii=False)


def process_txt(file_path: Path, source: str, **kwargs: dict[str, Any]) -> str:
    text = file_path.read_text()
    text = re.sub(r"(\n\s)+", "\n", text)
    metadata = {**kwargs, "file_path": str(file_path)}
    return json.dumps(asdict(create_JSONL(text, source, metadata)), ensure_ascii=False)


SUFFIX2METHOD = {
    ".pdf": process_pdf,
    ".html": process_html,
    ".docx": process_docx,
    ".epub": process_epub,
    ".txt": process_txt,
}


@APP.command(name="process_file", help="Process a single file, returning a json string")
def process_file(file: Path, dsk_client: str) -> str | None:
    if file.is_dir():
        return None

    suffix = file.suffix
    name = file.name
    method = SUFFIX2METHOD.get(suffix)

    if not method:
        logger.warning(f"Unsupported file type: {suffix} - for file: {file!s}")
        return None

    return method(file, dsk_client, file_type=suffix, filename=name)


@APP.command(
    name="process_directory",
    help="Crawl a directory and process files of different types",
)
def craw_directory(
    top_level_path: Path,
    output_path: Path,
    dsk_client: str,
    output_name: str = "1.jsonl.gz",
    n_workers: int = 2,
):
    files = top_level_path.glob("**/*")

    parallel = Parallel(n_jobs=n_workers, return_as="generator_unordered")
    output_path.mkdir(parents=True, exist_ok=True)
    with gzip.open(output_path / output_name, mode="wb") as out_file:
        # with (output_path / output_name).open("w+") as out_file:
        for doc in parallel(
            delayed(process_file)(file, dsk_client) for file in tqdm(files)
        ):
            if doc is None:
                continue
            out_file.write(f"{doc}\n".encode())


if __name__ == "__main__":
    APP()
