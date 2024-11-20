"""This module contains utilities for extracting text from documents."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Union

import pandas as pd
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline

pd.options.mode.chained_assignment = None


def build_document_converter() -> DocumentConverter:
    """Create a Docling `DocumentConverter` instance. Used to convert PDF, DOCX and, PPTX.

    Returns:
        DocumentConverter: THe `DocumentConverter` instance
    """
    # previous `PipelineOptions` is now `PdfPipelineOptions`
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = False
    pipeline_options.table_structure_options.mode = TableFormerMode.FAST
    # ...

    ## Custom options are now defined per format.
    doc_converter = DocumentConverter(  # all of the below is optional, has internal defaults.
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.MD,
            InputFormat.DOCX,
            InputFormat.HTML,
            InputFormat.PPTX,
            InputFormat.ASCIIDOC,
        ],  # whitelist formats, non-matching files are ignored.
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,  # pipeline options go here.
                backend=PyPdfiumDocumentBackend,  # optional: pick an alternative backend
            ),
            InputFormat.DOCX: WordFormatOption(
                pipeline_cls=SimplePipeline,  # default for office formats and HTML
            ),
        },
    )
    return doc_converter


@dataclass
class JSONL:
    id: str
    text: str
    source: str
    added: str
    created: str
    metadata: dict[str, Any]


def create_JSONL(text: str, source: str, metadata: dict[str, Any]) -> JSONL:
    """Helper method to create a JSONL dataclass instance.

    Args:
        text: The text that should be part of the object
        source: The source of the text
        metadata: Metadata surrounding the text (e.g. filename, filetype, etc.)

    Returns:
        JSONL: The JSONL dataclass instance.
    """
    id_ = f"{source}-{metadata.get('filename', '')}".replace(" ", "-")
    jsonl = JSONL(
        id=id_,
        text=text,
        source=source,
        added=str(datetime.now()),
        created=f"{datetime(2000, 1, 1)!s}, {datetime.now()!s}",
        metadata=metadata,
    )
    return jsonl


def build_metadata(document: Union[InputDocument, Path]) -> dict:
    """Helper function to build metadata from an input file.

    Args:
        document: The document/file to build metadata from.

    Returns:
        dict: A dictionary containing the metadata.
    """
    if isinstance(document, InputDocument):
        file_path = document.file
        filename = document.file.name
        filetype = document.format.name
        filesize = document.filesize
        page_count = document.page_count
    else:
        file_path = document
        filename = document.name
        filetype = "".join(document.suffixes)
        filesize = document.stat().st_size
        page_count = 0

    metadata = {
        "filename": filename,
        "filetype": filetype,
        "filesize": filesize,
        "page_count": page_count,
        "file_path": str(file_path),
    }

    return metadata


def find_near_duplicates(
    df: pd.DataFrame,
    threshold: float = 0.9,
) -> list[tuple]:
    """
    Finds pairs of columns in a DataFrame that are near-duplicates,
    based on a specified threshold of identical values.

    Args:
      df: The DataFrame to check.
      threshold: The minimum proportion of identical values to consider a pair of columns as near-duplicates.

    Returns:
      A list of tuples, where each tuple contains the names of two near-duplicate columns.
    """

    near_duplicates = []
    for i in range(len(df.columns)):
        for j in range(i + 1, len(df.columns)):
            if (df.iloc[:, i] == df.iloc[:, j]).mean() >= threshold:
                near_duplicates.append((df.columns[i], df.columns[j]))
    return near_duplicates


def find_text_keys(data: dict, prefix: str = ""):
    """Recursively finds all keys named 'text' in a JSON object and yields their full paths.

    Args:
      data: The JSON object to search.
      prefix: The prefix to be added to the path.

    Yields:
      The full paths to the 'text' keys.
    """

    if isinstance(data, dict):
        for key, value in data.items():
            if key == "text":
                yield prefix + key
            else:
                yield from find_text_keys(value, prefix + key + ".")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            yield from find_text_keys(item, prefix + str(i) + ".")


def extract_text_values(data: dict, paths: list[str]) -> list[str]:
    """Extracts text values from a JSON object using given paths.

    Args:
      data: The JSON object.
      paths: A list of paths to the 'text' keys.

    Returns:
      A list of extracted text values.
    """

    text_values = []
    for path in paths:
        value = data
        for key in path.split("."):
            try:
                k = int(key)
            except ValueError:
                k = key
            value = value[k]

        if value not in text_values and value != "":
            text_values.append(value)

    return text_values


def remove_newlines(df: pd.DataFrame) -> pd.DataFrame:
    """Removes newline characters from all string columns in a DataFrame.

    Args:
        df: The DataFrame to process.

    Returns:
        The DataFrame with newlines removed from string columns.
    """

    # Identify string columns
    string_cols = df.select_dtypes(include=["object", "string"]).columns
    # Remove newlines from string columns
    for col in string_cols:
        df[col] = df[col].astype(str).str.replace("\n", "", regex=False)

    return df


# Function to rename columns with unique suffixes
def make_unique(column_name: str, column_counts: dict[str, int]) -> str:
    """Method to rename duplicate column name

    Args:
        column_name (str): Name of the column
        column_counts (dict[str, int]): Number of times we have seen this column name

    Returns:
        str: The new column name
    """
    if column_name in column_counts:
        # Increment count and append the new suffix
        column_counts[column_name] += 1
        return f"{column_name}_{column_counts[column_name]}"
    # Initialize count for the first occurrence
    column_counts[column_name] = 0
    return column_name
