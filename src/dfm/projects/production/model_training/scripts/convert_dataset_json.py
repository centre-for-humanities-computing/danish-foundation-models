# Copyright 2022 MosaicML LLM Foundry authors
# Modified by @rlrs for Danish Foundation Models
# SPDX-License-Identifier: Apache-2.0

"""Streaming dataset conversion scripts for json files."""
import os
from argparse import ArgumentParser, Namespace
from glob import glob
from typing import Dict, Iterable, Optional, Union

import datasets as hf_datasets
from streaming import MDSWriter
from torch.utils.data import IterableDataset
from tqdm import tqdm
from transformers import AutoTokenizer, PreTrainedTokenizerBase
import numpy as np


def generate_chunks(dataset: Union[hf_datasets.IterableDataset, hf_datasets.Dataset], 
                    bos_tokens: list[int], eos_tokens: list[int], chunk_length: int) -> Iterable[Dict[str, bytes]]:
    buffer = np.empty(0, dtype=np.int64, order='C')
    for sample in dataset:
        iids = sample['input_ids']
        buffer = np.append(buffer, [*bos_tokens, *iids, *eos_tokens])
        while len(buffer) >= chunk_length:
            concat_sample = buffer[:chunk_length]
            buffer = buffer[chunk_length:] #if should_wrap else np.empty(0, dtype=np.int64, order='C')
            yield {
                # convert to bytes to store in MDS binary format
                'tokens': concat_sample.tobytes()
            }


def parse_args() -> Namespace:
    """Parse commandline arguments."""
    parser = ArgumentParser(
        description=
        'Convert dataset into MDS format, tokenizing and concatenating.'
    )
    parser.add_argument('--path', type=str, required=True)
    parser.add_argument('--out_root', type=str, required=True)
    parser.add_argument('--compression', type=str, default='zstd')

    parser.add_argument(
        '--concat_tokens',
        type=int,
        help='Convert text to tokens and concatenate up to this many tokens', required=True)

    parser.add_argument('--tokenizer', type=str, required=False, default=None)
    parser.add_argument('--bos_text', type=str, required=False, default=None)
    parser.add_argument('--eos_text', type=str, required=False, default=None)
    parser.add_argument('--no_wrap', default=False, action='store_true') # why would you do this?

    parser.add_argument('--test_size', type=float, default=0.01)
    parser.add_argument('--seed', type=int, default=42)

    parsed = parser.parse_args()

    if parsed.bos_text is None:
        parsed.bos_text = ''
    if parsed.eos_text is None:
        parsed.eos_text = ''
    return parsed


def build_hf_dataset(
    path: str,
    tokenizer: PreTrainedTokenizerBase,
    max_length: Optional[int] = None,
    bos_text: str = '',
    eos_text: str = '',
) -> IterableDataset:
    """Build an IterableDataset over the HF C4 or pile source data.

    Args:
        dataset_name (str): Dataset name
        max_length (int): The length of concatenated tokens
        bos_text (str): text to insert at the beginning of each sequence
        eos_text (str): text to insert at the end of each sequence
        no_wrap (bool): if concatenating, whether to wrap text across `max_length` boundaries
        tokenizer (PreTrainedTokenizerBase): the tokenizer to use

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
                                          split="train")

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

    return hf_dataset

def main(args: Namespace) -> None:
    """Main: create C4/pile streaming dataset.

    Args:
        args (Namespace): Commandline arguments.
    """

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)
    # we will enforce length, so suppress warnings about sequences too long for the model
    tokenizer.model_max_length = int(1e30)
    columns = {'tokens': 'bytes'}

    # Get samples
    dataset = build_hf_dataset(path=args.path,
                               max_length=args.concat_tokens,
                               bos_text=args.bos_text,
                               eos_text=args.eos_text,
                               tokenizer=tokenizer)
    
    bos_tokens = tokenizer(args.bos_text,
                           truncation=False,
                           padding=False,
                           add_special_tokens=False)['input_ids']
    if len(bos_tokens) > 1:
        warnings.warn(
            f'You specified --concat_tokens with --bos_text, but your BOS text is not tokenizing to one token\
            , instead we got {bos_tokens}. Quit if this was in error.')

    eos_tokens = tokenizer(args.eos_text,
                           truncation=False,
                           padding=False,
                           add_special_tokens=False)['input_ids']
    if len(eos_tokens) > 1:
        warnings.warn(
            f'You specified --concat_tokens with --eos_text, but your EOS text is not tokenizing to one token\
            , instead we got {self.eos_tokens}. Quit if this was in error.')

    eos_text_provided = args.eos_text != ''
    bos_text_provided = args.bos_text != ''
    test_text = tokenizer('')
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
    
    # We make a train/test split before chunking since it's way easier, although number
    # of samples will vary - splitting after chunking would fix this, but has other issues
    dataset = dataset.train_test_split(test_size=args.test_size, seed=args.seed)

    print("Tokenizing dataset")
    dataset = dataset.map(tokenize, batched=True,
                          batch_size=24*10,
                          remove_columns=['text'])

    # Write samples while chunking
    for split in dataset.keys():
        print(f'Writing {split} split... (iterations are samples)')
        with MDSWriter(columns=columns,
                       out=os.path.join(args.out_root, split),
                       compression=args.compression) as out:
            for sample in tqdm(generate_chunks(dataset[split], bos_tokens, eos_tokens, args.concat_tokens)):
                out.write(sample)

if __name__ == '__main__':
    main(parse_args())
