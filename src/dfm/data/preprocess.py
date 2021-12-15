"""Data preprocessing script for Danish Foundation Models """
from typing import List


def preprocess_dataset(datasets: List[str], tokenizer, num_proc: int = 4):
    def tokenize_func(examples):
        return tokenizer(examples["text"])

    datasets = datasets.map(
        tokenize_func, batched=True, num_proc=num_proc, remove_columns=["text"]
    )

    block_size = 128

    datasets = datasets.map(
        group_texts, batched=True, num_proc=num_proc, remove_columns=["text"]
    )

    datasets.shuffle()

    pass


def tokenize_func(examples):
    return tokenizer(examples["text"])


def group_texts(examples):
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
