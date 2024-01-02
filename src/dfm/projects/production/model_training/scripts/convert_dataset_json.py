# Copyright 2022 MosaicML LLM Foundry authors
# Modified by the Danish Foundation Models authors
# SPDX-License-Identifier: Apache-2.0

"""Streaming dataset conversion scripts for json files."""
import os
from argparse import ArgumentParser, Namespace
from enum import Enum
from glob import glob
from typing import Dict, Iterable, Optional, Union

import datasets as hf_datasets
from streaming import MDSWriter
from torch.utils.data import DataLoader, IterableDataset
from tqdm import tqdm
from transformers import AutoTokenizer, PreTrainedTokenizerBase
import multiprocessing
import numpy as np

class ConcatTokensDataset(IterableDataset):
    """An IterableDataset that returns token samples for MDSWriter.

    Returns dicts of {'tokens': bytes}

    To use data created by this class and written to MDS format:

    ```python
        import torch
        from streaming.base import StreamingDataset
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained('your/tokenizer')
        ds = StreamingDataset(local='mds-data-folder', split='val')

        # note, you need to copy the numpy array because the original is non-writeable
        # and torch does not support non-writeable tensors, so you get a scary warning and
        # if you do try to write to the tensor you get undefined behavior
        tokens = torch.from_numpy(np.frombuffer(ds[0]['tokens'], dtype=np.int64).copy())
        print(tokenizer.decode(tokens))
    ```
    """

    def __init__(
        self,
        hf_dataset: Union[hf_datasets.IterableDataset, hf_datasets.Dataset],
        tokenizer: PreTrainedTokenizerBase,
        max_length: int,
        bos_text: str,
        eos_text: str,
        no_wrap: bool,
    ):
        self.tokenizer = tokenizer
        assert self.tokenizer.is_fast, 'This tokenizer is not fast. Please use a fast tokenizer.'
        os.environ['TOKENIZERS_PARALLELISM'] = 'true'
        self.max_length = max_length
        self.bos_text = bos_text
        self.eos_text = eos_text
        self.should_wrap = not no_wrap

        self.bos_tokens = self.tokenizer(self.bos_text,
                                         truncation=False,
                                         padding=False,
                                         add_special_tokens=False)['input_ids']
        if len(self.bos_tokens) > 1:
            warnings.warn(
                f'You specified --concat_tokens with --bos_text, but your BOS text is not tokenizing to one token\
                , instead we got {self.bos_tokens}. Quit if this was in error.')

        self.eos_tokens = self.tokenizer(self.eos_text,
                                         truncation=False,
                                         padding=False,
                                         add_special_tokens=False)['input_ids']
        if len(self.eos_tokens) > 1:
            warnings.warn(
                f'You specified --concat_tokens with --eos_text, but your EOS text is not tokenizing to one token\
                , instead we got {self.eos_tokens}. Quit if this was in error.')

        eos_text_provided = self.eos_text != ''
        bos_text_provided = self.bos_text != ''
        test_text = self.tokenizer('')
        if len(test_text['input_ids']) > 0 and (eos_text_provided or
                                                bos_text_provided):
            message = 'both eos and bos' if eos_text_provided and bos_text_provided else (
                'eos_text' if eos_text_provided else 'bos_text')
            warnings.warn(
                f'The provided tokenizer adds special tokens, but you also specified {message}. This may result '
                +
                'in duplicated special tokens. Please be sure this is what you intend.'
            )

        def tokenize(batch):
            return tokenizer(batch['text'],
                            truncation=False,
                            padding=False,
                            add_special_tokens=False)

        print("Tokenizing dataset")
        self.dataset = hf_dataset.map(tokenize, batched=True,
                                      batch_size=24*10,
                                      remove_columns=['text'])

    def __iter__(self) -> Iterable[Dict[str, bytes]]:
        buffer = np.empty(0, dtype=np.int64, order='C')
        for sample in self.dataset:
            iids = sample['input_ids'] # List[int]
            # buffer = buffer + self.bos_tokens + iids + self.eos_tokens
            buffer = np.append(buffer, [*self.bos_tokens, *iids, *self.eos_tokens])
            while len(buffer) >= self.max_length:
                concat_sample = buffer[:self.max_length]
                buffer = buffer[self.max_length:] if self.should_wrap else np.empty(0, dtype=np.int64, order='C')
                yield {
                    # convert to bytes to store in MDS binary format
                    'tokens': concat_sample.tobytes()
                }


class ConcatMode(Enum):
    NO_CONCAT = 'NO_CONCAT'
    CONCAT_TOKENS = 'CONCAT_TOKENS'


