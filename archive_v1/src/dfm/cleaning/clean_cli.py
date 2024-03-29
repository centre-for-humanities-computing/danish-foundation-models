"""
A general script for cleaning iterable text documents

Usage:
    python clean_cli.py path=<path_to_dataset> --config <path_to_config>

Where <path_to_dataset> can include wildcards, e.g.:
    python clean_cli.py path=/path/to/dataset/*.parquet save_dir=/path/to/save_dir
    --config /path/to/config.yaml

This will clean all parquet files in the dataset directory and save the cleaned
data to the save_dir directory with the same name as the original file along with a
meta_data file containing file ID's along with cleaning meta_data with the default suffix
of <filename>_meta.jsonl

Authors:
    - Kenneth Enevoldsen <kennethcenevoldsen@gmail.com>
"""

import logging
import multiprocessing as mp
from functools import partial
from glob import glob
from pathlib import Path

import datasets
import hydra
from datasets import load_dataset
from datasets.utils import disable_progress_bar
from dfm.cleaning import QualityFilter, SentenceFilter
from omegaconf import DictConfig, OmegaConf
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

CFG_PATH = Path(__file__).parent / "configs"
VALID_SAVE_FORMATS = {
    "parquet": "parquet",
    "json": "json",
    "jsonl": "json",
    "ndjson": "json",
    "csv": "csv",
    "arrow": "arrow",
}


def create_quality_filter(cfg: DictConfig) -> QualityFilter:
    """Create a quality filter from a config

    Args:
        cfg (DictConfig): A config object containing the quality_filter config

    Returns:
        QualityFilter: A quality filter object
    """
    cfg = cfg.quality_filter

    qf = QualityFilter(
        min_stop_words=cfg.min_stop_words,
        mean_word_length=cfg.mean_word_length,
        doc_length=cfg.doc_length,
        alpha_ratio=cfg.alpha_ratio,
        symbol_2_word_hashtag=cfg.symbol_2_word_hashtag,
        symbol_2_word_ellipsis=cfg.symbol_2_word_ellipsis,
        max_p_begin_bullets=cfg.max_p_begin_bullets,
        max_p_end_ellipsis=cfg.max_p_end_ellipsis,
        min_bullets=cfg.min_bullets,
        min_ellipsis=cfg.min_ellipsis,
        duplicate_lines_chr_fraction=cfg.duplicate_lines_chr_fraction,
        duplicate_paragraph_chr_fraction=cfg.duplicate_paragraph_chr_fraction,
        top_ngram_chr_fraction_thresholds=cfg.top_ngram_chr_fraction_thresholds,
        top_ngram_chr_fraction_range=cfg.top_ngram_chr_fraction_range,
        top_ngram_min_count=cfg.top_ngram_min_count,
        duplicate_n_gram_fraction_thresholds=cfg.duplicate_n_gram_fraction_thresholds,
        duplicate_n_gram_fraction_range=cfg.duplicate_n_gram_fraction_range,
        max_length=cfg.max_length,
        string_filter=cfg.string_filter,
        language_detection_tool=cfg.language_detection_tool,
        language_threshold=cfg.language_threshold,
        languages=cfg.languages,
        short_long_sentence_length_split=cfg.short_long_sentence_length_split,
        short_long_sentence_threshold=cfg.short_long_sentence_threshold,
        ignore_filters=cfg.ignore_filters,
    )
    return qf


def create_sentence_filter(cfg: DictConfig) -> SentenceFilter:
    """Create a sentence filter from a config

    Args:
        cfg (DictConfig): A config object containing the sentence_filter config

    Returns:
        SentenceFilter: A sentence filter object
    """
    cfg = cfg.sentence_filter
    sf = SentenceFilter(
        filter_names=cfg.filter_names,
        title_cased_words_threshold=cfg.title_cased_words_threshold,
        min_num_words=cfg.min_num_words,
        curly_brackets_threshold=cfg.curly_brackets_threshold,
        n_jobs=1,
    )
    return sf


