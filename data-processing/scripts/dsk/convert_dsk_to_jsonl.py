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
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

from docling.datamodel.document import TableItem, TextItem
from joblib import Parallel, delayed
from loguru import logger
from pdfminer.high_level import extract_text as extract_pdf_text
from pypandoc import convert_file
from tqdm import tqdm
from trafilatura import extract as extract_html_text
from typer import Typer

from dfm_data.utils import (
    build_document_converter,
    build_metadata,
    create_JSONL,
    find_near_duplicates,
    make_unique,
    remove_newlines,
)

if TYPE_CHECKING:
    import pandas as pd

APP = Typer(name="2JSONL Converter")


def process_html(file_path: Path, source: str, **kwargs: dict[str, Any]) -> str:  # noqa: ARG001
    """Read a single HTML file and build a JSONL object. Uses Trafilatura for the extraction.

    Args:
        file_path (Path): Path to the HTML file
        source (str): What is the data source (most likely DSK client)
        **kwargs (dict): Additional arguments

    Returns:
        str: JSONL line with the file content
    """
    text = extract_html_text(file_path.read_text())
    text = re.sub(r"(\n\s)+", "\n", text)
    metadata = build_metadata(file_path)
    return json.dumps(asdict(create_JSONL(text, source, metadata)), ensure_ascii=False)


def process_epub(file_path: Path, source: str, **kwargs: dict[str, Any]) -> str:  # noqa: ARG001
    """Read a single EPUB file and build a JSONL object. Uses Pypandoc for the extraction.

    Args:
        file_path (Path): Path to the EPUB file
        source (str): What is the data source (most likely DSK client)
        **kwargs (dict): Additional arguments

    Returns:
        str: JSONL line with the file content
    """
    text = convert_file(file_path, to="plain", format="epub")
    text = re.sub(r"(\n\s)+", "\n", text)
    metadata = build_metadata(file_path)
    return json.dumps(asdict(create_JSONL(text, source, metadata)), ensure_ascii=False)


def process_txt(file_path: Path, source: str, **kwargs: dict[str, Any]) -> str:  # noqa: ARG001
    """Read a single TXT file and build a JSONL object

    Args:
        file_path (Path): Path to the TXT file
        source (str): What is the data source (most likely DSK client)
        **kwargs (dict): Additional arguments

    Returns:
        str: JSONL line with the file content
    """
    text = file_path.read_text()
    text = re.sub(r"(\n\s)+", "\n", text)
    metadata = build_metadata(file_path)
    return json.dumps(asdict(create_JSONL(text, source, metadata)), ensure_ascii=False)


def process_document(
    file: Path,
    source: str,
    **kwargs: dict[str, Any],
) -> str | None:
    """
    Process a single file, converting it into a JSONL string.

    Args:
        file (Path): Path to the input file.
        source (str): Source identifier for the data.
        **kwargs (dict): Extra arguments

    Returns:
        str | None: JSONL string if the file is processed successfully, else None.
    """
    doc_converter = kwargs.get("converter", build_document_converter())
    try:
        result = doc_converter.convert(file)

        metadata = build_metadata(result.input)

        file_content = ""
        # Iterate the elements in reading order, including hierarchy level
        for item, _ in result.document.iterate_items():
            if isinstance(item, TextItem):
                if item.text.strip():
                    file_content += item.text
            elif isinstance(item, TableItem):
                table_df: pd.DataFrame = item.export_to_dataframe()
                dups = find_near_duplicates(table_df, 0.8)
                column_counts = {}
                table_df.columns = [
                    make_unique(col, column_counts) for col in table_df.columns
                ]
                columns_to_keep = table_df.columns.copy(deep=True)
                for pair in dups:
                    if pair[1] in columns_to_keep:
                        columns_to_keep = columns_to_keep.drop(pair[1])

                df_cleaned = table_df[list(columns_to_keep)]
                df_cleaned = remove_newlines(df_cleaned)
                file_content += df_cleaned.to_markdown(index=False, tablefmt="github")
            file_content += "\n\n"

        # Create and return JSONL entry
        return json.dumps(
            asdict(create_JSONL(file_content, source, metadata)),
            ensure_ascii=False,
        )
    except Exception as e:
        logger.error(f"Failed to process file {file}: {e}")
        return None


SUFFIX2METHOD = {
    ".pdf": process_document,
    ".html": process_html,
    ".docx": process_document,
    ".epub": process_epub,
    ".txt": process_txt,
    ".pptx": process_document,
    ".md": process_document,
}


def process_file(file: Path, dsk_client: str, **kwargs: dict) -> str | None:
    if file.is_dir():
        return None

    suffix = file.suffix
    method = SUFFIX2METHOD.get(suffix)

    if not method:
        logger.warning(f"Unsupported file type: {suffix} - for file: {file!s}")
        return None

    return method(file, dsk_client, **kwargs)


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
