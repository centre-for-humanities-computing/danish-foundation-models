"""
apply filters to danews dataset.
"""

from pathlib import Path

from wasabi import msg
from datasets import load_from_disk, load_dataset, DatasetDict


def test_split_ntokens(dataset, n_tokens: int, n_tokens_col = "n_tokens"):
        """assumed dataset is shuffled"""
        test_indices = []
        test_tok = 0
        for i, sample in  enumerate(dataset):
                test_tok += sample[n_tokens_col]
                test_indices.append(i)
                if test_tok > n_tokens:
                        break
        test = dataset.select(test_indices)
        test_indices = set(test_indices)
        ds_ = dataset.filter(lambda example, idx: idx not in test_indices, with_indices=True, num_proc=32)
        return test, ds_

if __name__ == "__main__":
        path = Path("/work") / "hope-infomedia_cleaned" / "infomedia_2000-2021.arrow"

        msg.info(f"loading: {path}")
        ds = load_from_disk(path)

        meta = load_dataset("csv", data_files="/work/hope-infomedia_cleaned/news_meta.csv", split="train")
        assert len(meta) == len(ds)
        ds = ds.add_column("n_tokens", meta["n_tokens"])
        
        save_path = Path("/work") / "hope-infomedia_cleaned" / f"infomedia_2000-2021_filtered_w_splits_v1.0.0.arrow"
        if save_path.exists():
                raise Exception(f"save_path already exists: {save_path}")

        test, ds_ = test_split_ntokens(ds, 25_000)
        assert len(ds_) == (len(ds) - len(test))
        val, train = test_split_ntokens(ds_, 25_000)
        assert len(train) == (len(ds_) - len(val))

        dataset = DatasetDict({"train": train, "test": test, "validation": val})

        # write dataset
        msg.info(f"Saving to disk: {save_path}")
        dataset.save_to_disk(save_path)

        # write jsonl splits
        msg.info(f"Saving jsonl to disk")
        save_path_json = Path("/work") / "hope-infomedia_cleaned" / f"infomedia_2000-2021_filtered_v{ds.version}_test.jsonl"
        test.to_json(str(save_path_json))
        save_path_json = Path("/work") / "hope-infomedia_cleaned" / f"infomedia_2000-2021_filtered_v{ds.version}_val.jsonl"
        val.to_json(str(save_path_json))

        save_path_json = Path("/work") / "hope-infomedia_cleaned" / f"infomedia_2000-2021_filtered_v{ds.version}_train.jsonl"
        train_filtered = train.filter(lambda example: example["is_duplicate"] is False, num_proc=32)
        assert len(set(train_filtered["is_duplicate"])) == 1
        train_filtered.to_json(str(save_path_json))
