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

    domain_mapping_dict = {
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
        lambda x: {"domain": domain_mapping_dict[x["source"]]},  # type: ignore
        num_proc=num_proc,  # type: ignore
    )

    time_mapping_dict = {
        "retsinformationdk": "contemporary (2021)",
        "skat": "contemporary (2021)",
        "retspraksis": "contemporary (2021)",
        "hest": "contemporary (2021)",
        "cc": "contemporary (2021)",
        "adl": " 1700-2021",
        "botxt": "contemporary (2021)",
        "danavis": "1999-2003",
        "dannet": "contemporary (2021)",
        "depbank": "contemporary (2021)",
        "ep": "2004-2008",
        "ft": "2009-2019",
        "gutenberg": "1700-now",
        "jvj": "-",
        "naat": "1930-now",
        "opensub": "contemporary (2021)",
        "relig": "-",
        "spont": "2019",
        "synne": "contemporary (2021)",
        "tv2r": "2015-2019",
        "wiki": "2019-2020",
        "wikibooks": "2019-2020",
        "wikisource": "1700-now",
        "twfv19": "contemporary (2021)",  # not present in this version of the dataset
    }

    # add created
    ds = ds.map(lambda x: {"created": time_mapping_dict[x["source"]]}, num_proc=num_proc)  # type: ignore

    longname_mapping_dict = {
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
    ds = ds.map(lambda x: {"source": longname_mapping_dict[x["source"]]}, num_proc=num_proc)  # type: ignore

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
