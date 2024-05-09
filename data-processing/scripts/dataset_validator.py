"""
This CLI tool evaluate whether a datasets adhere to the expected schema.

The tool takes two arguments:
- dataset_folder: Path to the dataset folder. On UCloud this is danish-foundation-models/dfm-data/pre-training
- datasheets_folder: Path to the datasheets folder. On GitHub this is 'danish-foundation-models/docs/datasheets'

The tool will then check following attributes about the datasets in the dataset_folder:

Datasheets:

A datasheet of the same name should be located in the datasheets_folder and should contain the following information:
- License
- Languages

Folder Structure:

The dataset folder should contain one folder per dataset. Each dataset folder should have the following structure:

```
dataset_folder
│
└── dataset_name
    │
    ├── documents
    │   ├── document1.jsonl.gz   # MANDATORY: one or more files containing the documents in the dataset
    │   └── ...
    │
    └── attributes   # OPTIONAL: folder containing annotations from dataset cleaning
```


Schema:

An entry in the dataset should adhere to the Document schema (defined below).

```
{
    "id": "...",                      # MANDATORY: source-specific identifier
    "text": "foo",                    # MANDATORY: textual content of the document
    "source": "...",                  # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
    "added": "...",                   # MANDATORY: timestamp we acquired this data (time file was created), specified as
                                        # YYYY-MM-DD e.g 2021-04-13
    "created": "..."                  # MANDATORY: timestamp when orig document was created (best-guess if not available),
                                         # should be specified as a range;
                                         # "YYYY-MM-DD, YYYY-MM-DD"
    "metadata": {                     # OPTIONAL: source-specific metadata
         ...
     }
}
"""


import argparse
import gzip
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, field_validator
from tqdm import tqdm

logger = logging.getLogger(__name__)


class Document(BaseModel):
    id: str  # noqa
    text: str
    source: str
    added: str
    created: str
    metadata: dict[str, Any] = {}

    @field_validator("added")
    @classmethod
    def check_timestamp_format(cls, v: str):  # noqa
        if not v:
            raise ValueError("Timestamp 'added' is required.")
        try:
            datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            raise ValueError(
                "Timestamp 'added' should be in the format 'YYYY-MM-DD'.",
            )

    @field_validator("created")
    @classmethod
    def check_created_format(cls, v: str):
        if not v:
            raise ValueError("Timestamp 'created' is required.")
        try:
            start, end = v.split(", ")
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            if start_date > end_date:
                raise ValueError(
                    "Timestamp 'created' should be in the format 'YYYY-MM-DDTHH:MM:SS.TIMEZONE, YYYY-MM-DDTHH:MM:SS.TIMEZONE'.",
                )
        except ValueError as e:
            raise ValueError(
                "Timestamp 'created' should be in the format 'YYYY-MM-DDTHH:MM:SS.TIMEZONE, YYYY-MM-DDTHH:MM:SS.TIMEZONE'. Got additional error:\n"
                + str(e),
            )


def check_first_entry(document_file: Path):
    """
    Get first entry in jsonl.gz file.
    """
    dataset_name = document_file.parent.parent.name
    with gzip.open(document_file, "rb") as f:
        line = f.readline().decode("utf-8")

    json_entry = json.loads(line)
    doc = Document(**json_entry)
    assert (
        doc.source == dataset_name
    ), f"Source should be {dataset_name}, but is {doc.source}"


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset_folder",
        type=str,
        help="Path to the dataset folder. On UCloud this is danish-foundation-models/dfm-data/pre-training",
    )
    parser.add_argument(
        "--datasheets_folder",
        type=str,
        help="Path to the datasheets folder. On GitHub this is 'danish-foundation-models/docs/datasheets'",
    )
    return parser


