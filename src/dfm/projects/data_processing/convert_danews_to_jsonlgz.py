"""
Converts infomedia to a .jsonl.gz file with the format:

{
    "id": "...",             # MANDATORY: source-specific identifier
    "text": "foo",           # MANDATORY: textual content of the document
    "source": "...",         # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
    "added": "...",          # OPTIONAL: timestamp ai2 acquired this data
    "created": "..."         # OPTIONAL: timestamp when orig document was created (best-guess if not available)
    "metadata": {...}        # OPTIONAL: source-specific metadata
}
"""

from pathlib import Path
from typing import Any

from datasets import Dataset, load_dataset  # type: ignore


def create_text(example: dict[str, Any]) -> dict[str, Any]:
    """
    create the full text from the different text fields
    """
    text: str = ""
    text += f"# {example['Heading']}\n\n"
    if example["SubHeading"]:
        text += f"## {example['SubHeading']}\n\n"

    if example["Lead"]:
        text += example["Lead"] + "\n"  # type: ignore
    text += example["BodyText"] + "\n"  # type: ignore
    text = text.strip()  # type: ignore

    example["text"] = text
    return example  # type: ignore


def create_metadata(example: dict[str, Any]) -> dict[str, Any]:
    """
    create the metadata from the different fields
    """

    metadata = {
        "article_url": example["ArticleUrl"],
        "authors": example["Authors"],
        "source": example["Source"],
        "word_count": example["WordCount"],
        "page_ids": example["PageIds"],
        "section": example["Section"],
    }
    example["metadata"] = metadata
    return example


def reformat_dataset(ds: Dataset, num_proc: int = 8) -> Dataset:
    ds = ds.map(create_text, num_proc=num_proc)  # type: ignore
    ds = ds.map(lambda x: {"source": "infomedia"}, num_proc=num_proc)  # type: ignore # noqa: ARG005
    ds = ds.map(lambda x: {"added": "2022-10-24"}, num_proc=num_proc)  # type: ignore # noqa: ARG005
    ds = ds.map(create_metadata, num_proc=num_proc)  # type: ignore
    ds = ds.map(lambda x: {"id": x["ArticleId"]}, num_proc=num_proc)  # type: ignore
    ds = ds.map(lambda x: {"created": x["PublishDate"]}, num_proc=num_proc)  # type: ignore

    # remove unnecessary columns
    ds = ds.remove_columns(
        [
            "ArticleUrl",
            "Heading",
            "SubHeading",
            "Lead",
            "Paragraph",
            "PublishDate",
            "BodyText",
            "Captions",
            "Authors",
            "Source",
            "WordCount",
            "ArticleId",
            "PageIds",
            "Section",
        ],
    )
    return ds


def main():
    path = Path("/work/845878/raw_datasets/hope-infomedia/yearly")
    files = [str(p) for p in path.glob("*.ndjson")]
    save_path = "dfm-data/v3.0.0/danews/data.jsonl.gz"

    ds: Dataset = load_dataset("json", data_files=files, split="train")  # type: ignore
    # current keys are:
    # dict_keys(['ArticleUrl', 'Heading', 'SubHeading', 'Lead', 'Paragraph', 'PublishDate', 'BodyText', 'Captions', 'Authors', 'Source', 'WordCount', 'ArticleId', 'PageIds', 'Section'])  # noqa

    # ids in file are not are not unique -->
    # create new id:
    ids = list(range(len(ds)))
    ds = ds.add_column("id", ids)  # type: ignore

    # reformat dataset
    ds = reformat_dataset(ds)  # type: ignore

    # save
    ds.to_json(  # type: ignore
        save_path,
        orient="records",
        lines=True,
        compression="gzip",
    )


if __name__ == "__main__":
    main()
