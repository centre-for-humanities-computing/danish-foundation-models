"""Data preprocessing script for Danish Foundation Models """
from typing import List, Union
from functools import partial
from datasets.arrow_dataset import Dataset
from transformers import AutoTokenizer
from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.tokenization_utils_fast import PreTrainedTokenizerFast
from dfm.data.load import dfm_load_dataset
from datasets import DatasetDict


def main():
    tokenizer = AutoTokenizer.from_pretrained("Maltehb/danish-bert-botxo")

    ds = dfm_load_dataset("DDSC/reddit-da")
    ds["train"] = ds["train"].select(range(1000))
    ds["test"] = ds["test"].select(range(1000))
    ds["val"] = ds["val"].select(range(1000))

    ds = preprocess_dataset(ds, tokenizer)


def preprocess_dataset(
    dataset: DatasetDict,
    tokenizer: Union[PreTrainedTokenizerFast, PreTrainedTokenizerBase],
    num_proc: int = 4,
    block_size: int = 512,
):

    for key in dataset.keys():
        cols = dataset[key].column_names
        cols.remove("text")
        dataset[key] = dataset[key].remove_columns(cols)
        # select the text column
        ##dataset[key] = dataset[key].map(
        #    select_column_, input_columns="text", remove_columns=dataset[key].column_names
        # )

    tokenize_func_ = partial(tokenize_func, tokenizer=tokenizer)
    dataset = dataset.map(
        tokenize_func_, batched=True, num_proc=num_proc, remove_columns=["text"]
    )
    group_texts_ = partial(group_texts, block_size=block_size)

    dataset = dataset.map(
        group_texts_,
        batched=True,
        batch_size=1000,
        num_proc=num_proc,
    )
    dataset.shuffle()

    return dataset


def select_column_(dataset: Dataset, column: str):
    return dataset[column]


def tokenize_func(examples, tokenizer):
    return tokenizer(examples["text"])


def group_texts(examples, block_size: int):
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
