"""Class that deduplicates an iterable corpus.

The deduplication is based on the MinHash algorithm [1].

Author:
    Dan Saattrup Nielsen (saattrupdan@gmail.com)

References:
    [1] Broder, Andrei Z. "On the resemblance and containment of documents."
        Proceedings. Compression and Complexity of SEQUENCES 1997
        (Cat. No. 97TB100171). IEEE, 1997.
"""

from datasketch import MinHash, LeanMinHash, MinHashLSH
from datasets.arrow_dataset import Dataset
from datasets.iterable_dataset import IterableDataset
from typing import Union, Iterable, Optional
from pathlib import Path
import json
from unicodedata import normalize
import re
from tqdm.auto import tqdm
from typing import Callable


def _default_normalization(doc: str) -> str:
    """NFKC normalise document and remove punctuation

    Args:
        doc (str): The document to normalize.
    Returns:
        doc (str): The normalized document.
    """
    doc = normalize("NFKC", doc)
    doc = re.sub(r"[\.\,\:\;\!\?\(\)\[\]\{\}]", " ", doc)
    return re.sub(" +", " ", doc)


class Deduper:
    """Class that deduplicates an iterable corpus.

    The deduplication is based on the MinHash algorithm [1].

    Args:
        split_method (str or None, optional):
            The method to split the documents into shingles. Can be either
            'char_ngram', 'word_ngram', 'paragraph', 'none' or None. Here
            'none' or None means that a document is not split up at all.
            Defaults to 'char_ngram'.
        ngram_size (int, optional):
            The size of the ngram shingles. Only relevant if `split_method` is
            'char_ngram' or 'word_ngram'. Defaults to 13.
        ngram_stride (int, optional):
            The stride of the ngram shingles. Only relevant if `split_method`
            is 'char_ngram' or 'word_ngram'. Defaults to 1, corresponding to no
            stride.
        similarity_threshold (float, optional):
            The similarity threshold to use for the MinHash functions.
            Defaults to 0.8.
        num_minhashes (int, optional):
            The number of MinHash functions to use. Defaults to 128.
        random_seed (int, optional):
            The random seed to use for the MinHash functions. Defaults to 42.
        normalization_func: (Callable[[str], str], optional):
            The function used to normalize documents before they are compared to
            ignore insignificant differences.
        verbose (bool, optional):
            Print progress to stdout. Defaults to True.

    Attributes:
        split_method (str): The splitting method for extracting shingles.
        ngram_size (str): The size of the ngram shingles.
        ngram_stride (str): The stride used for the ngram shingles.
        similarity_threshold (float): The Jaccard similarity threshold.
        num_minhashes (int): The number of MinHash functions to use.
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
        split_method: Optional[str] = "char_ngram",
        ngram_size: int = 13,
        ngram_stride: int = 1,
        similarity_threshold: float = 0.8,
        num_minhashes: int = 128,
        random_seed: int = 42,
        normalization_func: Callable[[str], str] = _default_normalization,
        verbose: bool = True,
    ):
        self.split_method = "none" if split_method is None else split_method
        self.ngram_size = ngram_size
        self.ngram_stride = ngram_stride
        self.similarity_threshold = similarity_threshold
        self.num_minhashes = num_minhashes
        self.random_seed = random_seed
        self.normalization_func = normalization_func
        self.verbose = verbose

    def deduplicate(
        self,
        corpus: Union[Dataset, IterableDataset, Iterable[str]],
        output_fname: Union[str, Path] = "deduplicated.jsonl",
        overwrite: bool = False,
    ):
        """Removes duplicate documents from the corpus and stores it to disk.

        Args:
            corpus (Dataset, IterableDataset or iterable of strings):
                The corpus to deduplicate.
            output_fname (str or Path, optional):
                The name of the output file.
            overwrite (bool, optional):
                Whether to overwrite the output file if it already exists.
                Defaults to False.

        Raises:
            FileExistsError:
                If the output file already exists and `overwrite` is False.
        """
        # Convert corpus to an iterable of strings if a Dataset is given
        if isinstance(corpus, Dataset) or isinstance(corpus, IterableDataset):
            corpus = (sample["text"] for sample in corpus)

        # Ensure that `output_fname` is a Path object
        output_fname = Path(output_fname)

        # If the output file already exists then raise an error if `overwrite`
        # is False and otherwise delete the file
        if output_fname.exists():
            if overwrite:
                output_fname.unlink()
            else:
                raise FileExistsError(f"Output file {output_fname} " f"already exists.")

        # Initialise the LSH cache
        cache = MinHashLSH(
            threshold=self.similarity_threshold, num_perm=self.num_minhashes
        )

        # Iterate over the corpus and store documents that are not duplicates
        duplicates = 0
        with tqdm(corpus, desc="Deduplicating", disable=not self.verbose) as pbar:
            for doc_idx, doc in enumerate(pbar):

                # Compute the fingerprint for the document
                minhash = self._get_minhash(doc)

                # If the document is not a near-duplicate then store in the LSH
                # cache and append it to the JSONL output file
                if len(cache.query(minhash)) == 0:
                    cache.insert(doc_idx, minhash)
                    self._store_document(doc_idx=doc_idx, doc=doc, output_fname=output_fname)

                # Otherwise, increment the number of duplicate documents
                else:
                    duplicates += 1

                #  Update the progress bar description with the number of
                # duplicates found so far
                pct_duplicated = 100 * duplicates / (1 + doc_idx)
                desc = (
                    f"Deduplicating - {pct_duplicated:.2f}% "
                    f"duplicates or near-duplicates found"
                )
                pbar.set_description(desc)

    def _get_minhash(self, doc: str) -> LeanMinHash:
        """Returns a minhash fingerprint for the given document.

        Args:
            doc (str): The document to create the MinHash object for.

        Returns:
            LeanMinHash: The minhash fingerprint for the given document.
        """
        # Normalize the document to ignore insignificant differences
        doc = self.normalization_func(doc)

        # Initialise the fingerprint
        minhash = MinHash(num_perm=self.num_minhashes, seed=self.random_seed)

        # Add all shingles of the document to the fingerprint
        for shingle in self._extract_shingles(doc):
            minhash.update(shingle.encode("utf-8"))

        # Convert the fingerprint to a LeanMinHash fingerprint, to save memory
        # and increase performance
        minhash = LeanMinHash(minhash, seed=self.random_seed)

        # Return the fingerprint
        return minhash

    def _extract_shingles(self, doc: str):
        """Extract shingles from the document, depending on the `split_method`

        Args:
            doc (str): The document to extract shingles from.

        Returns:
            shingles (list): A list of shingles the document has been split into.

        Raises:
            ValueError:
                If `self.split_method` is not 'char_ngram', 'word_ngram',
                'paragraph' or 'none'.
        """
        if self.split_method == "char_ngram":
            max_char_idx = 1 + len(doc) - self.ngram_size
            return [
                doc[i : i + self.ngram_size]
                for i in range(0, max_char_idx, self.ngram_stride)
            ] or [doc]
        elif self.split_method == "word_ngram":
            words = [word for word in doc.split(" ") if len(word) > 0]
            max_word_idx = 1 + len(words) - self.ngram_size
            return [
                " ".join(words[i : i + self.ngram_size]).strip()
                for i in range(0, max_word_idx, self.ngram_stride)
            ] or [doc]
        elif self.split_method == "paragraph":
            return [p for p in doc.split("\n") if len(p) > 0]
        elif self.split_method == "none":
            return [doc]
        else:
            raise ValueError(f"Invalid split method: {self.split_method}")

    def _store_document(
        self, doc_idx: Union[str, int], doc: str, output_fname: Union[str, Path]
    ):
        """Appends the document to a JSONL file.

        Args:
            doc_idx (str or int): The document index.
            doc (str): The document to append to the JSONL file.
            output_fname (str or Path): The name of the JSONL file to append to.
        """
        # Ensure that `doc_idx` is a string
        doc_idx = str(doc_idx)

        # Ensure that `output_fname` is a Path object
        output_fname = Path(output_fname)

        # Append the document to the JSONL file
        with output_fname.open("a") as f:
            jsonned = json.dumps(dict(id=doc_idx, text=doc))
            f.write(jsonned + "\n")


if __name__ == "__main__":
    from datasets import load_dataset

    corpus = load_dataset(
        "DDSC/partial-danish-gigaword-no-twitter", streaming=True, split="train"
    )
    deduper = Deduper(split_method="none")
    deduper.deduplicate(corpus, output_fname="deduplicated.jsonl")
