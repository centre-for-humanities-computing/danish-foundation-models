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

import hydra
import ndjson
from datasets import Dataset, load_dataset
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


def dataset_to_disk(dataset: Dataset, path: Path, ext: str, streaming: bool):
    """Save a dataset to disk"""
    _ext = VALID_SAVE_FORMATS[ext]
    path = path.with_suffix(f".{ext}")
    if streaming and not ext != "jsonl":
        raise ValueError(
            "Streaming is only supported for jsonl files. "
            "Please use a different save format."
        )
    elif streaming:
        # write each row to path as a jsonl file
        with open(path, "w", encoding="utf-8") as file:
            writer = ndjson.writer(file, ensure_ascii=False)
            for row in dataset:
                writer.writerow(row)

    elif _ext == "parquet":
        dataset.to_parquet(path)
    elif _ext == "json":
        dataset.to_json(path)
    elif _ext == "csv":
        dataset.to_csv(path)
    elif _ext == "arrow":
        dataset.to_disk(path)
    logging.info("\tSaved deduplicated dataset to %s", str(path.resolve()))
    return path


def process_path(path: Path, deduper: Deduper, cfg: DictConfig) -> None:
    """Deduplicate a single file and save the deduplicated data to disk"""
    path = Path(path)
    file_ext = path.suffix
    ext = VALID_SAVE_FORMATS[file_ext[1:]]  # remove the "."
    dataset = load_dataset(
        ext, data_files=str(path), split="train", streaming=cfg.streaming
    )

    if cfg.streaming:
        column_names = list(next(iter(dataset)).keys())
    else:
        column_names = dataset.column_names

    logging.debug("The columns of the dataset is: \n %s", str(column_names))

    if cfg.keep_duplicates and "passed_quality_filter" in column_names:
        info_str = (
            "'keep_duplicates' is set to False, therefore files"
            + " which did not pass the quality filter will also be removed."
        )
        logging.info(info_str)
        if cfg.verbosity_level == 2:
            len_before = len(dataset)
        dataset = dataset.filter(lambda x: x["passed_quality_filter"])

        logging.debug("Filtered out %d documents", len_before - len(dataset))
        texts = dataset[cfg.text_col]
    else:
        if "passed_quality_filter" in column_names:
            # create a text generator of texts which passed the quality filter
            texts = (
                example["text"]
                for example in dataset
                if example["passed_quality_filter"]
            )
        else:
            texts = (example["text"] for example in dataset)

    depup_gen = deduper.deduplicate(
        enumerate(texts),
        return_generator=True,
        overwrite=True,
        store_corpus_to_disk=False,
        store_mask_to_disk=True,
        store_lsh_cache_to_disk=False,
        store_config_to_disk=False,
        output_dir="tmp_path",
    )

    # add dedupe meta data columns
    if cfg.keep_duplicates and "passed_quality_filter" in column_names:
        # add meta data columns
        is_dub_gen = (x["duplicate"] for x in depup_gen)
        is_dup = [
            next(is_dub_gen) if example["passed_quality_filter"] else None
            for example in dataset
        ]
        dataset.add_column("is_duplicate", is_dup)
    else:
        # add dedupe meta data columns
        is_dup = [x["duplicate"] for x in depup_gen]
        dataset.add_column("is_duplicate", is_dup)

    if not cfg.keep_duplicates:
        # filter out duplicates
        dataset = dataset.filter(lambda x: x["is_duplicate"] is False)

    # save dataset with new file extension
    path = dataset_to_disk(dataset, path, cfg.save_file_ext, streaming=cfg.streaming)


@hydra.main(
    config_path=CFG_PATH,
    config_name="default_dedupe_config.yaml",
    version_base="1.2",
)
def main(cfg: DictConfig) -> None:
    """Main function for deduplicating a dataset"""

    save_dir = Path(cfg.save_dir)
    save_dir.mkdir(exist_ok=True, parents=True)
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
    main()
