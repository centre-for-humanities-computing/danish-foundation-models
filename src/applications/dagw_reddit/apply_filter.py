"""
apply filters to twitter dataset.
"""

import os

from wasabi import msg
from datasets import load_from_disk

def filter(batch):
        i = 0
        while i < len(batch):
                if batch["is_duplicate"][i] is not False:
                        for k in batch:
                                batch[k].pop(i)
                else:
                        i += 1
        return batch


if __name__ == "__main__":
        path = os.path.join("/work", "dagw-clean", "dfm_dagw_reddit.arrow")

        msg.info(f"loading: {path}")
        ds = load_from_disk(path)

        ds_filtered = ds.filter(lambda example: example["is_13_gram_duplicate"] is False, num_proc=16)
        assert len(set(ds_filtered["is_13_gram_duplicate"])) == 1

        # write dataset with added metadata
        save_path = os.path.join("/work", "dagw-clean",  f"dagw_reddit_filtered_v{ds.version}.arrow")
        msg.info(f"Saving to disk: {save_path}")
        ds_filtered.save_to_disk(save_path)
