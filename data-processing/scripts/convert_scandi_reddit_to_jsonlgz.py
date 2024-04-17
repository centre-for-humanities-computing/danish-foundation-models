"""
downloads dataset and save it as jsonl.gz file with the format:

{
    "id": "...",             # MANDATORY: source-specific identifier
    "text": "foo",           # MANDATORY: textual content of the document
    "source": "...",         # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
    "added": "...",          # OPTIONAL: timestamp ai2 acquired this data
    "created": "..."         # OPTIONAL: timestamp when orig document was created (best-guess if not available)
    "metadata": {...}        # OPTIONAL: source-specific metadata
}
"""
import datetime

from datasets import Dataset, DatasetDict, load_dataset  # type: ignore

reddit_time = "2005-12-01T00:00:00.000Z, 2022-11-01T00:00:00.000Z"
date_added = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def reformat_dataset(ds: Dataset) -> Dataset:
    # current keys: ['doc', 'subreddit', 'language', 'language_confidence']

    # rename doc to text
    ds = ds.rename_column("doc", "text")

    # add id column
    id_column = [str(i) for i in range(len(ds))]  # dolma id must be a string
    ds = ds.add_column("id", id_column)  # type: ignore

    # add source column
    source_column = ["scandi-reddit"] * len(ds)  # type: ignore
    ds = ds.add_column("source", source_column)  # type: ignore

    # add created column
    created_column = [reddit_time] * len(ds)  # type: ignore
    ds = ds.add_column("created", created_column)  # type: ignore

    # add added column
    added_column = [date_added] * len(ds)  # type: ignore
    ds = ds.add_column("added", added_column)  # type: ignore

    # add metadata
    ds = ds.map(  # type: ignore
        lambda x: {  # type: ignore
            "metadata": {
                "language": x["language"],  # type: ignore
                "language_confidence": x["language_confidence"],  # type: ignore
                "subreddit": x["subreddit"],  # type: ignore
            },
        },
    )  # type: ignore
    ds = ds.remove_columns(["subreddit", "language", "language_confidence"])  # type: ignore

    return ds  # type: ignore


def main():
    ds = load_dataset("alexandrainst/scandi-reddit")
    assert isinstance(ds, DatasetDict)
    ds = ds["train"]
    assert isinstance(ds, Dataset)

    # reformat
    ds = reformat_dataset(ds)

    # save to jsonl.gz
    ds.to_json("scandi-reddit.jsonl.gz", orient="records", lines=True, compression="gzip")  # type: ignore


if __name__ == "__main__":
    main()

    # # test that it load back in
    ds = load_dataset("json", data_files="scandi-reddit.jsonl.gz", split="train")
    assert isinstance(ds[0], dict)  # type: ignore

    # test that it can be streamed
    ds = load_dataset(
        "json",
        data_files="scandi-reddit.jsonl.gz",
        split="train",
        streaming=True,
    )
    example = next(iter(ds))  # type: ignore
    assert isinstance(example, dict)
