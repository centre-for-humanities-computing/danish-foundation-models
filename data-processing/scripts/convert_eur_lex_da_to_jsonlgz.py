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

The dataset contains reference and summaries. As we use this dataset for pretraining we
concatenate reference and summary

"""
import datetime

from datasets import Dataset, DatasetDict, load_dataset

eu_start_time = "1993-11-01T00:00:00.000Z"
date_added = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
eu_time_span = ",".join([eu_start_time, date_added])


def reformat_dataset(ds: Dataset) -> Dataset:
    # current keys: ['celex_id', 'reference', 'summary']

    # rename celex_id to id
    ds = ds.rename_column("celex_id", "id")

    # add source column
    source_column = ["eur-lex-sum-da"] * len(ds)  # type: ignore
    ds = ds.add_column("source", source_column)  # type: ignore

    # add created column
    created_column = [eu_time_span] * len(ds)  # type: ignore
    ds = ds.add_column("created", created_column)  # type: ignore

    # add added column
    added_column = [date_added] * len(ds)  # type: ignore
    ds = ds.add_column("added", added_column)  # type: ignore

    # add metadata
    ds = ds.map(  # type: ignore
        lambda x: {  # type: ignore
            "text": x["reference"] + "\n" + x["summary"],
            "metadata": {
                "summary_start": len(x["reference"] + "\n"),  # type: ignore
            }
        },
    )  # type: ignore
    ds = ds.remove_columns(["reference", "summary"])  # type: ignore

    return ds  # type: ignore


def main():
    ds = load_dataset("dennlinger/eur-lex-sum", "danish")
    assert isinstance(ds, DatasetDict)
    # We take only the train dataset in case this dataset is used for model evaulation
    ds = ds["train"]
    assert isinstance(ds, Dataset)

    # reformat
    ds = reformat_dataset(ds)

    # save to jsonl.gz
    ds.to_json("eur-lex-sum-da.jsonl.gz", orient="records", lines=True, compression="gzip")  # type: ignore


if __name__ == "__main__":
    main()

    # # test that it load back in
    ds = load_dataset("json", data_files="eur-lex-sum-da.jsonl.gz", split="train")
    assert isinstance(ds[0], dict)  # type: ignore

    # test that it can be streamed
    ds = load_dataset(
        "json",
        data_files="eur-lex-sum-da.jsonl.gz",
        split="train",
        streaming=True,
    )
    example = next(iter(ds))  # type: ignore
    assert isinstance(example, dict)
