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

oldest_case = "1855-02-28T00:00:00.000Z"
date_added = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
case_time_span = ",".join([oldest_case, date_added])


def reformat_dataset(ds: Dataset) -> Dataset:
    # current keys:
    # ['case_id', 'Overskrift', 'Afgørelsesstatus', 'Faggruppe', 'Ret', 'Rettens sagsnummer', 'Sagstype', 'Instans', 'Domsdatabasens sagsnummer', 'Sagsemner', 'Særlige retsskridt', 'Sagsdeltagere', 'Dørlukning', 'Løftet ud af småsagsprocessen', 'Anerkendelsespåstand', 'Politiets journalnummer', 'Påstandsbeløb', 'Sagskomplekser', 'text', 'text_anonymized', 'text_len', 'text_anon_len']

    # rename celex_id to id
    ds = ds.rename_column("case_id", "id")

    # add source column
    source_column = ["domsdatabasen"] * len(ds)  # type: ignore
    ds = ds.add_column("source", source_column)  # type: ignore

    # add created column
    created_column = [case_time_span] * len(ds)  # type: ignore
    ds = ds.add_column("created", created_column)  # type: ignore

    # add added column
    added_column = [date_added] * len(ds)  # type: ignore
    ds = ds.add_column("added", added_column)  # type: ignore

    metadata_keys = ['Overskrift', 'Afgørelsesstatus', 'Faggruppe', 'Ret', 'Rettens sagsnummer', 'Sagstype', 'Instans', 'Domsdatabasens sagsnummer', 'Sagsemner', 'Særlige retsskridt', 'Sagsdeltagere', 'Dørlukning', 'Løftet ud af småsagsprocessen', 'Anerkendelsespåstand', 'Politiets journalnummer', 'Påstandsbeløb', 'Sagskomplekser', 'text_len']
    # add metadata
    ds = ds.map(  # type: ignore
        lambda x: {  # type: ignore
            "text": x["text"],
            "metadata": {
                k: x[k] for k in metadata_keys  # type: ignore
            }
        },
    )  # type: ignore
    ds = ds.remove_columns(["text_anonymized", "text_anon_len"])  # type: ignore
    ds = ds.remove_columns(metadata_keys)  # type: ignore

    return ds  # type: ignore


def main():
    ds = load_dataset("alexandrainst/domsdatabasen")
    assert isinstance(ds, DatasetDict)
    # We take only the train dataset in case this dataset is used for model evaulation
    ds = ds["train"]
    assert isinstance(ds, Dataset)

    # reformat
    ds = reformat_dataset(ds)

    # save to jsonl.gz
    ds.to_json("domsdatabasen.jsonl.gz", orient="records", lines=True, compression="gzip")  # type: ignore


if __name__ == "__main__":
    main()

    # # test that it load back in
    ds = load_dataset("json", data_files="domsdatabasen.jsonl.gz", split="train")
    assert isinstance(ds[0], dict)  # type: ignore

    # test that it can be streamed
    ds = load_dataset(
        "json",
        data_files="domsdatabasen.jsonl.gz",
        split="train",
        streaming=True,
    )
    example = next(iter(ds))  # type: ignore
    assert isinstance(example, dict)