def convert_to_paths(dataset_folder: str, datasheets_folder: str) -> tuple[Path, Path]:
    _dataset_folder = Path(dataset_folder)
    _datasheets_folder = Path(datasheets_folder)

    if not _dataset_folder.exists():
        raise FileNotFoundError(
            f"Dataset folder {_dataset_folder.resolve()} does not exist.",
        )
    if not _datasheets_folder.exists():
        raise FileNotFoundError(
            f"Datasheets folder {_datasheets_folder.resolve()} does not exist.",
        )

    return _dataset_folder, _datasheets_folder


def check_datasheet(dataset_path: Path, datasheets_path: Path) -> str:
    datasheet_path = datasheets_path / dataset_path.name
    msg = ""

    if not datasheet_path.exists():
        msg += f"Datasheet {datasheet_path.name} does not exist.\n"

    # extract frontmatter from datasheet
    try:
        with datasheet_path.open("r") as f:
            markdown = f.read()
            frontmatter = yaml.safe_load(markdown.split("---")[1])
    except Exception as e:
        msg += f"Error reading datasheet {datasheet_path.name}: {e}\n"
        return msg

    # check if datasheet contains required fields
    required_fields = ["license", "language"]
    missing_fields = [field for field in required_fields if field not in frontmatter]
    if missing_fields:
        msg += f"Datasheet {datasheet_path.name} is missing the following fields: {missing_fields}\n"

    # check license == "other"
    if frontmatter.get("license") == "other":
        # license name should be specified
        if not frontmatter.get("license_name"):
            msg += f"Datasheet {datasheet_path.name} has license 'other' but is missing 'license_name' field\n"

    return msg


def check_folder_structure(dataset_path: Path) -> str:
    msg = ""

    required_folders = ["documents"]
    allowed_folders = ["attributes"]
    subfolders = list(dataset_path.glob("*"))

    for folder in subfolders:
        if folder.is_dir():
            if folder.name not in required_folders + allowed_folders:
                msg += f"Folder {folder.name} is not allowed in dataset {dataset_path.name}\n"
        else:
            msg += f"File {folder.name} is not allowed in dataset {dataset_path.name}\n"
    return msg


def check_schema(dataset_path: Path) -> str:
    msg = ""
    documents_path = dataset_path / "documents"

    if not documents_path.exists():
        msg += f"Folder 'documents' does not exist in dataset {dataset_path.name}\n"

    document_files = list(documents_path.glob("*.jsonl.gz"))
    if not document_files:
        msg += f"Folder 'documents' does not contain any document files in dataset {dataset_path.name}\n"

    n_errors = 3  # only print up to 3 errors
    for document_file in document_files:
        try:
            check_first_entry(document_file)
        except Exception as e:
            n_errors -= 1
            msg += f"Error in document file {document_file.name}: {e}\n"
        if n_errors < 1:
            break

    return msg


def check_datasets(dataset_folder: str, datasheets_folder: str):
    logger.info(
        f"Checking datasets in {dataset_folder} against datasheets in {datasheets_folder}.",
    )

    datasets_path, datasheets_path = convert_to_paths(dataset_folder, datasheets_folder)
    datasets = list(datasets_path.glob("*"))

    failed_datasets: list[str] = []

    pbar = tqdm(datasets)

    for dataset_path in pbar:
        # update progress bar description
        pbar.set_description(f"Checking dataset: {dataset_path.name}")  # type: ignore

        msg = check_datasheet(dataset_path, datasheets_path)
        msg += check_folder_structure(dataset_path)
        msg += check_schema(dataset_path)

        dataset_failed_checks = msg != ""
        if dataset_failed_checks:
            logger.error(
                f"--- Dataset {dataset_path.name} failed validation ------------",
            )
            logger.error(msg)

        if dataset_failed_checks:
            failed_datasets.append(dataset_path.name)

    if failed_datasets:
        logger.error("The following datasets failed validation:")
        logger.error("\n - ".join(failed_datasets))


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    check_datasets(args.dataset_folder, args.datasheets_folder)
