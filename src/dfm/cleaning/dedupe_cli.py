"""
A general script for deduplicating iterable text documents

Usage:
    python dedupe_cli.py path=<path_to_dataset> --config <path_to_config>

Where <path_to_dataset> can include wildcards, e.g.:
    python clean.py path=/path/to/dataset/*.parquet save_dir=/path/to/save_dir

This will deduplicate all parquet files in the dataset directory and save the
deduplicated data to the save_dir directory with the same name as the original file
with a metadata column "is_duplicate" added.

If the dataset has a columns with the name "passed_quality_filter" then this will be
used to filter out documents that did not pass the quality filter.

Authors:
    - Kenneth Enevoldsen <kennethcenevoldsen@gmail.com>
"""

import logging
import multiprocessing as mp
from glob import glob
from pathlib import Path
from typing import Callable, Generator, Iterable, Union

import datasets
import hydra
import ndjson
from datasets import Dataset, load_dataset
from datasets.utils import disable_progress_bar
from omegaconf import DictConfig, OmegaConf
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from dfm.cleaning import Deduper

CFG_PATH = Path(__file__).parent / "configs"
VALID_SAVE_FORMATS = {
    "parquet": "parquet",
    "json": "json",
    "jsonl": "json",
    "ndjson": "json",
    "csv": "csv",
    "arrow": "arrow",
}


def multigen(gen_func: Callable) -> Callable:
    """A decorator for using a generator multiple times

    gen_func (Callable): A generator function

    Returns:
        A generator function that can be used multiple times
    """

    class _multigen:
        def __init__(self, *args, **kwargs):
            self.__args = args
            self.__kwargs = kwargs
            self.elements = []
            self.finished = False

        def initial_iter(self):
            """The initial iteration over the generator

            This saves the elements generated in the generator to a list
            """
            # This is the first time we are iterating over the generator
            self.elements = []
            for i in gen_func(*self.__args, **self.__kwargs):
                self.elements.append(i)
                yield i
            self.finished = True

        def __iter__(self):
            if self.finished:
                # If we have already iterated over the generator, return the
                # elements we have already generated
                return iter(self.elements)
            return self.initial_iter()

    return _multigen


def dataset_to_disk(
    dataset: Union[Dataset, Iterable[dict]], path: Path, ext: str, streaming: bool
) -> None:
    """Save a dataset to disk

    Args:
        dataset (Union[Dataset, Iterable[dict]]): The dataset to save
        path (Path): The path to save the dataset to
        ext (str): The file extension to save the dataset as
        streaming (bool): Whether to save the dataset in streaming mode

    Raises:
        ValueError: If the file extension is not supported
    """
    _ext = VALID_SAVE_FORMATS[ext]
    path = path.with_suffix(f".{ext}")
    if streaming and ext not in {"jsonl", "json"}:
        raise ValueError(
            f"Streaming is only supported for jsonl files not for {ext}. "
            "Please use a different save format."
        )
    if streaming:
        # write each row to path as a jsonl file
        with open(path, "w", encoding="utf-8") as file:
            writer = ndjson.writer(file, ensure_ascii=False)
            for row in dataset:
                writer.writerow(row)
        return

    if _ext == "parquet":
        dataset.to_parquet(path)
    elif _ext == "json":
        dataset.to_json(path)
    elif _ext == "csv":
        dataset.to_csv(path)
    elif _ext == "arrow":
        dataset.to_disk(path)
    else:
        raise ValueError(f"Unsupported save format {ext}")
    logging.info("\tSaved deduplicated dataset to %s", str(path.resolve()))


def create_dataset_generator(path: Union[Path, str]) -> Generator[dict, None, None]:
    """Create a generator that yields datasets from a path

    Args:
        path (Union[Path, str]): The path to the dataset

    Yields:
        dict: A dataset
    """
    # check file extension is json or jsonl
    ext = path.suffix[1:]
    if ext not in {"json", "jsonl"}:
        raise ValueError(
            "Only json and jsonl files are supported when use_huggingface_loader is"
            + f" False, not {ext}. Please use a different save format."
        )
    with open(path, "r") as file:  # pylint: disable=unspecified-encoding
        reader = ndjson.reader(file)

        for post in reader:
            yield post


