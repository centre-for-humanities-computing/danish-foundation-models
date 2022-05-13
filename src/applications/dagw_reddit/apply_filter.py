"""
apply filters to twitter dataset.
"""

import os
from pathlib import Path
from wasabi import msg
from datasets import load_from_disk, load_dataset, DatasetDict

def __test_split_ntokens(dataset, n_tokens: int, category: set, n_tokens_col = "n_tokens"):
        """assumed dataset is shuffled"""
        print(f"Started category: {category}")
        test_indices = []
        test_tok = 0
        found_all = False
        for i, sample in  enumerate(dataset):
                if sample["source"] not in category:
                        continue
                test_tok += sample[n_tokens_col]
                test_indices.append(i)
                if test_tok > n_tokens:
                        found_all = True
                        break
        if found_all is False:
                print(f"WARNING: did not find all on category {category}")
        return test_indices

def test_split(dataset, n_tokens_pr_cat: int=25_000):
        reddit_test_indices = __test_split_ntokens(dataset, n_tokens_pr_cat, category={"reddit-da"})
        legal_test_indices = __test_split_ntokens(dataset, n_tokens_pr_cat, category={"retsinformationdk", "skat"})
        spont_speech_test_indices = __test_split_ntokens(dataset, n_tokens_pr_cat, category={"spont", "opensub"})
        bornholmsk_test_indices = __test_split_ntokens(dataset, n_tokens_pr_cat, category={"botxt"})
        books_test_indices = __test_split_ntokens(dataset, n_tokens_pr_cat, category={"gutenberg", "wikibooks", "wikisource", "adl"})
        wiki_test_indices = __test_split_ntokens(dataset, n_tokens_pr_cat, category={"wiki"})
        test_indices = reddit_test_indices + legal_test_indices + spont_speech_test_indices + bornholmsk_test_indices + books_test_indices + wiki_test_indices
        test = dataset.select(test_indices)
        test_indices = set(test_indices)
        train = dataset.filter(lambda example, idx: idx not in test_indices, with_indices=True, num_proc=32)
        return test, train


if __name__ == "__main__":
        path = os.path.join("/work", "dagw-clean", "dfm_dagw_reddit.arrow")

        msg.info(f"loading: {path}")
        ds = load_from_disk(path)

        # create dataset splits
        test, ds_ = test_split(ds, n_tokens_pr_cat=25_000)
        assert len(ds_) == (len(ds) - len(test))
        val, train = test_split(ds_, n_tokens_pr_cat=25_000)
        assert len(train) == (len(ds_) - len(val))

        dataset = DatasetDict({"train": train, "test": test, "validation": val})

        # write dataset with added metadata
        save_path = os.path.join("/work", "dagw-clean",  f"dagw_reddit_filtered_w_splits_v1.0.0.arrow")
        msg.info(f"Saving to disk: {save_path}")
        dataset.save_to_disk(save_path)

        # write jsonl splits
        msg.info(f"Saving jsonl to disk")
        save_path_json = Path("/work") / "dagw-clean" / "dagw_reddit_v1.0.0_test.arrow" 
        test.to_json(str(save_path_json))
        save_path_json = Path("/work") / "dagw-clean" / "dagw_reddit_v1.0.0_val.arrow" 
        val.to_json(str(save_path_json))
        train_filtered = train.filter(lambda example: example["is_13_gram_duplicate"] is False, num_proc=32)
        assert len(set(train_filtered["is_13_gram_duplicate"])) == 1
        save_path_json = Path("/work") / "dagw-clean" / "dagw_reddit_filtered_v1.0.0_train.arrow" 
        train_filtered.to_json(str(save_path_json))

