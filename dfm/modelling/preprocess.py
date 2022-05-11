"""Data preprocessing script for Danish Foundation Models """

from functools import partial
from typing import Union

from datasets import DatasetDict
from datasets.arrow_dataset import Dataset
from dfm.data.load import dfm_load_dataset
from transformers import AutoTokenizer, BatchEncoding
from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.tokenization_utils_fast import PreTrainedTokenizerFast


def main():
    """Main method for running the preprocessing script."""

    tokenizer = AutoTokenizer.from_pretrained("Maltehb/danish-bert-botxo")

    ds = dfm_load_dataset("DDSC/reddit-da")
    ds["train"] = ds["train"].select(range(2))
    ds["test"] = ds["test"].select(range(2))
    ds["val"] = ds["val"].select(range(2))

    ds = preprocess_dataset(ds, tokenizer)


def preprocess_dataset(
    dataset: DatasetDict,
    tokenizer: Union[PreTrainedTokenizerFast, PreTrainedTokenizerBase],
    num_proc: int = 4,
    block_size: int = 512,
) -> Dataset:
    """Preprocesses a dataset for training.

    Args:
        dataset (DatasetDict): Dataset to be preprocessed.
        tokenizer (Union[PreTrainedTokenizerFast, PreTrainedTokenizerBase]): A Hugging Face tokenizer.
        num_proc (int, optional): Number of cores to use for preprocessing. Defaults to 4.
        block_size (int, optional): Block size of how long the grouped texts can maximally be. Defaults to 512.

    Returns:
        Dataset: A preprocessed dataset.
    """

    # Only use text columns
    # for key in dataset.keys():
    #     cols = dataset[key].column_names
    #     cols.remove("text")
    #     dataset[key] = dataset[key].remove_columns(cols)

    # Tokenize texts
    tokenize_func_ = partial(tokenize_func, tokenizer=tokenizer)
    dataset = dataset.map(tokenize_func_, batched=True, remove_columns="text")

    # Group texts into blocks of `block_size`.
    group_texts_ = partial(group_texts, block_size=block_size)
    dataset = dataset.map(
        group_texts_,
        batched=True,
        batch_size=1000,
    )

    return dataset


def tokenize_func(
    examples: dict, tokenizer: Union[PreTrainedTokenizerFast, PreTrainedTokenizerBase]
) -> BatchEncoding:
    """Wrapper for tokenization.

    Args:
        examples (dict): A dictionary containing a "text" key and the text value.
        tokenizer (Union[PreTrainedTokenizerFast, PreTrainedTokenizerBase]): A Hugging Face tokenizer.

    Returns:
        BatchEncoding: A batch encoding with input ids, token type ids and attention masks.
    """
    return tokenizer(examples["text"])


def group_texts(examples: dict, block_size: int) -> dict:
    """Groups texts into blocks of `block_size

    Args:
        examples (dict): A dictionary containing a "text" key and the text value.
        block_size (int): The block size.

    Returns:
        dict: A dict containing input ids, token type ids and attention masks with sizes corresponding to the `block_size`.
    """

    # Concatenate all texts.
    concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
    total_length = len(concatenated_examples[list(examples.keys())[0]])

    # We drop the small remainder, we could add padding if the model supported it instead of this drop, you can
    # customize this part to your needs.
    total_length = (total_length // block_size) * block_size

    # Split by chunks of max_len.
    result = {
        k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
        for k, t in concatenated_examples.items()
    }
    result["labels"] = result["input_ids"].copy()
    return result


if __name__ == "__main__":
    main()
