"""
Script for downloading the AI-aktindsigt (Sønderborg kommune) dataset and
converting it to jsonl.gz.
The data is in xlsx format
"""
import datetime
import subprocess
from pathlib import Path
from typing import Any, Iterable

import pandas

# Git lfs must be installed
# git clone https://huggingface.co/datasets/AI-aktindsigt/Skrabet_kommunale_hjemmesider


def assume_same(x: Iterable[Any]):
    iterator = iter(x)
    first = next(iterator)

    for item in iterator:
        if pandas.isna(first):
            assert pandas.isna(item)
        else:
            assert first == item

    return first


def main():
    subprocess.run(("git", "clone",  "https://huggingface.co/datasets/AI-aktindsigt/Skrabet_kommunale_hjemmesider"))

    dfs = []
    for path in sorted(Path("Skrabet_kommunale_hjemmesider").glob("*.xlsx")):
        print(f"Reading {path}")

        dtype = {
            "text": str,
            "sentence": int,
            "kommune": str,
            "url": str,
            #"klassifikation": int, # This column seems to be unused
            "sha512": str,
            "ppl_score": float,
        }
        df = pandas.read_excel(path, header=1, dtype=dtype)
        df.dropna(subset=["text"], inplace=True) # Drop empty sentences
        # Convert all column names to lowercase (in some sheets URL is in capital letters)
        df.columns = map(str.lower, df.columns)

        dfs.append(df)

    megaframe = pandas.concat(dfs)

    print("Grouping by [id, sha512]")
    groups = megaframe.groupby(by=["id", "sha512"])

    agg_funcs = {
        "text": "\n".join, # join the sentences with newlines.
        "sentence": lambda x: max(x) + 1,
        "kommune": assume_same,
        "url": assume_same,
        #"sha512": assume_same,
        "ppl_score": lambda x: [float(a) for a in x],
    }
    print("Aggregating frame")
    df = groups.agg(agg_funcs)

    print("Reshaping into dolma format")
    df["id"] = df.apply(lambda row:'%s_%s' % (row.name[0],row.name[1]),axis=1)
    df["sha512"] = df.apply(lambda row:'%s' % row.name[1],axis=1)
    df["added"] = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    df["created"]: "1970-01-01T00:00:00.000Z,2024-04-01T00:00:00.000Z" # best guess creation time, between 1970 and release time

    metadata_keys = ["url", "kommune", "sentence", "ppl_score", "sha512"]
    df["metadata"] = df.apply(lambda row: {k: row[k] for k in metadata_keys}, axis=1)
    df.drop(columns=metadata_keys, inplace=True)

    print("Writing to file")
    df.to_json("ai_aktindsigt.jsonl.gz", orient="records", lines=True)
    print("Done")

if __name__ == "__main__":
    main()
