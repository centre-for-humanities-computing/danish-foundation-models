"""
Flattens twitter newline json such that it can be read by the huggingface dataset loader.

Dependent on:
    isn't dependent

Authors:
    Kenneth Enevoldsen
"""
import glob
import os

import ndjson


def flatten_post(
    post: dict,
    keys_to_keep=["text", "id", "possibly_sensitive", "author_id", "source", "lang"],
):
    return {k: post[k] for k in keys_to_keep}


def flatten_ndjson(path: str, write_folder: str):
    """flatten a json and write to disk"""
    fname = os.path.split(path)[-1]
    path_, ext = os.path.splitext(fname)
    write_path = os.path.join(write_folder, path_ + "_flatten" + ext)

    print(f"Flattening: {path} to {write_path}")

    # stream in json from orgin to write_path
    with open(path, "r") as f:
        reader = ndjson.reader(f)

        with open(write_path, "w") as f:
            writer = ndjson.writer(f, ensure_ascii=False)

            for post in reader:
                # write flattened post to new json
                writer.writerow(flatten_post(post))


def main(read_path, write_path):
    path = os.path.join(read_path, "**", "*.ndjson")
    json_files = glob.glob(path, recursive=True)

    for j_file in json_files:
        flatten_ndjson(j_file, write_path)


if __name__ == "__main__":
    read_path = os.path.join("/work", "twitter")
    write_path = os.path.join("/work", "twitter_cleaned")
    main(read_path, write_path)
