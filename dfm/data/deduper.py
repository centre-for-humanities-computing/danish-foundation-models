'''Class that deduplicates an iterable corpus.

The deduplication is based on the MinHash algorithm [1].

Author:
    Dan Saattrup Nielsen (saattrupdan@gmail.com)

References:
    [1] Broder, Andrei Z. "On the resemblance and containment of documents."
        Proceedings. Compression and Complexity of SEQUENCES 1997
        (Cat. No. 97TB100171). IEEE, 1997.
'''

from datasketch import MinHash, LeanMinHash, MinHashLSH
from datasets.arrow_dataset import Dataset
from datasets.iterable_dataset import IterableDataset
from typing import Union, Iterable, Optional
from pathlib import Path
import json
from unicodedata import normalize
import re
from tqdm.auto import tqdm


class Deduper:
    '''Class that deduplicates an iterable corpus.

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

    Attributes:
        split_method (str): The splitting method for extracting shingles.
        ngram_size (str): The size of the ngram shingles.
        ngram_stride (str): The stride used for the ngram shingles.
        similarity_threshold (float): The Jaccard similarity threshold.
        num_minhashes (int): The number of MinHash functions to use.
        random_seed (int): The random seed to use for the MinHash functions.
        cache (MinHashLSH object): The LSH cache for storing the fingerprints.

    References:
        [1] Broder, Andrei Z. "On the resemblance and containment of documents."
            Proceedings. Compression and Complexity of SEQUENCES 1997
            (Cat. No. 97TB100171). IEEE, 1997.
    '''
    def __init__(self,
                 split_method: Optional[str] = 'char_ngram',
                 ngram_size: int = 13,
                 ngram_stride: int = 1,
                 similarity_threshold: float = 0.8,
                 num_minhashes: int = 128,
                 random_seed: int = 42):
        self.split_method = 'none' if split_method is None else split_method
        self.ngram_size = ngram_size
        self.ngram_stride = ngram_stride
        self.similarity_threshold = similarity_threshold
        self.num_minhashes = num_minhashes
        self.random_seed = random_seed

    def _get_minhash(self, doc: str) -> LeanMinHash:
        '''Returns a minhash fingerprint for the given document.

        Args:
            doc (str): The document to create the MinHash object for.

        Returns:
            LeanMinHash: The minhash fingerprint for the given document.

        Raises:
            ValueError:
                If `self.split_method` is not 'char_ngram', 'word_ngram',
                'paragraph' or 'none'.
        '''
        # NFKC normalise document and remove punctuation
        doc = normalize('NFKC', doc)
        doc = re.sub(r'[\.\,\:\;\!\?\(\)\[\]\{\}]', ' ', doc)
        doc = re.sub(' +', ' ', doc)

        # Initialise the fingerprint
        minhash = MinHash(num_perm=self.num_minhashes, seed=self.random_seed)

        # Extract shingles from the document, depending on the `split_method`
        if self.split_method == 'char_ngram':
            max_char_idx = len(doc) - self.ngram_size
            shingles = [doc[i : i + self.ngram_size]
                        for i in range(0, max_char_idx, self.ngram_stride)]
        elif self.split_method == 'word_ngram':
            words = doc.split(' ')
            max_word_idx = len(words) - self.ngram_size
            shingles = [' '.join(words[i : i + self.ngram_size]).strip()
                        for i in range(0, max_word_idx, self.ngram_stride)]
        elif self.split_method == 'paragraph':
            shingles = [p for p in doc.split('\n') if len(p) > 0]
        elif self.split_method == 'none':
            shingles = [doc]
        else:
            raise ValueError(f'Invalid split method: {self.split_method}')

        # Add all the shingles to the fingerprint
        for shingle in shingles:
            minhash.update(shingle.encode('utf-8'))

        # Convert the fingerprint to a LeanMinHash fingerprint, to save memory
        # and increase performance
        minhash = LeanMinHash(minhash, seed=self.random_seed)

        # Return the fingerprint
        return minhash

    def _store_document(self,
                        doc_idx: Union[str, int],
                        doc: str,
                        fname: Union[str, Path]):
        '''Appends the document to a JSONL file.

        Args:
            doc_idx (str or int): The document index.
            doc (str): The document to append to the JSONL file.
            fname (str or Path): The name of the JSONL file to append to.
        '''
        # Ensure that `doc_id` is a string
        doc_id = str(doc_idx)

        # Ensure that `fname` is a Path object
        fname = Path(fname)

        # Append the document to the JSONL file
        with fname.open('a') as f:
            jsonned = json.dumps(dict(id=doc_id, text=doc))
            f.write(jsonned + '\n')

    def deduplicate(self,
                    corpus: Union[Dataset, IterableDataset, Iterable[str]],
                    output_fname: Union[str, Path] = 'deduplicated.jsonl'):
        '''Removes duplicate documents from the corpus and stores it to disk.

        Args:
            corpus (Dataset, IterableDataset or iterable of strings):
                The corpus to deduplicate.
            output_fname (str or Path, optional):
                The name of the output file.

        Raises:
            FileExistsError: If the output file already exists.
        '''
        # Convert corpus to an iterable of strings if a Dataset is given
        if isinstance(corpus, Dataset) or isinstance(corpus, IterableDataset):
            corpus = (sample["text"] for sample in corpus)

        # Ensure that `output_fname` is a Path object
        output_fname = Path(output_fname)

        # If the output file already exists then raise an error
        if output_fname.exists():
            raise FileExistsError(f'Output file {output_fname} '
                                  f'already exists.')

        # Initialise the LSH cache
        cache = MinHashLSH(threshold=self.similarity_threshold,
                           num_perm=self.num_minhashes)

        # Iterate over the corpus and store documents that are not duplicates
        duplicates = 0
        with tqdm(corpus, desc='Deduplicating') as pbar:
            for doc_idx, doc in enumerate(pbar):

                # Compute the fingerprint for the document
                minhash = self._get_minhash(doc)

                # If the document is not a near-duplicate then store in the LSH
                # cache and append it to the JSONL output file
                if len(cache.query(minhash)) == 0:
                    cache.insert(doc_idx, minhash)
                    self._store_document(doc_idx=doc_idx,
                                         doc=doc,
                                         fname=output_fname)

                # Otherwise, increment the number of duplicate documents
                else:
                    duplicates += 1

                # Update the progress bar description with the number of
                # duplicates found so far
                pct_duplicated = 100 * duplicates / (1 + doc_idx)
                desc = (f'Deduplicating - {pct_duplicated:.2f}% '
                        f'duplicates or near-duplicates found')
                pbar.set_description(desc)


if __name__ == '__main__':
    from datasets import load_dataset

    corpus = load_dataset('DDSC/partial-danish-gigaword-no-twitter',
                          streaming=True,
                          split='train')
    deduper = Deduper(split_method='char_ngram', ngram_size=13)
    deduper.deduplicate(corpus, output_fname='deduplicated.jsonl')
