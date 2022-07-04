"""Utility functions for the deduplicator.

Author:
    Dan Saattrup Nielsen (dan.nielsen@alexandra.dk)
"""

from datasketch import MinHash, LeanMinHash
from typing import List, Callable
from unicodedata import normalize
import re


def get_shingles(
    doc: str,
    normalization_func: Callable,
    split_method: str,
    ngram_size: int,
    ngram_stride: int,
) -> List[str]:
    """Extracts the shingles from a document.

    Args:
        doc (str):
            The document to extract the shingles from.
        normalization_func (Callable):
            The function to normalize the document with.
        split_method (str):
            The method to split the document into shingles.
            Can be 'word_ngram', 'paragraph', 'none' or None.
        ngram_size (int):
            The size of the ngrams to use.
        ngram_stride (int):
            The stride of the ngrams to use.

    Returns:
        list of str:
            The shingles extracted from the document.

    Raises:
        ValueError:
            If `split_method` is not 'word_ngram', 'paragraph', 'none'
            or None.
    """
    # Normalise document
    doc = normalization_func(doc)

    # Extract shingles from the document, depending on the `split_method`
    if split_method == "word_ngram":
        words = [word for word in doc.split(" ") if len(word) > 0]
        max_word_idx = 1 + len(words) - ngram_size
        shingles = [
            " ".join(words[i : i + ngram_size]).strip()
            for i in range(0, max_word_idx, ngram_stride)
        ] or [doc]
    elif split_method == "paragraph":
        shingles = [p for p in doc.split("\n") if len(p) > 0]
    elif split_method == "none" or split_method is None:
        shingles = [doc]
    else:
        raise ValueError(f"Invalid split method: {split_method}")

    return shingles


def get_minhash(
    doc: str,
    normalization_func: Callable,
    split_method: str,
    ngram_size: int,
    ngram_stride: int,
    num_minhashes: int,
    random_seed: int,
) -> LeanMinHash:
    """Returns a minhash fingerprint for the given document.

    Args:
        doc (str):
            The document to create the MinHash object for.
        normalization_func (Callable):
            The function to normalize the document with.
        split_method (str):
            The method to split the document into shingles.
            Can be 'word_ngram', 'paragraph', 'none' or None.
        ngram_size (int):
            The size of the ngrams to use.
        ngram_stride (int):
            The stride of the ngrams to use.
        num_minhashes (int):
            The number of minhashes to use.
        random_seed (int):
            The random seed to use.

    Returns:
        LeanMinHash: The minhash fingerprint for the given document.

    Raises:
        ValueError:
            If `split_method` is not 'word_ngram', 'paragraph', 'none'
            or None.
    """
    # Extract shingles from the document, depending on the `split_method`
    shingles = get_shingles(
        doc,
        normalization_func=normalization_func,
        split_method=split_method,
        ngram_size=ngram_size,
        ngram_stride=ngram_stride,
    )

    # Initialise the fingerprint
    minhash = MinHash(num_perm=num_minhashes, seed=random_seed)

    # Add all the shingles to the fingerprint
    minhash.update_batch([shingle.encode("utf-8") for shingle in shingles])

    # Convert the fingerprint to a LeanMinHash fingerprint, to save memory
    # and increase performance
    minhash = LeanMinHash(minhash, seed=random_seed)

    # Return the fingerprint
    return minhash


def default_normalization(doc: str) -> str:
    """NFKC normalise document and remove punctuation

    Args:
        doc (str): The document to normalize.

    Returns:
        str: The normalized document.
    """
    doc = normalize("NFKC", doc)
    doc = re.sub(r"[\.\,\:\;\!\?\(\)\[\]\{\}]", " ", doc)
    return re.sub(" +", " ", doc)