def apply_quality_filter(batch: dict, cfg: DictConfig) -> dict:
    """
    Apply quality filter to huggingface datasets batch. Does not apply to texts
    that are already filtered out.

    Args:
        batch (dict): A hf datasets batch
        cfg (DictConfig): A config object containing the quality_filter config

    Returns:
        dict: A hf datasets batch
    """
    qf = create_quality_filter(cfg)

    if cfg.save_meta_data:
        valid_langs = set(cfg.valid_languages)
        if valid_langs:

            def filter_lang(batch, i):
                return (
                    batch[cfg.lang_col][i] in valid_langs
                    and batch["passed_sentence_filter"]
                )

        else:

            def filter_lang(batch, i):
                return batch["passed_sentence_filter"]

        # Filter out all texts that do not pass the filters
        is_filtered = [filter_lang(batch, i) for i, _ in enumerate(batch[cfg.text_col])]
        texts = (t for t, is_f in zip(batch[cfg.text_col], is_filtered) if is_f)

        # apply quality filter
        filter_gen = qf.describe_filter(texts, batch_size=cfg.batch_size)

        # merge with unfiltered texts
        merge_filter = [next(filter_gen) if is_f else None for is_f in is_filtered]
        batch["passed_quality_filter"] = [
            None if is_filtered_by is None else is_filtered_by == "passed filters"
            for is_filtered_by in merge_filter
        ]

        # add colums for specific filters
        #   manually add max_chr_length as it is an exception handling filter
        prev_filters = {None}
        batch["filtered_by_max_chr_length"] = [
            None if is_f in prev_filters else is_f == "max_chr_length"
            for is_f in merge_filter
        ]
        prev_filters.add("max_chr_length")

        # add metadata column for which filters the text was filtered by
        for qfilter in qf.filters:
            batch["filtered_by_" + qfilter] = [
                None if is_f in prev_filters else is_f == qfilter
                for is_f in merge_filter
            ]
            prev_filters.add(qfilter)
        return batch

    passed = [
        f == "passed filters"
        for f in qf.describe_filter(batch[cfg.text_col], batch_size=cfg.batch_size)
    ]
    # return batch with only the texts that passed the quality filter
    return {k: [v[i] for i, p in enumerate(passed) if p] for k, v in batch.items()}


def apply_sentence_filter(batch: dict, cfg: DictConfig) -> dict:
    """
    Apply sentence filter to a huggingface datasets batch

    Args:
        batch (dict): A hf datasets batch
        cfg (DictConfig): A config object containing the sentence_filter config

    Returns:
        dict: A hf datasets batch
    """
    sf = create_sentence_filter(cfg)

    if cfg.save_meta_data:
        valid_langs = set(cfg.valid_languages)

        if valid_langs:

            def filter_lang(batch, i):
                return batch[cfg.lang_col][i] in valid_langs

            is_filtered = [
                filter_lang(batch, i) for i, _ in enumerate(batch[cfg.text_col])
            ]
            texts = (t for t, is_f in zip(batch[cfg.text_col], is_filtered) if is_f)
            filtered_texts = sf(texts)
            # merge with unfiltered texts
            batch[cfg.text_col] = [
                next(filtered_texts) if is_f else None for is_f in is_filtered
            ]
        else:
            batch[cfg.text_col] = sf(batch[cfg.text_col])

        # create meta data columns
        batch["passed_sentence_filter"] = [bool(t) for t in batch[cfg.text_col]]
        return batch

    batch[cfg.text_col] = sf(batch[cfg.text_col])
    # remove text that are now empty strings
    return {
        k: [v[i] for i, t in enumerate(batch[cfg.text_col]) if t]
        for k, v in batch.items()
    }


def dataset_to_disk(dataset, path, ext: str) -> None:
    """Save a dataset to disk

    Args:
        dataset (Dataset): A huggingface dataset
        path (Path): A path to save the dataset to
        ext (str): The extension to save the dataset to
    """
    _ext = VALID_SAVE_FORMATS[ext]
    path = path.with_suffix(f".{ext}")
    if _ext == "parquet":
        dataset.to_parquet(path)
    elif _ext == "json":
        dataset.to_json(path)
    elif _ext == "csv":
        dataset.to_csv(path)
    elif _ext == "arrow":
        dataset.to_disk(path)
    else:
        raise ValueError(f"Invalid extension: {ext}")
    logging.info("\tSaved cleaned dataset to %s", path.resolve())


