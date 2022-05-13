"""
apply filters to danews dataset.
"""

from pathlib import Path

from wasabi import msg
from datasets import load_from_disk

if __name__ == "__main__":
        path = Path("/work") / "hope-infomedia_cleaned" / "infomedia_2000-2021"

        msg.info(f"loading: {path}")
        ds = load_from_disk(path)

        save_path = Path("/work") / "hope-infomedia_cleaned" / f"infomedia_2000-2021_filtered_v{ds.version}.arrow"
        save_path_json = save_path.with_suffix(".jsonl")
        if save_path.exists() or save_path_json.exists():
                raise Exception(f"save_path already exists: {save_path}")

        ds_filtered = ds.filter(lambda example: example["is_duplicate"] is False, num_proc=16)
        assert len(set(ds_filtered["is_duplicate"])) == 1

        # write dataset with added metadata
        msg.info(f"Saving to disk: {save_path}")
        ds_filtered.save_to_disk(str(save_path))
        msg.info(f"Saving to disk: {save_path_json}")
        ds_filtered.to_json(str(save_path_json))
