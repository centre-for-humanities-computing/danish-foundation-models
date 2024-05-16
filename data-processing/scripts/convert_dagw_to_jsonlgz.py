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
from typing import Generator
import os
from datetime import datetime
from dateutil.parser import parse


def replace_swedish(timestamp_str):
    # Mapping of Swedish day and month names to English
    swedish_to_english = {
        'mån': 'Mon',
        'tis': 'Tue',
        'ons': 'Wed',
        'tors': 'Thu',
        'fre': 'Fri',
        'lör': 'Sat',
        'sön': 'Sun',
        'jan': 'Jan',
        'feb': 'Feb',
        'mar': 'Mar',
        'apr': 'Apr',
        'maj': 'May',
        'jun': 'Jun',
        'jul': 'Jul',
        'aug': 'Aug',
        'sep': 'Sep',
        'okt': 'Oct',
        'nov': 'Nov',
        'dec': 'Dec'
    }
    for swedish, english in swedish_to_english.items():
        timestamp_str = timestamp_str.replace(swedish, english)
    return timestamp_str

def parse_added(timestamp_str):
    # Handling NA
    if timestamp_str == "NA":
        return "2024-05-16" # Set a default value

    timestamp_str = replace_swedish(timestamp_str)

    formats = [
        "%a %b %d %H:%M:%S %Y %z",     # Without timezone name, with UTC offset
        "%a %b %d %H:%M:%S %Y %Z %z",   # With timezone name and UTC offset
        "%a %d %b %Y %H:%M:%S %Z %z",  # With day first, e.g., ons 13 nov 2019 12:42:34 CET +0100, Swedish abbreviations
        "%a %d %b %Y %H:%M:%S %z"      # Without timezone name, with UTC offset, day first
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Fallback using dateutil.parser.parse
    try:
        dt = parse(timestamp_str)
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Timestamp '{timestamp_str}' does not match any known format.")



def reformat_and_clean_dataset(ds: Dataset, num_proc: int) -> Dataset:
    # current keys: dict_keys(['text', 'source', 'doc_id', 'LICENSE', 'uri', 'date_built'])

    # doc-id --> id
    ds = ds.rename_column("doc_id", "id")
    # date-built --> added
    ds = ds.rename_column("date_built", "added")
    ## source --> sub-source
    #ds = ds.rename_column("source", "sub-source")
    # format added: "%a %b %d %H:%M:%S %Y %Z %z" to "%Y-%m-%d"
    ds = ds.map(
        lambda x: {"added": parse_added(x["added"])},  # type: ignore
        num_proc=num_proc,
    )

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

    # source2time = {
    #     "retsinformationdk": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "skat": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "retspraksis": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "hest": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "cc": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "adl": "1700-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "botxt": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "danavis": "1999-01-01T00:00:00.000Z, 2004-01-01T00:00:00.000Z",
    #     "dannet": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "depbank": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "ep": "2004-01-01T00:00:00.000Z, 2009-01-01T00:00:00.000Z",
    #     "ft": "2009-01-01T00:00:00.000Z, 2019-01-01T00:00:00.000Z",
    #     "gutenberg": "1700-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "jvj": "1873-01-01T00:00:00.000Z, 1951-01-01T00:00:00.000Z",
    #     "naat": "1930-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "opensub": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "relig": "NA",
    #     "spont": "2019-01-01T00:00:00.000Z, 2020-01-01T00:00:00.000Z",
    #     "synne": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "tv2r": "2015-01-01T00:00:00.000Z, 2020-01-01T00:00:00.000Z",
    #     "wiki": "2019-01-01T00:00:00.000Z, 2021-01-01T00:00:00.000Z",
    #     "wikibooks": "2019-01-01T00:00:00.000Z, 2021-01-01T00:00:00.000Z",
    #     "wikisource": "1700-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",
    #     "twfv19": "2000-01-01T00:00:00.000Z, 2022-01-01T00:00:00.000Z",  # not present in this version of the dataset
    # }

    source2time ={
        "retsinformationdk": "2000-01-01, 2022-01-01",
        "skat": "2000-01-01, 2022-01-01",
        "retspraksis": "2000-01-01, 2022-01-01",
        "hest": "2000-01-01, 2022-01-01",
        "cc": "2000-01-01, 2022-01-01",
        "adl": "1700-01-01, 2022-01-01",
        "botxt": "2000-01-01, 2022-01-01",
        "danavis": "1999-01-01, 2004-01-01",
        "dannet": "2000-01-01, 2022-01-01",
        "depbank": "2000-01-01, 2022-01-01",
        "ep": "2004-01-01, 2009-01-01",
        "ft": "2009-01-01, 2019-01-01",
        "gutenberg": "1700-01-01, 2022-01-01",
        "jvj": "1873-01-01, 1951-01-01",
        "naat": "1930-01-01, 2022-01-01",
        "opensub": "2000-01-01, 2022-01-01",
        # "relig": "NA",
        "relig" : "1700-01-01, 2022-01-01", # Take a guess instead
        "spont": "2019-01-01, 2020-01-01",
        "synne": "2000-01-01, 2022-01-01",
        "tv2r": "2015-01-01, 2020-01-01",
        "wiki": "2019-01-01, 2021-01-01",
        "wikibooks": "2019-01-01, 2021-01-01",
        "wikisource": "1700-01-01, 2022-01-01",
        "twfv19": "2000-01-01, 2022-01-01" # not present in this version of the dataset
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

    # update sub-source
    ds = ds.map(lambda x: {"source-pretty": source2longname[x["source"]]}, num_proc=num_proc)  # type: ignore

    # move license, domain, sub-source to metadata
    ds = ds.map(  # type: ignore
            lambda x: {"metadata": {"license": x["LICENSE"], "domain": x["domain"], "source-pretty": x["source-pretty"]}},  # type: ignore
        num_proc=num_proc,
    )

    # add dagw to source: dagw-source
    ds = ds.map(lambda x: {**x, "source": f"dagw-{x['source']}"})
    ds = ds.remove_columns(["LICENSE", "domain", "uri", "source-pretty"])


    # filter out documents with empty "text" entries:
    # either empty or totally while space
    # 162051 out of 673211 empty docs found in total if skipping this step
    ds = ds.filter(lambda x: x['text'] != '' and not x['text'].isspace(), num_proc=num_proc)

    return ds

def filter_by_source_pretty(ds: Dataset, source_pretty_list: list, num_proc: int) -> Dataset:
    """
    Filters the dataset to exclude records where the 'metadata' field's 'domain'
    matches one of the domains specified in 'domain_list'.
    """
    # Filter dataset based on the domain list
    return ds.filter(lambda x: x['metadata']['source-pretty'] not in source_pretty_list, num_proc=num_proc)

def split_by_source(ds: Dataset, num_proc: int) -> Generator[tuple[str, Dataset], None, None]:
    """
    Split the dataset into a dataset for each source
    """
    sources = ds.unique("source")
    for source in sources:
        yield source, ds.filter(lambda x: x["source"] == source, num_proc=num_proc)

def determine_size_category(num_records):
    if num_records < 10_000:
        return "1-10k"
    elif num_records < 100_000:
        return "10k-100k"
    elif num_records < 1_000_000:
        return "100k-1M"
    elif num_records < 10_000_000:
        return "1M-10M"
    elif num_records < 100_000_000:
        return "10M-100M"
    else:
        return "100M+"

def make_markdown(ds: Dataset, directory: str) -> None:
    source2licenseIdentifier = {
    "dagw-jvj": "cc-by-sa-4.0",
    "dagw-ft": "cc0-1.0",
    "dagw-retsinformationdk": "other",
    "dagw-retspraksis": "cc0-1.0",
    "dagw-adl": "cc0-1.0",
    "dagw-naat": "cc0-1.0",
    "dagw-relig": "cc0-1.0",
    "dagw-depbank": "cc-by-sa-4.0",
    "dagw-skat": "cc0-1.0",
    "dagw-hest": "cc0-1.0",
    "dagw-gutenberg": "Gutenberg License",
    "dagw-tv2r": "cc-by-sa-4.0",
    "dagw-wikibooks": "cc0-1.0",
    "dagw-ep": "cc0-1.0",
    "dagw-spont": "cc0-1.0",
    "dagw-wiki": "cc0-1.0",
    "dagw-botxt": "cc0-1.0",
    "dagw-synne": "cc0-1.0",
    "dagw-dannet": "DanNet 1.0 License",
    "dagw-wikisource": "cc0-1.0"
    }
    source2LicenseName = {
    "dagw-jvj": "Creative Commons Attribution Share Alike 4.0",
    "dagw-ft": "Creative Commons Zero v1.0 Universal",
    "dagw-retsinformationdk": "Danish Copyright Law",
    "dagw-retspraksis": "Creative Commons Zero v1.0 Universal",
    "dagw-adl": "Creative Commons Zero v1.0 Universal",
    "dagw-naat": "Creative Commons Zero v1.0 Universal",
    "dagw-relig": "Creative Commons Zero v1.0 Universal",
    "dagw-depbank": "Creative Commons Attribution Share Alike 4.0",
    "dagw-skat": "Creative Commons Zero v1.0 Universal",
    "dagw-hest": "Creative Commons Zero v1.0 Universal",
    "dagw-gutenberg": "Gutenberg License",
    "dagw-tv2r": "Creative Commons Attribution Share Alike 4.0",
    "dagw-wikibooks": "Creative Commons Zero v1.0 Universal",
    "dagw-ep": "Creative Commons Zero v1.0 Universal",
    "dagw-spont": "Creative Commons Zero v1.0 Universal",
    "dagw-wiki": "Creative Commons Zero v1.0 Universal",
    "dagw-botxt": "Creative Commons Zero v1.0 Universal",
    "dagw-synne": "Creative Commons Zero v1.0 Universal",
    "dagw-dannet": "DanNet 1.0 License",
    "dagw-wikisource": "Creative Commons Zero v1.0 Universal"
    }
    num_records = ds.num_rows
    num_records_category = determine_size_category(num_records)
    sample = ds[0]
    text = sample["text"].strip()[:50].replace("'", "\\'")  # Escaping single quotes in the YAML-like example and strip leading/trailing whitespace
    source = sample["source"]
    id = sample["id"]
    added = sample["added"]
    created = sample["created"]
    domain = sample["metadata"]["domain"]
    license = sample["metadata"]["license"]
    licenseIdentifier = source2licenseIdentifier[source]
    licenseName = source2LicenseName[source]
    source_pretty = sample["metadata"]["source-pretty"]
    templete = """---
pretty_name: {source_pretty}
language:
  - da
license: {licenseIdentifier}
license_name: {licenseName}
size_categories:
  - {num_records_category}
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# Dataset Card for {source_pretty}
## Dataset Description
- **Number of records:** {num_records}
- **Languages:** Danish
## Dataset Sturcture
An example from the dataset looks as follows.
```yaml
{{
    'text': '{text}',
    'source': '{source}',
    'id': '{id}',
    'added': '{added}',
    'created': '{created}',
    'metadata': {{
        'domain': '{domain}',
        'license': '{license}',
        'source-pretty': '{source_pretty}'
        }}
}}
```

## Data Fields

- **id**: source-specific identifier.
- **text**: textual content of the document.
- **source**: source of the data.
- **added**: timestamp ai2 acquired this data.
- **created**": timestamp when original document was created (best-guess if not available)
- **metadata**: source-specific metadata.

## Lisence Information
<details>
<summary>{licenseName}</summary>
<p>
{license}
</p>
</details>
"""
    filled_template = templete.format(
        source_pretty=source_pretty,
        licenseIdentifier=licenseIdentifier,
        licenseName=licenseName,
        num_records=num_records,
        num_records_category=num_records_category,
        text=text,
        source=source,
        id=id,
        added=added,
        created=created,
        domain=domain,
        license=license,
    )
    file_path = os.path.join(directory, f"{source}.md")
    with open(file_path, 'w') as md_file:
        md_file.write(filled_template)

def main():
    num_proc = 32
    # Domains to filter
    source_pretty_list = ['Danish daily newspapers', 'Common Crawl', 'Open Subtitles']

    print("Start loading the dataset...")
    ds: DatasetDict = load_dataset("DDSC/partial-danish-gigaword-no-twitter")
    ds: Dataset = ds["train"]
    print("Dataset loaded.")
    print("Start reformatting the dataset...")
    # Reformat and clean the dataset
    ds = reformat_and_clean_dataset(ds, num_proc=num_proc)
    print("Dataset reformatted and cleaned.")
    # Filter dataset based on domains
    ds = filter_by_source_pretty(ds, source_pretty_list, num_proc=num_proc)

    # Print out a sample
    sample = ds[0]
    print("Sample Record:", sample)

    print("Start saving the dataset...")

    save_directory_path = "/work/dfm-data/pre-training/dagw/documents"
    datasheet_path = "/work/github/danish-foundation-models/docs/datasheets"
    # Create the directory if it does not exist
    if not os.path.exists(save_directory_path):
        os.makedirs(save_directory_path)
    for source, ds in split_by_source(ds, num_proc=num_proc):
        # Make markdown
        make_markdown(ds, datasheet_path)
        file_path = os.path.join(save_directory_path, f"{source}.jsonl.gz")
        # Save to jsonl.gz
        ds.to_json(file_path, orient="records", lines=True, compression="gzip")
        # Load and test dataset
        ds_test = load_dataset("json", data_files=file_path, split="train")
        assert isinstance(ds_test[0], dict)
        ds_stream = load_dataset("json", data_files=file_path, split="train", streaming=True)
        example = next(iter(ds_stream))
        assert isinstance(example, dict)
    print("Dataset saved.")

if __name__ == "__main__":
    main()
