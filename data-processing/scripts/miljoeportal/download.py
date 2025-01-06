"""Script to fetch a list of all documents available in the Milloeportal"""

import gzip
import json
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import requests
import tqdm
from dfm_data.document_processing.processors import process_file
from loguru import logger
from requests import Response
from typer import Exit, Typer

APP = Typer(name="Miljoeportalen")


def catalog(path: Path) -> bool:
    """Pull a list of all assessments.

    Args:
        path: Path to save results.

    Returns:
       If the pull was succesful or not.
    """
    url = "https://eahub.miljoeportal.dk/api/assessments/search"

    headers: dict[str, str] = {"Content-Type": "application/json"}

    body: dict[str, str] = {"assessmentType": "All"}

    res: Response = requests.post(url, json=body, headers=headers)

    if res.status_code == 200:
        assessments = res.json()
        logger.info(f"Fetched {len(assessments)} from Miljøportalen.")
        with (path / "result.json").open("w") as output:
            json.dump(
                [doc["id"] for doc in res.json()],
                output,
                indent=4,
                ensure_ascii=False,
            )
        return True

    logger.error(f"Searching content failed: {res.status_code} - {res.text}")
    return False


def download_files(file_path: Path, id_: str) -> list[str]:
    """Download and extract files

    Args:
        file_path (Path): Path to where to save raw files
        id_ (str): ID of the assessment to download

    """
    url = "https://eahub.miljoeportal.dk/api/assessments/{assessment}/download"
    res: Response = requests.get(url.format(assessment=id_))
    body: str | json.Any = res.content.decode("utf-8").lstrip('"').rstrip('"')
    response: Response = requests.get(body)
    texts = []
    with ZipFile(BytesIO(response.content)) as z:
        for zip_info in z.infolist():
            with z.open(zip_info) as file:
                raw_file = file_path / zip_info.filename
                if raw_file.exists():
                    continue
                text: str | None = process_file(file, "Miljoeportalen")
                if text:
                    file.seek(0)
                    raw_file.open("wb").write(file.read())
                    texts.append(text)

    return texts


@APP.command()
def download(raw_data: Path, cleaned: Path, workers: int = 2):
    """Command to download documents from miljoeportalen.

    Args:
        raw_data: Path to save the raw results, i.e. list of assessments that can be downloaded.
        cleaned: Path to save the downloaded and extracted results.
        workers: Number of parallel calls. Defaults to 2.
    """
    raw_data.mkdir(parents=True, exist_ok=True)
    cleaned.mkdir(parents=True, exist_ok=True)

    result: bool = catalog(raw_data)
    if not result:
        raise Exit(2)

    results = json.load((raw_data / "result.json").open())
    with gzip.open((cleaned / "miljoeportal.jsonl.gz"), mode="wb") as gzfile:
        # TODO: parallelize this...
        for result in tqdm.tqdm(results):
            texts: list[str] = download_files(raw_data, result)
            [gzfile.write(f"{line}\n".encode()) for line in texts]


if __name__ == "__main__":
    APP()
