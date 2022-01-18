"""Dataset loading script for Danish Foundation Models
"""
from typing import Optional
from datasets import load_dataset
from datasets import DatasetDict


def main():
    ds = dfm_load_dataset("DDSC/reddit-da")
    print("DONE")


def dfm_load_dataset(dataset: str):
    """loads a single dataset from the Hugging Face Datasets hub.

    Args:
        dataset (str): string for Hugging Face dataset.

    Returns:
        DatasetDict: Dataset with train, test and validation split.
    """

    ds = load_dataset(dataset, streaming=True)

    if "validation" and "test" not in ds:
        train_test = ds["train"].train_test_split(test_size=0.1)
        # Split the 10% test + valid in half test, half valid
        test_valid = train_test["test"].train_test_split(test_size=0.5)
        # gather everyone if you want to have a single DatasetDict
        ds = DatasetDict(
            {
                "train": train_test["train"],
                "test": test_valid["test"],
                "val": test_valid["train"],
            }
        )

    return ds


if __name__ == "__main__":
    main()
