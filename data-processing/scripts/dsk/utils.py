from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd


@dataclass
class JSONL:
    id: str
    text: str
    source: str
    added: str
    created: str
    metadata: dict[str, Any]


def create_JSONL(text: str, source: str, metadata: dict[str, Any]) -> JSONL:
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
