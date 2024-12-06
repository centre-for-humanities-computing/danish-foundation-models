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
import io
import itertools
import json
import logging
import zipfile
from collections.abc import Generator
from datetime import date, datetime
from pathlib import Path
from typing import TextIO

import requests
from dfm_data.document_processing.processors import process_file
from typer import Typer

APP = Typer(name="Cellar CLI")


# Match available formats to the preference order
def ordered_match(options: list[str]) -> list[str]:
    # Preferred file types order
    preference = {
        "txt",
        "html",
        "xhtml",
        "epub",
        "docx",
        "doc",
        "pdf",
        "pdf1x",
        "pdfa1a",
        "pdfa1b",
        "pdfa2a",
        "pdfx",
        "pdfx4",
        "fmx4",
        "xml",
        "RDF/XML",
        "mobi",
    }
    opts = set(options)
    return [p for p in preference if p in opts]


def process_documents(lang: str, docs: list[dict], path: Path):
    """
    Process a list of documents and save the results in a compressed file.

    Args:
        lang: The language to fetch the document for.
        docs: A list of dictionaries representing the documents to process. Each dictionary must contain at least a "work" key with the URI of the document, and a "type" key with a list of available formats.
        path: The path where the compressed file will be saved.
    """
    logging.info(f"{path} - {len(docs)}")
    with gzip.open(
        path,
        "wt",
        encoding="utf-8",
    ) as gzfile, requests.Session() as session:
        for doc in docs:
            uri = doc["work"]
            types = doc["type"]
            name = uri.split("/")[-1]
            logging.info(f"Ingesting {uri}")

            # Fetch document content in the preferred format for each language
            if not fetch_and_process_doc(lang, gzfile, session, uri, types, name):
                logging.warning(f"No valid format for {uri} {lang}")


def fetch_and_process_doc(
    lang: str,
    gzfile: TextIO,
    session: requests.Session,
    uri: str,
    types: list[str],
    name: str,
) -> bool:
    """
    Fetch and process a document in the preferred format.

    Args:
        lang: The language to fetch the document for.
        gzfile: A text file where the processed content will be written.
        session: An instance of `requests.Session` that is used to make HTTP requests.
        uri: The URI of the document.
        types: A list of available formats for the document.
        name: The name of the document.

    Returns:
        True if the document was successfully fetched and processed, False otherwise.
    """
    for mtype in ordered_match(types):
        header = {
            "accept": f"application/zip;mtype={mtype}",
            "accept-language": lang.lower(),
        }
        response = session.get(uri, headers=header)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                process_zip_content(gzfile, f"Cellar-{lang}-{name}", z)
            return True
    return False


def process_zip_content(gzfile: TextIO, name: str, z: zipfile.ZipFile):
    """
    Process the contents of a ZIP file and write the processed text to a gzip file.

    Args:
        gzfile: A text file where the processed content will be written.
        name: The name of the document being processed.
        z: An instance of `zipfile.ZipFile` containing the contents of the ZIP file.
    """
    for zip_info in z.infolist():
        with z.open(zip_info) as file:
            text = process_file(file, name)
            if text:
                gzfile.write(text + "\n")


# Group documents by date
def get_groups(infile: Path) -> Generator[tuple[tuple[str, date], itertools.groupby]]:
    """
    Generate groups of documents based on language and date.

    Args:
        infile: The path to the input file containing document data in JSON format.

    Yields:
        A tuple containing a key (language, date) and a group of documents that match the key.
    """

    def get_group(doc: dict) -> tuple[str, date]:
        return (doc["language"], datetime.fromisoformat(doc["timestamp"]).date())

    with infile.open() as handle:
        docs = (json.loads(line) for line in handle)
        docs = sorted(docs, key=get_group)
        yield from itertools.groupby(docs, get_group)


@APP.command(
    name="process_cellar",
    help="Process documents and save the results in a compressed file.",
)
def main(infile: Path, outdir: Path):
    """
    Process documents from the given input file and save the results in compressed JSONL files.

    Args:
        infile: The path to the input file containing document metadata.
        outdir: The directory where the compressed JSONL files will be saved.
    """
    logging.basicConfig(level=logging.INFO)

    for group in get_groups(infile):
        (lang, date), docs = group
        path = outdir / f"{lang}-{date.year}-{date.month}-{date.day}.jsonl.gz"

        if path.exists():
            logging.warning(f"{path} already exists! Skipping")
            continue

        path.parent.mkdir(parents=True, exist_ok=True)

        process_documents(lang, list(docs), path)


# Main script execution
if __name__ == "__main__":
    APP()
