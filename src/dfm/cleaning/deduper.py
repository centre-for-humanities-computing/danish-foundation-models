"""Class that deduplicates a corpus.

The deduplication is based on the MinHash algorithm [1], which is optimised
using parallelism and vectorisation.

Author:
    Dan Saattrup Nielsen (saattrupdan@gmail.com)

References:
    [1] Broder, Andrei Z. "On the resemblance and containment of documents."
        Proceedings. Compression and Complexity of SEQUENCES 1997
        (Cat. No. 97TB100171). IEEE, 1997.
"""

from datasketch import MinHashLSH
from datasets.arrow_dataset import Dataset
from datasets.iterable_dataset import IterableDataset
from typing import Union, Iterable, Optional, Callable, Dict, Tuple
from pathlib import Path
import shutil
import json
from tqdm.auto import tqdm
import itertools as it
import more_itertools as mit
from joblib import Parallel, delayed
import multiprocessing as mp
import pickle
from functools import partial
from .deduper_utils import get_minhash, default_normalization


class Deduper:
    """Class that deduplicates an iterable corpus.

    The deduplication is based on the MinHash algorithm [1].

    Args:
        split_method (str or None, optional):
            The method to split the documents into shingles. Can be either
            'word_ngram', 'paragraph', 'none' or None. Here 'none' or None
            means that a document is not split up at all. Defaults to
            'word_ngram'.
        ngram_size (int, optional):
            The size of the ngram shingles. Only relevant if `split_method` is
            'word_ngram'. Defaults to 13.
        ngram_stride (int, optional):
            The stride of the ngram shingles. Only relevant if `split_method`
            is 'word_ngram'. Defaults to 1, corresponding to no stride.
        similarity_threshold (float, optional):
            The similarity threshold to use for the MinHash functions.
            Defaults to 0.8.
        num_minhashes (int, optional):
            The number of MinHash functions to use. Defaults to 128.
        batch_size (int, optional):
            The number of documents to process at a time.  Defaults to 100_000.
        n_jobs (int, optional):
            The number of parallel jobs to use. If set to -1 then all available
            cores are used. Defaults to -1.
        random_seed (int, optional):
            The random seed to use for the MinHash functions. Defaults to 42.
        normalization_func: (Callable[[str], str], optional):
            The function used to normalize documents before they are compared to
            ignore insignificant differences. Needs to be pickleable.
        verbose (bool, optional):
            Print progress to stdout. Defaults to True.

    Attributes:
        split_method (str): The splitting method for extracting shingles.
        ngram_size (str): The size of the ngram shingles.
        ngram_stride (str): The stride used for the ngram shingles.
        similarity_threshold (float): The Jaccard similarity threshold.
        num_minhashes (int): The number of MinHash functions to use.
        batch_size (int): The number of documents to process at a time.
        n_jobs (int): The number of parallel jobs to use.
        random_seed (int): The random seed to use for the MinHash functions.
        normalization_func (Callable): The function used for normalization.
        verbose (bool): Print progress to stdout.

    References:
        [1] Broder, Andrei Z. "On the resemblance and containment of documents."
            Proceedings. Compression and Complexity of SEQUENCES 1997
            (Cat. No. 97TB100171). IEEE, 1997.
    """

    def __init__(
        self,
        split_method: Optional[str] = "word_ngram",
        ngram_size: int = 13,
        ngram_stride: int = 1,
        similarity_threshold: float = 0.8,
        num_minhashes: int = 128,
        batch_size: int = 100_000,
        n_jobs: int = -1,
        random_seed: int = 42,
        normalization_func: Callable[[str], str] = default_normalization,
        save_mask: bool = True,
        verbose: bool = True,
    ):
        self.split_method = "none" if split_method is None else split_method
        self.ngram_size = ngram_size
        self.ngram_stride = ngram_stride
        self.similarity_threshold = similarity_threshold
        self.num_minhashes = num_minhashes
        self.batch_size = batch_size
        self.n_jobs = mp.cpu_count() if n_jobs == -1 else n_jobs
        self.random_seed = random_seed
        self.normalization_func = normalization_func
        self.verbose = verbose
        self.save_mask = save_mask
        if save_mask:
            self.mask = list()
        self.lsh_cache = MinHashLSH(
            threshold=self.similarity_threshold, num_perm=self.num_minhashes
        )

    def reset(self):
        """Reset the deduplicator, removing the mask and the LSH cache"""
        if self.save_mask:
            self.mask = list()
        self.lsh_cache = MinHashLSH(
            threshold=self.similarity_threshold, num_perm=self.num_minhashes
        )
        return self

    @classmethod
    def load_from_disk(cls, directory: Union[str, Path]) -> "Deduper":
        """Load a Deduper from disk.

        Args:
            directory (str or Path):
                The directory to load the Deduper from.

        Returns:
            Deduper:
                The Deduper loaded from disk.

        Raises:
            FileNotFoundError:
                If the directory does not exist.
        """
        # Ensure that `directory` is a Path
        directory = Path(directory)

        # Check if the directory exists, and raise an error if it doesn't
        if not directory.exists():
            raise FileNotFoundError(f"Directory {directory} does not exist.")

        # Load the config file
        with open(directory / "config.pkl", "rb") as f:
            config = pickle.load(f)

        # Create the Deduper
        deduper = cls(**config)

        # Load the mask if it exists
        mask_path = directory / "mask.jsonl"
        if mask_path.exists():
            with open(mask_path, "r") as f:
                mask = [json.loads(line) for line in f]
            deduper.mask = mask

        # Load the LSH cache
        with open(directory / "lsh_cache.pkl", "rb") as f:
            deduper.lsh_cache = pickle.load(f)

        # Return the Deduper
        return deduper

    def get_config(self) -> dict:
        """Get the configuration of the deduplicator.

        Returns:
            dict: The configuration of the deduplicator.
        """
        config = dict(
            split_method=self.split_method,
            ngram_size=self.ngram_size,
            ngram_stride=self.ngram_stride,
            similarity_threshold=self.similarity_threshold,
            num_minhashes=self.num_minhashes,
            batch_size=self.batch_size,
            n_jobs=self.n_jobs,
            random_seed=self.random_seed,
            normalization_func=self.normalization_func,
            verbose=self.verbose,
        )
        return config

    def _store_document(self, output_path: Union[str, Path], **kwargs):
        """Appends the document to a JSONL file.

        Args:
            output_path (str or Path):
                The name of the JSONL file to append to.
            **kwargs:
                The document to append to the JSONL file.
        """
        # Ensure that `path` is a Path object
        output_path = Path(output_path)

        # Append the document to the JSONL file
        with output_path.open("a") as f:
            jsonned = json.dumps(kwargs)
            f.write(jsonned + "\n")

    def deduplicate(
        self,
        corpus: Union[
            Dataset,
            IterableDataset,
            Iterable[Tuple[Union[str, int], str]],
            Iterable[Dict[str, Union[str, int]]],
        ],
        id_column: str = "id",
        text_column: str = "text",
        output_dir: Union[str, Path] = "deduplicated",
        overwrite: bool = False,
        store_corpus_to_disk: bool = True,
        store_mask_to_disk: bool = True,
        store_lsh_cache_to_disk: bool = True,
        store_config_to_disk: bool = True,
        return_generator: bool = False,
    ) -> Union[Iterable, None]:
        """Removes duplicate documents from the corpus.

        Args:
            corpus (Dataset, IterableDataset, iter of tuples or dicts):
                The corpus to deduplicate.
            id_column (str, optional):
                The name of the column in the corpus that contains the document
                IDs. Defaults to 'id'.
            text_column (str, optional):
                The name of the column in the corpus that contains the document
                texts. Defaults to 'text'.
            output_dir (str or Path, optional):
                The name of the output directory. Defaults to 'deduplicated'.
            overwrite (bool, optional):
                Whether to overwrite the output file if it already exists.
                Defaults to False.
            store_corpus_to_disk (bool, optional):
                Whether to store the corpus to disk. Defaults to True.
            store_mask_to_disk (bool, optional):
                Whether to store the mask to disk. Defaults to True.
            store_lsh_cache_to_disk (bool, optional):
                Whether to store the LSH cache to disk. Defaults to True.
            store_config_to_disk (bool, optional):
                Whether to store the configuration to disk. Defaults to True.
            return_generator (bool, optional):
                Whether to return a generator which yields the mask. Defaults
                to False.

        Returns:
            Iterable or None:
                If `return_generator` is True, then a generator which yields
                a dictionary with keys `id` and `duplicate`. Otherwise, None.

        Raises:
            FileExistsError:
                If the output file already exists and `overwrite` is False.
        """
        iterable = self._deduplicate(
            corpus=corpus,
            id_column=id_column,
            text_column=text_column,
            output_dir=output_dir,
            overwrite=overwrite,
            store_corpus_to_disk=store_corpus_to_disk,
            store_mask_to_disk=store_mask_to_disk,
            store_lsh_cache_to_disk=store_lsh_cache_to_disk,
            store_config_to_disk=store_config_to_disk,
            return_generator=return_generator,
        )
        if return_generator:
            return iterable
        else:
            for _ in iterable:
                pass

    def _deduplicate(
        self,
        corpus: Union[
            Dataset,
            IterableDataset,
            Iterable[Tuple[Union[str, int], str]],
            Iterable[Dict[str, Union[str, int]]],
        ],
        id_column: str = "id",
        text_column: str = "text",
        output_dir: Union[str, Path] = "deduplicated",
        overwrite: bool = False,
        store_corpus_to_disk: bool = True,
        store_mask_to_disk: bool = True,
        store_lsh_cache_to_disk: bool = True,
        store_config_to_disk: bool = True,
        return_generator: bool = False,
    ) -> Iterable:
        """Helper function for the `deduplicate` method.

        Args:
            corpus (Dataset, IterableDataset, iter of tuples or dicts):
                The corpus to deduplicate.
            id_column (str, optional):
                The name of the column in the corpus that contains the document
                IDs. Defaults to 'id'.
            text_column (str, optional):
                The name of the column in the corpus that contains the document
                texts. Defaults to 'text'.
            output_dir (str or Path, optional):
                The name of the output directory. Defaults to 'deduplicated'.
            overwrite (bool, optional):
                Whether to overwrite the output file if it already exists.
                Defaults to False.
            store_corpus_to_disk (bool, optional):
                Whether to store the corpus to disk. Defaults to True.
            store_mask_to_disk (bool, optional):
                Whether to store the mask to disk. Defaults to True.
            store_lsh_cache_to_disk (bool, optional):
                Whether to store the LSH cache to disk. Defaults to True.
            store_config_to_disk (bool, optional):
                Whether to store the configuration to disk. Defaults to True.
            return_generator (bool, optional):
                Whether to return a generator which yields the mask. Defaults
                to False.

        Yields:
            dict or None:
                A dictionary with keys `id` and `duplicate` if
                `return_generator` is True, and otherwise None.

        Raises:
            FileExistsError:
                If the output file already exists and `overwrite` is False.
        """
        # Register number of documents in the corpus
        num_docs = len(corpus) if hasattr(corpus, "__len__") else None

        # If the corpus is a Dataset or IterableDataset then convert it to an
        # iterable of tuples
        if isinstance(corpus, Dataset) or isinstance(corpus, IterableDataset):
            corpus = ((sample[id_column], sample[text_column]) for sample in corpus)

        # Otherwise we check if the corpus is an iterable of dictionaries, in
        # which case we also convert it to an iterable of tuples
        else:

            # Create a copy of the corpus to ensure that we're not modifying
            # the original, and extract the first element of the copy.
            corpus, corpus_copy = it.tee(corpus)
            sample = next(corpus_copy)

            # If the first element of the corpus is a dictionary then we
            # convert the corpus to an iterable of tuples
            if isinstance(sample, dict):
                corpus = ((sample[id_column], sample[text_column]) for sample in corpus)

        # Ensure that `output_dir` is a Path object
        output_dir = Path(output_dir)

        # If the output file already exists then raise an error if `overwrite`
        # is False and otherwise delete the file
        if output_dir.exists():
            if overwrite:

                # Delete the output directory
                shutil.rmtree(output_dir)

                # Create the output directory
                output_dir.mkdir(parents=True)

                # Store existing mask
                if self.save_mask and store_mask_to_disk:
                    mask_path = output_dir / "mask.jsonl"
                    mask_str = "\n".join(json.dumps(sample) for sample in self.mask)
                    with mask_path.open("w") as f:
                        f.write(mask_str)

                # Store existing LSH cache
                if store_lsh_cache_to_disk:
                    lsh_cache_path = output_dir / "lsh_cache.pkl"
                    with lsh_cache_path.open("wb") as f:
                        pickle.dump(self.lsh_cache, f)

                # Store existing configuration
                if store_config_to_disk:
                    config_path = output_dir / "config.pkl"
                    config = self.get_config()
                    with config_path.open("wb") as f:
                        pickle.dump(config, f)

            else:
                raise FileExistsError(
                    f"Output directory {output_dir} already exists."
                    "Please set `overwrite` to True to overwrite "
                    "the files. If you are loading an existing "
                    "Deduper from the directory then the previous "
                    "config, mask and LSH cache will still will "
                    "not be lost and will be stored in the directory."
                )

        # Create the output directory
        if not output_dir.exists() and (
            store_corpus_to_disk
            or store_lsh_cache_to_disk
            or store_mask_to_disk
            or store_config_to_disk
        ):
            output_dir.mkdir(parents=True)

        # Set up paths
        output_path = output_dir / "deduplicated_corpus.jsonl"
        mask_path = output_dir / "mask.jsonl"
        lsh_cache_path = output_dir / "lsh_cache.pkl"
        config_path = output_dir / "config.pkl"

        # Store the deduper config to disk
        if store_config_to_disk:
            config = self.get_config()
            with config_path.open("wb") as f:
                pickle.dump(config, f)

        #  Split the corpus into batches of `self.batch_size` documents
        batches = mit.ichunked(corpus, self.batch_size)

        # Iterate over the corpus and store documents that are not duplicates
        duplicates = 0
        num_processed = 0
        pbar_params = dict(
            desc="Deduplicating",
            total=num_docs,
            disable=(not self.verbose),
            leave=False,
        )
        with tqdm(batches, **pbar_params) as pbar:

            # Initialise the multiprocessing
            with Parallel(n_jobs=self.n_jobs) as parallel:

                # Define the function that will be called in parallel
                fn = delayed(
                    partial(
                        get_minhash,
                        normalization_func=self.normalization_func,
                        split_method=self.split_method,
                        ngram_size=self.ngram_size,
                        ngram_stride=self.ngram_stride,
                        num_minhashes=self.num_minhashes,
                        random_seed=self.random_seed,
                    )
                )

                # Iterate over the batches
                for batch in pbar:

                    # Create a copy of the batch to ensure that we're not
                    # modifying the original
                    batch, batch_copy = it.tee(batch)

                    # Compute size of the batch
                    new_num_processed = num_processed + self.batch_size
                    if num_docs is not None:
                        new_num_processed = min(new_num_processed, num_docs)
                    batch_size = new_num_processed - num_processed

                    # Define parameters used in batch progress bars
                    pbar_params = dict(
                        total=batch_size, leave=False, disable=(not self.verbose)
                    )

                    # Compute the fingerprint for the document
                    pbar_params["desc"] = "Computing minhashes"
                    with tqdm(batch, **pbar_params) as batch_pbar:
                        minhashes = parallel(fn(doc) for _, doc in batch_pbar)

                    # Iterate over the minhashes
                    pbar_params["desc"] = "Deduplicating batch"
                    with tqdm(batch_copy, **pbar_params) as batch_pbar:
                        for (idx, doc), minhash in zip(batch_pbar, minhashes):

                            # If the document is not a near-duplicate candidate
                            # then store in the LSH cache and append it to the
                            # JSONL output file
                            candidates = self.lsh_cache.query(minhash)
                            if len(candidates) == 0:

                                # Insert the document into the LSH cache
                                self.lsh_cache.insert(idx, minhash)

                                # Store the non-duplicate document in the JSONL
                                # output
                                if store_corpus_to_disk:
                                    self._store_document(
                                        id=idx, text=doc, output_path=output_path
                                    )

                                # Compute the mask for the document
                                mask_entry = dict(id=idx, duplicate=False)

                            # Otherwise, increment the number of duplicate
                            # documents
                            else:
                                duplicates += 1

                                # Compute the mask for the document
                                mask_entry = dict(id=idx, duplicate=True)

                            # Add the mask to the mask attribute
                            if self.save_mask:
                                self.mask.append(mask_entry)

                            # Yield the mask
                            if return_generator:
                                yield mask_entry

                            # Store the mask to disk
                            if store_mask_to_disk:
                                self._store_document(
                                    output_path=mask_path, **mask_entry
                                )

                    # Store the LSH cache to disk
                    if store_lsh_cache_to_disk:
                        with lsh_cache_path.open("wb") as f:
                            pickle.dump(self.lsh_cache, f)

                    # Update the number of documents processed, and compute the
                    # number of documents in the batch
                    num_processed = new_num_processed

                    # Update the progress bar
                    pbar.update(batch_size)
                    pct_duplicated = 100 * duplicates / num_processed
                    desc = (
                        f"Deduplicating - {pct_duplicated:.2f}% near-duplicates found"
                    )
                    pbar.set_description(desc)

        # Return final update
        if self.verbose:
            pct_duplicated = 100 * duplicates / num_processed
            print("Finished deduplicating corpus.")
            print(f"- {num_processed:,} documents processed.")
            print(f"- {pct_duplicated:.2f}% documents marked as duplicates.")


if __name__ == "__main__":
    from datasets import load_dataset
    from pathlib import Path
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--split_method", "-s", type=str, required=True)
    parser.add_argument("--n_jobs", type=int, default=-1)
    parser.add_argument("--streaming", action="store_true")
    args = parser.parse_args()

    # Set up path to store the deduplicated corpus
    output_dir = Path("deduplicated-test")

    # Remove the deduplicated corpus if it already exists
    if output_dir.exists():
        shutil.rmtree(output_dir)

    # Load the test dataset
    corpus = load_dataset(
        "DDSC/partial-danish-gigaword-no-twitter",
        streaming=args.streaming,
        split="train",
    )

    #  Deduplicate the test dataset
    deduper = Deduper(split_method=args.split_method, n_jobs=args.n_jobs)
    deduper.deduplicate(corpus, id_column="doc_id", output_dir=output_dir)

    # *** Time taken to deduplicate DAGW with 16 cores, by `split_method` ***
    #   - 'none': ~3.5 minutes (found 24.75% duplicates)
    #   - 'paragraph': ~4 minutes (found 25.83% duplicates)
    #   - 'word_ngram' with n == 13: ~10 minutes (found 25.77% duplicates)