def process_files(path: Path, cfg: DictConfig) -> None:
    """Process a file or directory of files

    Args:
        path (Path): A path to a file or directory of files
        cfg (DictConfig): A config object containing the config for the
            sentence_filter and quality_filter
    """
    # load dataset
    file_ext = Path(path).suffix
    ext = VALID_SAVE_FORMATS[file_ext[1:]]  # remove the "."

    save_dir = Path(cfg.save_dir)
    save_path = save_dir / Path(path).name

    meta_data_cols = [
        cfg.id_col,
        cfg.lang_col,
        "passed_sentence_filter",
        "passed_quality_filter",
    ]

    _save_path = save_path.with_suffix(f".{cfg.save_file_ext}")
    if _save_path.exists() and cfg.skip_existing:
        logging.info("File already existing, skipping:\n\t %s", _save_path)
        return

    dataset = load_dataset(ext, data_files=path, split="train")
    if cfg.verbosity_level == 2:
        logging.debug("The columns of the dataset is:\n %s", dataset.column_names)

    # filter languages:
    if not cfg.save_meta_data and cfg.valid_languages and cfg.lang_col:
        valid_langs = set(cfg.valid_languages)
        dataset.filter(lambda example: example[cfg.lang_col] in valid_langs)

    if cfg.apply_sentence_filter:
        dataset = dataset.map(
            lambda batch: apply_sentence_filter(batch, cfg),
            batched=True,
            batch_size=cfg.batch_size,
        )
    if cfg.apply_quality_filter:
        dataset = dataset.map(
            lambda batch: apply_quality_filter(batch, cfg),
            batched=True,
            batch_size=cfg.batch_size,
        )

    if cfg.save_meta_data:
        # subset meta data
        columns_to_remove = [
            c
            for c in dataset.column_names
            if (c not in meta_data_cols) and (not c.startswith("filtered_by_"))
        ]
        meta = dataset.remove_columns(columns_to_remove)
        # save meta
        meta_path = save_dir / (Path(path).stem + "_meta.jsonl")
        meta.to_json(meta_path)
        logging.info("\tSaved meta data to %s", meta_path.resolve())

    # remove meta data columns
    columns_to_remove = [
        c for c in dataset.column_names if c.startswith("filtered_by_")
    ]
    dataset = dataset.remove_columns(columns_to_remove)

    # save dataset with new file extension
    dataset_to_disk(dataset, save_path, cfg.save_file_ext)


@hydra.main(
    config_path=CFG_PATH,
    config_name="default_clean_config.yaml",
    version_base="1.2",
)
def main(cfg: DictConfig) -> None:
    """Main function for cleaning a dataset.

    Args:
        cfg (DictConfig): A config object containing the config for the
            sentence_filter and quality_filter
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
        logging.basicConfig(filename=save_dir / "cleaning.log", level=logging.INFO)
    if cfg.verbosity_level == 2:
        logging.basicConfig(filename=save_dir / "cleaning.log", level=logging.DEBUG)
    # save config to folder
    with open(save_dir / "clean_config.yaml", "w", encoding="utf-8") as f:
        OmegaConf.save(cfg, f)

    num_proc = mp.cpu_count() - 1 if cfg.num_proc == -1 else cfg.num_proc

    paths = glob(cfg.path)

    # check save path file extension
    if cfg.save_file_ext not in VALID_SAVE_FORMATS:
        raise ValueError(
            f"Invalid save path file extension. Must be one of {VALID_SAVE_FORMATS}",
        )

    # group paths in batches
    files = tqdm(paths, desc="files")

    _process_files = partial(process_files, cfg=cfg)
    with logging_redirect_tqdm(), mp.Pool(num_proc) as pool:
        # process files in parallel
        for _ in pool.imap_unordered(_process_files, files, chunksize=1):
            pass

    logging.info("Finished cleaning %s files", len(paths))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