def process_path(path: Union[Path, str], deduper: Deduper, cfg: DictConfig) -> None:
    """Deduplicate a single file and save the deduplicated data to disk

    Args:
        path (Union[Path, str]): The path to the dataset
        deduper (Deduper): The deduper to use
        cfg (DictConfig): The Hydra config

    Raises:
        ValueError: If the file extension is not supported
    """

    save_dir = Path(cfg.save_dir)
    save_path = save_dir / Path(path).name
    path = Path(path)
    logging.info("Processing %s", str(path.resolve()))
    file_ext = path.suffix
    ext = VALID_SAVE_FORMATS[file_ext[1:]]  # remove the "."
    if cfg.use_huggingface_loader:
        dataset = load_dataset(
            ext, data_files=str(path), split="train", streaming=cfg.streaming
        )
    else:
        dataset = multigen(create_dataset_generator)(path)

    if cfg.streaming or cfg.use_huggingface_loader:
        try:
            column_names = list(next(iter(dataset)).keys())
        except StopIteration:
            logging.warning("Dataset is empty, skipping: \n%s\n", str(path))
            return
    else:
        column_names = dataset.column_names

    logging.debug("The columns of the dataset is: \n %s", str(column_names))

    if (not cfg.keep_duplicates) and "passed_quality_filter" in column_names:
        info_str = (
            "'keep_duplicates' is set to False, therefore files"
            + " which did not pass the quality filter will also be removed."
        )
        logging.info(info_str)
        if cfg.verbosity_level == 2:
            len_before = len(dataset)

        if cfg.use_huggingface_loader:
            dataset_filtered = dataset.filter(
                lambda x: x["passed_quality_filter"] is True
            )
        else:
            dataset_filtered = (
                d for d in dataset if d["passed_quality_filter"] is True
            )

        if cfg.verbosity_level == 2:
            logging.debug("Filtered out %d documents", len_before - len(dataset))
        texts = (example["text"] for example in dataset_filtered)
    else:
        if "passed_quality_filter" in column_names:
            # create a text generator of texts which passed the quality filter
            texts = (
                example[cfg.text_col]
                for example in dataset
                if example["passed_quality_filter"] is True
            )
        else:
            texts = (example[cfg.text_col] for example in dataset)

    text_gen_w_unique_ids = ((str(path) + str(i), text) for i, text in enumerate(texts))

    depup_gen = deduper.deduplicate(
        text_gen_w_unique_ids,
        return_generator=True,
        overwrite=True,
        store_corpus_to_disk=False,
        store_mask_to_disk=False,
        store_lsh_cache_to_disk=False,
        store_config_to_disk=False,
        output_dir=path.parent / "duplicates",
    )

    # add dedupe meta data columns
    if cfg.keep_duplicates and "passed_quality_filter" in column_names:
        # add meta data columns
        is_dub_gen = (x["duplicate"] for x in depup_gen)
        is_dup = [
            next(is_dub_gen) if example["passed_quality_filter"] is True else None
            for example in dataset
        ]
        if cfg.use_huggingface_loader:
            dataset_dedup = dataset.add_column("is_duplicate", is_dup)
        else:
            dataset_dedup = (dict(d, is_duplicate=i) for d, i in zip(dataset, is_dup))
    else:
        # add dedupe meta data columns
        is_dup = [x["duplicate"] for x in depup_gen]
        if cfg.use_huggingface_loader:
            dataset_dedup = dataset.add_column("is_duplicate", is_dup)
        else:
            dataset_dedup = (dict(d, is_duplicate=i) for d, i in zip(dataset, is_dup))

    if not cfg.keep_duplicates:
        # filter out duplicates
        if cfg.use_huggingface_loader:
            dataset_deduplicated = dataset_dedup.filter(
                lambda x: x["is_duplicate"] is False
            )
        else:
            dataset_deduplicated = (
                d for d in dataset_dedup if d["is_duplicate"] is False
            )
    else:
        dataset_deduplicated = dataset_dedup

    # save dataset with new file extension
    dataset_to_disk(
        dataset_deduplicated, save_path, cfg.save_file_ext, streaming=cfg.streaming
    )


@hydra.main(
    config_path=CFG_PATH,
    config_name="default_dedupe_config.yaml",
    version_base="1.2",
)
def main(cfg: DictConfig) -> None:
    """Main function for deduplicating a dataset

    Args:
        cfg (DictConfig): The Hydra config
    """

    save_dir = Path(cfg.save_dir)
    save_dir.mkdir(exist_ok=True, parents=True)
    # set logging for huggingface datasets
    datasets.logging.set_verbosity_error()
    disable_progress_bar()
    # set logging
    if cfg.verbosity_level == 0:
        logging.basicConfig(level=logging.ERROR)
    if cfg.verbosity_level == 1:
        logging.basicConfig(filename=save_dir / "deduplication.log", level=logging.INFO)
    if cfg.verbosity_level == 2:
        logging.basicConfig(
            filename=save_dir / "deduplication.log", level=logging.DEBUG
        )

    # save config to folder
    with open(save_dir / "deduplication_config.yaml", "w", encoding="utf-8") as file:
        OmegaConf.save(cfg, file)

    if cfg.num_proc == -1:
        num_proc = mp.cpu_count() - 1
    else:
        num_proc = cfg.num_proc

    paths = glob(cfg.path)
    paths = [
        path for path in paths if not path.endswith("_meta.jsonl")
    ]  # remove meta files from clean_cli

    # create deduper
    verbose = False
    if cfg.verbosity_level == 2:
        verbose = True
    deduper = Deduper(
        split_method=cfg.deduper.split_method,
        ngram_size=cfg.deduper.ngram_size,
        ngram_stride=cfg.deduper.ngram_stride,
        similarity_threshold=cfg.deduper.similarity_threshold,
        num_minhashes=cfg.deduper.num_minhashes,
        batch_size=cfg.batch_size,
        n_jobs=num_proc,
        random_seed=cfg.seed,
        verbose=verbose,
    )

    # add tqdm to path
    files = tqdm(paths, desc="files")

    with logging_redirect_tqdm():
        for path in files:
            # load dataset
            process_path(path, deduper, cfg)

    logging.info("Finished deduplicating %d files", len(paths))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
