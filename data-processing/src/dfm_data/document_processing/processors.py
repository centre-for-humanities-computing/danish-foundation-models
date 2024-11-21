"""This module contains processing methods for extracting text from various documents."""

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

from docling.datamodel.document import TableItem, TextItem
from extract_msg import openMsg
from loguru import logger
from pypandoc import convert_file
from trafilatura import extract as extract_html_text

from .utils import (
    build_document_converter,
    build_metadata,
    create_JSONL,
    find_near_duplicates,
    generate_decode_url,
    make_unique,
    remove_newlines,
)

if TYPE_CHECKING:
    import pandas as pd


def process_msg(file_path: Path, source: str, **kwargs: dict[str, Any]) -> str:  # noqa: ARG001
    """Read a single MSG file and build a JSONL object. Uses Trafilatura for the extraction.

    Args:
        file_path: Path to the HTML file
        source: What is the data source (most likely DSK client)
        **kwargs: Additional arguments

    Returns:
        str: JSONL line with the file content
    """

    def replace_url(match: re.Match) -> str:
        url = match.group(0)
        decoded_url = generate_decode_url(url)
        if decoded_url:
            return decoded_url
        return url

    text = openMsg(file_path).body
    text = re.sub(r"(\n\s)+", "\n", text)
    text = re.sub(r"\[.+?\]", "", text)
    text = text.replace("\r", "")
    text = re.sub(r"https?://[^>]+", replace_url, text)
    metadata = build_metadata(file_path)
    return json.dumps(asdict(create_JSONL(text, source, metadata)), ensure_ascii=False)


def process_html(file_path: Path, source: str, **kwargs: dict[str, Any]) -> str:  # noqa: ARG001
    """Read a single HTML file and build a JSONL object. Uses Trafilatura for the extraction.

    Args:
        file_path: Path to the HTML file
        source: What is the data source (most likely DSK client)
        **kwargs: Additional arguments

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
        file_path: Path to the EPUB file
        source: What is the data source (most likely DSK client)
        **kwargs: Additional arguments

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
        file_path: Path to the TXT file
        source: What is the data source (most likely DSK client)
        **kwargs: Additional arguments

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
        file: Path to the input file.
        source: Source identifier for the data.
        **kwargs: Extra arguments

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


def process_file(file: Path, dsk_client: str, **kwargs: dict) -> str | None:
    """Generic method for processing a file. Will find the file type and use the right processing method.

    Args:
        file: Path to the file to process
        dsk_client: What DSK client have delivered the file
        **kwargs: Extra arguments

    Returns:
        str | None: Returns a JSONL line if the file type is supported, else None.
    """
    if file.is_dir():
        return None

    suffix = file.suffix
    method = {
        ".pdf": process_document,
        ".html": process_html,
        ".docx": process_document,
        ".epub": process_epub,
        ".txt": process_txt,
        ".pptx": process_document,
        ".md": process_document,
        ".msg": process_msg,
    }.get(suffix)

    if not method:
        logger.warning(f"Unsupported file type: {suffix} - for file: {file!s}")
        return None

    return method(file, dsk_client, **kwargs)