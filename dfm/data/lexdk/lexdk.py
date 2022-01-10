'''Script to load the Lex.dk dataset'''

from pathlib import Path
from typing import Union
from datasets.arrow_dataset import Dataset
from datasets.features import Features, Value


def load_lexdk(path: Union[Path, str]) -> Dataset:
    '''Load the Lex.dk dataset as a Hugging Face Dataset object.

    Args:
        path (Union[Path, str]): Path to the JSONL file containing the dataset.

    Returns:
        Dataset: The loaded Hugging Face dataset.
    '''
    features = Features(dict(
        url=Value('string'),
        title=Value('string'),
        clarification=Value('string'),
        authors=[Value('string')],
        date=Value('string'),
        text=Value('string')
    ))
    return Dataset.from_json(path, features=features)


if __name__ == '__main__':
    dataset = load_lexdk('lexdk.jsonl')
    breakpoint()
