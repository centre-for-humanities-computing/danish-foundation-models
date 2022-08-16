"""
Apply filters to the Twitter dataset.

Dependent on:
    src/applications/hopetwitter/add_metadata.py

Authors:
    Kenneth Enevoldsen
"""
import os

from datasets import load_from_disk
from wasabi import msg

if __name__ == "__main__":
    path = os.path.join(
        "/work", "twitter_cleaned", "twitter_da_stopwords_2019-01-01_2021-04-30.arrow"
    )

    msg.info(f"loading: {path}")
    ds = load_from_disk(path)

    ds_filtered = ds.filter(
        lambda example: example["is_duplicate"] is False, num_proc=16
    )
    assert len(set(ds_filtered["is_duplicate"])) == 1

    # write dataset with added metadata
    save_path = os.path.join(
        "/work",
        "twitter_cleaned",
        f"twitter_da_stopwords_2019-01-01_2021-04-30_filtered_v{ds.version}.arrow",
    )
    msg.info(f"Saving to disk: {save_path}")
    ds_filtered.save_to_disk(save_path)
