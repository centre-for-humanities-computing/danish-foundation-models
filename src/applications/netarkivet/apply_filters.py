"""
Apply deduplication and quality filter to NetArkivet Text Corpus (NAT).

Dependent on:
    src/applications/netarkivet/add_duplicate_column.py

Authors:
    Kenneth Enevoldsen
"""
from typing import Iterable, Optional, List, Union
from pathlib import Path
import glob
import random
from contextlib import ExitStack
import os

import ndjson
from wasabi import msg


def shuffle_buffer(x: Iterable, buffer_size: int) -> Iterable:
    """Creates shuffle buffer from iterable.
    
    Args:
        x (Iterable): An iterable you want shuffled
        buffer_size (int): The buffer shuffle
    
    Returns:
        Iterable: An iterable which is shuffled using a shuffle buffer
    
    Example:
        >>> shuffled = shuffle_buffer(x =[1,2, 3, 4, 5], buffer_size=2)
        >>> print(list(shuffled))
        [2, 1, 4, 3, 5]
    """
    iter_x = iter(x)

    shufbuf = []
    try:
        for i in range(buffer_size):
            shufbuf.append(next(iter_x))
    except StopIteration:
        buffer_size = len(shufbuf)

    while True:
        try:
            item = next(iter_x)
            i = random.randint(0, buffer_size - 1)
            yield shufbuf[i]
            shufbuf[i] = item
        except StopIteration:
            break
    while shufbuf:
        yield shufbuf.pop()


def jsonl_merge(
    jsonl_files: List[Union[Path, str]],
    buffer_size: Optional[int] = None,
    sample: bool = True,
) -> Iterable[dict]:
    """
    Merge a list of jsonl files into an iterable of json objects

    Args:
        json_files (List[Union[Path, str]]): A list of jsonl or ndjson file paths.
        buffer_size (Optional[int], optional): Buffer size. I specified add a shuffle
            buffer with the defined buffer size. Default to None.
        sample (bool, optional): Should the iterable sample from the json files (True)
            or should it read then in order? Defaults to True.
    """

    def __sample_yield(readers: list) -> Iterable:
        while readers:
            i = random.randint(0, len(readers) - 1)
            reader = readers[i]
            try:
                yield next(reader)
            except StopIteration:
                readers.pop(i)

    def __iterative_yield(readers: list) -> Iterable:
        for reader in readers:
            for sample in reader:
                yield sample

    yield_fn = __sample_yield if sample is True else __iterative_yield

    if buffer_size:
        json_gen = shuffle_buffer(
            jsonl_merge(jsonl_files=jsonl_files, buffer_size=None, sample=sample),
            buffer_size=buffer_size,
        )
        for sample in json_gen:
            yield sample
    else:
        with ExitStack() as stack:
            files = [stack.enter_context(open(filename)) for filename in jsonl_files]
            readers = [ndjson.reader(f) for f in files]

            for sample in yield_fn(readers):
                yield sample


def apply_filter(dataset=Iterable[dict], columns_to_keep=["text"]) -> Iterable[dict]:
    for sample in dataset:
        if sample["is_duplicate"] is False:
            yield {k: sample[k] for k in columns_to_keep}


def main(
    netarkivet_path=Path("/work/netarkivet-cleaned"),
    write_folder=Path("/work/netarkivet-cleaned"),
    buffer_size=1_000_000,
):
    for year in range(2006, 2017):
        msg.info(f"starting year: {year}")
        path = netarkivet_path / str(year) / "*.jsonl"
        write_path = write_folder / f"{year}_deduplicated_filtered.jsonl"
        if os.path.exists(write_path):
            msg.warn(f"\tFile already exists - skipping: {write_path}")
            continue

        jsonl_files = glob.glob(str(path))

        json_gen = jsonl_merge(jsonl_files, sample=True, buffer_size=buffer_size)

        json = next(json_gen)
        json_gen_filtered = apply_filter(json_gen)

        msg.info("\tWriting to disk")
        with open(write_path, "w") as f:
            writer = ndjson.writer(f)
            for json in json_gen_filtered:
                writer.writerow(json)


if __name__ == "__main__":
    main()
