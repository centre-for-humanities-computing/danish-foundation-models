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

from datasets import Dataset, DatasetDict, load_dataset  # type: ignore


def reformat_dataset(ds: Dataset, num_proc: int) -> Dataset:
    # current keys: dict_keys(['text', 'source', 'doc_id', 'LICENSE', 'uri', 'date_built'])

    # doc-id --> id
    ds = ds.rename_column("doc_id", "id")
    # date-built --> added
    ds = ds.rename_column("date_built", "added")

    source2domain = {
        "retsinformationdk": "Legal",
        "skat": "Legal",
        "retspraksis": "Legal",
        "hest": "Social Media",
        "cc": "Web",
        "adl": "Wiki & Books",
        "botxt": "Other",
        "danavis": "News",
        "dannet": "dannet",
        "depbank": "Other",
        "ep": "Conversation",
        "ft": "Conversation",
        "gutenberg": "Wiki & Books",
        "jvj": "Wiki & Books",
        "naat": "Conversation",
        "opensub": "Conversation",
        "relig": "Wiki & Books",
        "spont": "Conversation",
        "synne": "Other",
        "tv2r": "News",
        "wiki": "Wiki & Books",
        "wikibooks": "Wiki & Books",
        "wikisource": "Wiki & Books",
        "twfv19": "Social Media",  # not present in this version of the dataset
    }

    # add domain
    ds = ds.map(  # type: ignore
        lambda x: {"domain": source2domain[x["source"]]},  # type: ignore
        num_proc=num_proc,  # type: ignore
    )

    source2time = {
        "retsinformationdk": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "skat": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "retspraksis": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "hest": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "cc": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "adl": "1700-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "botxt": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "danavis": "1999-01-01T00:00:00.000Z, 2004-01-01T00:00:00.000Z",
        "dannet": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "depbank": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "ep": "2004-01-01T00:00:00.000Z, 2009-01-01T00:00:00.000Z",
        "ft": "2009-01-01T00:00:00.000Z, 2019-01-01T00:00:00.000Z",
        "gutenberg": "1700-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "jvj": "1873-01-01T00:00:00.000Z, 1951-01-01T00:00:00.000Z",
        "naat": "1930-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "opensub": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "relig": "NA",
        "spont": "2019-01-01T00:00:00.000Z, 2020-01-01T00:00:00.000Z",
        "synne": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "tv2r": "2015-01-01T00:00:00.000Z, 2020-01-01T00:00:00.000Z",
        "wiki": "2019-01-01T00:00:00.000Z, 2021-01-01T00:00:00.000Z",
        "wikibooks": "2019-01-01T00:00:00.000Z, 2021-01-01T00:00:00.000Z",
        "wikisource": "1700-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
        "twfv19": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",  # not present in this version of the dataset
    }

    # add created
    ds = ds.map(lambda x: {"created": source2time[x["source"]]}, num_proc=num_proc)  # type: ignore

    source2longname = {
        "retsinformationdk": "retsinformation.dk (Danish legal information)",
        "skat": "Skat (Danish tax authority)",
        "retspraksis": "retspraksis (Danish legal information)",
        "hest": "Hestenettet (Danish debate forum)",
        "cc": "Common Crawl",
        "adl": " Archive for Danish Literature",
        "botxt": "Bornholmsk (Danish dialect)",
        "danavis": "Danish daily newspapers",
        "dannet": "DanNet (Danish WordNet)",
        "depbank": "Danish Dependency Treebank",
        "ep": "European Parliament",
        "ft": "Folketinget (Danish Parliament)",
        "gutenberg": "Gutenberg",
        "jvj": "Johannes V. Jensen (Danish poet)",
        "naat": "NAAT",
        "opensub": "Open Subtitles",
        "relig": "Religious texts",
        "spont": "Spontaneous speech",
        "synne": "Synderjysk (Danish dialect)",
        "tv2r": "TV 2 Radio (Danish news)",
        "wiki": "Wikipedia",
        "wikibooks": "Wikibooks",
        "wikisource": "Wikisource",
        "twfv19": "Twitter Folketingsvalget 2019 (Danish election tweets)",  # not present in this version of the dataset
    }

    # update source
    ds = ds.map(lambda x: {"source": source2longname[x["source"]]}, num_proc=num_proc)  # type: ignore

    # move license, domain to metadata
    ds = ds.map(  # type: ignore
        lambda x: {"metadata": {"license": x["LICENSE"], "domain": x["domain"]}},  # type: ignore
        num_proc=num_proc,
    )
    ds = ds.remove_columns(["LICENSE", "domain", "uri"])
    return ds


def main():
    num_proc = 2
    ds: DatasetDict = load_dataset("DDSC/partial-danish-gigaword-no-twitter")  # type: ignore
    ds: Dataset = ds["train"]  # type: ignore

    # reformat
    ds = reformat_dataset(ds, num_proc=num_proc)

    # save to jsonl.gz
    ds.to_json("data.jsonl.gz", orient="records", lines=True, compression="gzip")  # type: ignore


if __name__ == "__main__":
    main()

    # # test that it load back in
    ds = load_dataset("json", data_files="data.jsonl.gz", split="train")
    assert isinstance(ds[0], dict)  # type: ignore

    # test that it can be streamed
    ds = load_dataset("json", data_files="data.jsonl.gz", split="train", streaming=True)
    example = next(iter(ds))  # type: ignore
    assert isinstance(example, dict)
