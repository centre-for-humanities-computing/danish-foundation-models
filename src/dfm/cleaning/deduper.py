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
        batch_size (int or None, optional):
            The number of documents to process at a time. If None then it is
            set to 10,000 if `split_method` is 'paragraph', 'none' or None,
            and 1,000 if `split_method` is 'word_ngram'. Defaults to None.
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
        batch_size: Optional[int] = None,
        n_jobs: int = -1,
        random_seed: int = 42,
        normalization_func: Callable[[str], str] = default_normalization,
        verbose: bool = True,
    ):
        self.split_method = "none" if split_method is None else split_method
        self.ngram_size = ngram_size
        self.ngram_stride = ngram_stride
        self.similarity_threshold = similarity_threshold
        self.num_minhashes = num_minhashes
        self.n_jobs = mp.cpu_count() if n_jobs == -1 else n_jobs
        self.random_seed = random_seed
        self.normalization_func = normalization_func
        self.verbose = verbose
        self.mask = list()
        self.lsh_cache = MinHashLSH(
            threshold=self.similarity_threshold, num_perm=self.num_minhashes
        )

        if batch_size is None:
            if self.split_method in ["paragraph", "none"] or self.split_method is None:
                self.batch_size = 10_000
            elif self.split_method == "word_ngram":
                self.batch_size = 1_000
            else:
                raise ValueError(
                    f"Invalid split_method: {self.split_method}. "
                    "Valid values are 'word_ngram', 'paragraph', 'none' and None."
                )
        else:
            self.batch_size = batch_size

    def reset(self):
        """Reset the deduplicator, removing the mask and the LSH cache"""
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

        # Load the mask
        with open(directory / "mask.jsonl", "r") as f:
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
        output_dir: Union[str, Path] = "deduplicated",
        overwrite: bool = False,
        store_mask: bool = False,
    ):
        """Removes duplicate documents from the corpus and stores it to disk.

        Args:
            corpus (Dataset, IterableDataset, iter of tuples or dicts):
                The corpus to deduplicate. If it is a Dataset or
                IterableDataset then it must have an `id` column and a `text`
                column. If it is an iterable of tuples then the first entry
                must be the document id and the second entry must be the
                document text. If it is an iterable of dicts then the keys must
                be `id` and `text`. The document ID in all cases can be either
                an integer or a string.
            output_dir (str or Path, optional):
                The name of the output directory. Defaults to 'deduplicated'.
            overwrite (bool, optional):
                Whether to overwrite the output file if it already exists.
                Defaults to False.
            store_mask (bool, optional):
                Whether to store the mask to disk. Defaults to False.

        Raises:
            FileExistsError:
                If the output file already exists and `overwrite` is False.
        """
        # Register number of documents in the corpus
        num_docs = len(corpus) if hasattr(corpus, "__len__") else None

        # If the corpus is a Dataset or IterableDataset then convert it to an
        # iterable of tuples
        if isinstance(corpus, Dataset) or isinstance(corpus, IterableDataset):
            corpus = (
                (sample["id"], sample["text"])
                for sample in corpus
                if sample["id"] not in [i for i, _ in self.mask]
            )

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
                corpus = (
                    (sample["id"], sample["text"])
                    for sample in corpus
                    if sample["id"] not in [i for i, _ in self.mask]
                )

        # Ensure that `output_dir` is a Path object
        output_dir = Path(output_dir)

        # If the output file already exists then raise an error if `overwrite`
        # is False and otherwise delete the file
        if output_dir.exists():
            if overwrite:
                shutil.rmtree(output_dir)
            else:
                raise FileExistsError(f"Output directory {output_dir} already exists.")

        # Create the output directory
        output_dir.mkdir(parents=True)

        # Set up paths
        output_path = output_dir / "deduplicated_corpus.jsonl"
        mask_path = output_dir / "mask.jsonl"
        lsh_cache_path = output_dir / "lsh_cache.pkl"
        config_path = output_dir / "config.pkl"

        # Store the deduper config to disk
        config = self.get_config()
        with config_path.open("wb") as f:
            pickle.dump(config, f)

        #  Split the corpus into batches of `self.batch_size` documents
        batches = mit.ichunked(corpus, self.batch_size)

        # Iterate over the corpus and store documents that are not duplicates
        duplicates = 0
        num_processed = 0
        pbar_params = dict(
            desc="Deduplicating", total=num_docs, disable=(not self.verbose)
        )
        with tqdm(batches, **pbar_params) as pbar:

            # Initialise the multiprocessing
            with Parallel(n_jobs=self.n_jobs) as parallel:
                fn = delayed(partial(get_minhash,
                                     normalization_func=self.normalization_func,
                                     split_method=self.split_method,
                                     ngram_size=self.ngram_size,
                                     num_minhashes=self.num_minhashes,
                                     random_seed=self.random_seed))

                # Iterate over the batches
                for batch in pbar:

                    # Create a copy of the batch to ensure that we're not
                    # modifying the original
                    batch, batch_copy = it.tee(batch)

                    # Compute the fingerprint for the document
                    with tqdm(batch, total=self.batch_size, leave=False) as pb:
                        minhashes = parallel(fn(doc) for _, doc in pb)

                    # Iterate over the minhashes
                    for (doc_idx, doc), minhash in zip(batch_copy, minhashes):

                        # If the document is not a near-duplicate candidate then
                        # store in the LSH cache and append it to the JSONL output
                        # file
                        candidates = self.lsh_cache.query(minhash)
                        if len(candidates) == 0:

                            # Insert the document into the LSH cache
                            self.lsh_cache.insert(doc_idx, minhash)

                            # Store the non-duplicate document in the JSONL output
                            self._store_document(
                                id=doc_idx, text=doc, output_path=output_path
                            )

                            # Add the current document to the Boolean mask
                            mask_entry = dict(id=doc_idx, duplicate=False)
                            self.mask.append(mask_entry)

                        # Otherwise, increment the number of duplicate documents
                        else:
                            duplicates += 1

                            # Add the current document to the Boolean mask
                            mask_entry = dict(id=doc_idx, duplicate=True)
                            self.mask.append(mask_entry)

                        # Store the Boolean mask to disk
                        if store_mask:
                            self._store_document(output_path=mask_path, **mask_entry)

                    # Store the LSH cache to disk
                    with lsh_cache_path.open("wb") as f:
                        pickle.dump(self.lsh_cache, f)

                    # Update the number of documents processed
                    num_processed += self.batch_size

                    # Update the progress bar
                    pbar.update(self.batch_size)
                    pct_duplicated = 100 * duplicates / num_processed
                    desc = f"Deduplicating - {pct_duplicated:.2f}% near-duplicates found"
                    pbar.set_description(desc)


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
    ).rename_column('doc_id', 'id')

    #  Deduplicate the test dataset
    deduper = Deduper(split_method=args.split_method, n_jobs=args.n_jobs)
    deduper.deduplicate(corpus, output_dir=output_dir)

    # *** Time taken to deduplicate DAGW with 16 cores, by `split_method` ***
    #   - 'none': ~3.5 minutes (found 24.75% duplicates)
    #   - 'paragraph': ~4 minutes (found 25.83% duplicates)
    #   - 'word_ngram' with n == 13: ~16 minutes (found 31.49% duplicates)