def parse_args() -> Namespace:
    """Parse commandline arguments."""
    parser = ArgumentParser(
        description=
        'Convert dataset into MDS format, optionally concatenating and tokenizing'
    )
    parser.add_argument('--path', type=str, required=True)
    parser.add_argument('--out_root', type=str, required=True)
    parser.add_argument('--compression', type=str, default=None)

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        '--concat_tokens',
        type=int,
        help='Convert text to tokens and concatenate up to this many tokens')
    parser.add_argument('--split', type=str, default='train')

    parser.add_argument('--tokenizer', type=str, required=False, default=None)
    parser.add_argument('--bos_text', type=str, required=False, default=None)
    parser.add_argument('--eos_text', type=str, required=False, default=None)
    parser.add_argument('--no_wrap', default=False, action='store_true')

    parsed = parser.parse_args()

    if os.path.isdir(parsed.out_root) and len(
            set(os.listdir(parsed.out_root)).intersection(set(
                parsed.split))) > 0:
        raise ValueError(
            f'--out_root={parsed.out_root} contains {os.listdir(parsed.out_root)} which cannot overlap with the requested splits {parsed.splits}.'
        )

    # Make sure we have needed concat options
    if (parsed.concat_tokens is not None and
            isinstance(parsed.concat_tokens, int) and parsed.tokenizer is None):
        parser.error(
            'When setting --concat_tokens, you must specify a --tokenizer')

    # now that we have validated them, change BOS/EOS to strings
    if parsed.bos_text is None:
        parsed.bos_text = ''
    if parsed.eos_text is None:
        parsed.eos_text = ''
    return parsed


def build_hf_dataset(
    path: str,
    split: str,
    mode: ConcatMode,
    max_length: Optional[int] = None,
    bos_text: str = '',
    eos_text: str = '',
    no_wrap: bool = False,
    tokenizer: PreTrainedTokenizerBase = None,
) -> IterableDataset:
    """Build an IterableDataset over the HF C4 or pile source data.

    Args:
        dataset_name (str): Dataset name
        split (str): Split name.
        mode (ConcatMode): NO_CONCAT, or CONCAT_TOKENS
        max_length (int): The length of concatenated tokens
        bos_text (str): text to insert at the beginning of each sequence
        eos_text (str): text to insert at the end of each sequence
        no_wrap (bool): if concatenating, whether to wrap text across `max_length` boundaries
        tokenizer (PreTrainedTokenizerBase): if mode is CONCAT_TOKENS, the tokenizer to use
        data_subset (str): Referred to as "name" in HuggingFace datasets.load_dataset.
            Typically "all" (The Pile) or "en" (c4).

    Returns:
        An IterableDataset.
    """
    if os.path.isdir(path):
        data_files = glob(f'{path}/*')
    else:
        data_files = path

    hf_dataset = hf_datasets.load_dataset('json',
                                          keep_in_memory=False,
                                          data_files=data_files,
                                          split=split)

    if mode == ConcatMode.NO_CONCAT:
        dataset = NoConcatDataset(hf_dataset)
    else:
        if not isinstance(tokenizer, PreTrainedTokenizerBase):
            raise ValueError(
                f'{tokenizer=} must be of type PreTrainedTokenizerBase')
        if max_length is None:
            raise ValueError(f'max_length must be set.')
        if bos_text + eos_text == '':
            test_tokens = tokenizer('test')
            if test_tokens['input_ids'][
                    0] != tokenizer.bos_token_id and test_tokens['input_ids'][
                        -1] != tokenizer.eos_token_id:
                tok_error_msg = 'This tokenizer does not insert an EOS nor BOS token. '
                tok_error_msg += 'Concatenating with this tokenizer will result in sequences being '
                tok_error_msg += 'attached without a separating token. Please use another tokenizer, '
                tok_error_msg += 'such as facebook/opt-125m, or specify EOS/BOS text with e.g. '
                tok_error_msg += '--bos_text=<|endoftext|>.'
                raise ValueError(tok_error_msg)
        dataset = ConcatTokensDataset(hf_dataset=hf_dataset,
                                      tokenizer=tokenizer,
                                      max_length=max_length,
                                      bos_text=bos_text,
                                      eos_text=eos_text,
                                      no_wrap=no_wrap)
    return dataset


def generate_samples(
        loader: DataLoader,
        truncate_num_samples: Optional[int] = None
) -> Iterable[Dict[str, bytes]]:
    """Generator over samples of a dataloader.

    Args:
       loader (DataLoader): A dataloader emitting batches like {key: [sample0_bytes, sample1_bytes, sample2_bytes, ...]}
       truncate_num_samples (Optional[int]): An optional # of samples to stop at.

    Yields:
        Sample dicts.
    """
    n_samples = 0
    for batch in loader:
        keys = list(batch.keys())
        current_bs = len(batch[keys[0]])
        for idx in range(current_bs):
            if truncate_num_samples is not None and n_samples == truncate_num_samples:
                return
            n_samples += 1
            yield {k: v[idx] for k, v in batch.items()}


def main(args: Namespace) -> None:
    """Main: create C4/pile streaming dataset.

    Args:
        args (Namespace): Commandline arguments.
    """
    if args.concat_tokens is not None:
        mode = ConcatMode.CONCAT_TOKENS
        tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)
        # we will enforce length, so suppress warnings about sequences too long for the model
        tokenizer.model_max_length = int(1e30)
        columns = {'tokens': 'bytes'}
    else:
        mode = ConcatMode.NO_CONCAT
        tokenizer = None
        columns = {'text': 'str'}

    # Get samples
    dataset = build_hf_dataset(path=args.path,
                               split=args.split,
                               mode=mode,
                               max_length=args.concat_tokens,
                               bos_text=args.bos_text,
                               eos_text=args.eos_text,
                               no_wrap=args.no_wrap,
                               tokenizer=tokenizer)

    # Write samples with parallel processing
    print(f'Converting to MDS format...')
    with MDSWriter(columns=columns,
                   out=os.path.join(args.out_root),
                   compression=args.compression) as out:
        for sample in tqdm(dataset):
            out.write(sample)


if __name__ == '__main__':
    main(parse_args())
