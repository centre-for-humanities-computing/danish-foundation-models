"""Data preprocessing script for Danish Foundation Models """
from typing import List


def preprocess_dataset(datasets: List[str], tokenizer, num_proc: int = 4):
    def tokenize_func(examples):
        return tokenizer(examples["text"])

    datasets = datasets.map(
        tokenize_func, batched=True, num_proc=num_proc, remove_columns=["text"]
    )

    datasets.shuffle()

    pass
