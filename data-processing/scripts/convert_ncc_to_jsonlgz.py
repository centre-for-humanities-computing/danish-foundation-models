"""
Download  The Norwegian Colossal Corpus, convert to jsonl.gz with each document following the format:

{
    "id": "...",             # MANDATORY: source-specific identifier
    "text": "foo",           # MANDATORY: textual content of the document
    "source": "...",         # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
    "added": "...",          # OPTIONAL: timestamp ai2 acquired this data
    "created": "..."         # OPTIONAL: timestamp when orig document was created (best-guess if not available)
    "metadata": {...}        # OPTIONAL: source-specific metadata
}
"""

import os
import datetime
from functools import partial
from datasets import load_dataset, Dataset, IterableDataset


EXPORT_PATH = "ncc_sample.jsonl.gz"
date_added = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def convert_from_iterable_to_ds(iterable_ds: IterableDataset) -> Dataset:
    """Iterate through an IterableDataset, creating a Dataset. 
    Needed for debug mode (cleaning a smaller subset of the dataset)."""

    def _gen_from_iterable_dataset(iterable_ds):
        yield from iterable_ds

    return Dataset.from_generator(
        partial(_gen_from_iterable_dataset, iterable_ds), features=iterable_ds.features
    )


def _remove_existing_jsonlgz() -> None:
    """Checks if EXPORT_PATH exists, removes existing file if yes.
    This is because `ds.to_json` does not overwrite existing files.
    """
    if os.path.exists(EXPORT_PATH):
        os.remove(EXPORT_PATH)
        print(f"Removing existing export: {EXPORT_PATH}")


def _structure_records(obs: dict) -> dict:
    """Structure a single observation to Dolma format"""

    # NCC has publish year (YYYY) which will be used to construct the `created` column.
    # It is assumed that documents were created in YYYY-01-01 at midnight.
    publish_year = obs["publish_year"]

    # structure into dolma format
    obs = {
        "id": obs["id"],
        "text": obs["text"],
        "source": "NCC",
        "added": date_added,
        "created": f"{publish_year}-01-01T00:00:00.000Z",
        "metadata": {
            "doc_type": obs["doc_type"],
            "lang_fasttext": obs["lang_fasttext"],
            "lang_fasttext_conf": obs["lang_fasttext_conf"],
        },
    }

    return obs


def main(debug: bool = False) -> None:

    # remove existing export file
    # because `ds.to_json` does not overwrite it
    _remove_existing_jsonlgz()

    if debug:
        ncc = load_dataset(
            "NbAiLab/NCC", streaming=True, split="train", trust_remote_code=True
        )
        ds = ncc.take(1000)
        ds = convert_from_iterable_to_ds(ds)

    else:
        ds = load_dataset("NbAiLab/NCC", split="train", trust_remote_code=True)

    # cleanup cache to force the dataset to overwrite itself
    ds.cleanup_cache_files()
    # structure records & remove columns that are in the `metadata` key
    ds = ds.map(_structure_records)
    ds = ds.remove_columns(
        column_names=["doc_type", "publish_year", "lang_fasttext", "lang_fasttext_conf"]
    )

    # export
    ds.to_json(EXPORT_PATH, orient="records", lines=True, compression="gzip")


if __name__ == "__main__":
    # run the full dataset
    main(debug=False)

    # test type of observation
    ds = load_dataset("json", data_files=EXPORT_PATH, split="train")
    assert isinstance(ds[0], dict)
    # test that the right number of features are exported
    assert len(ds.features) == 6
    # test that it can be streamed
    ds = load_dataset("json", data_files=EXPORT_PATH, split="train", streaming=True)
    example = next(iter(ds))  # type: ignore
    assert isinstance(example, dict)
