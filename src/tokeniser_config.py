'''Class to hold the configuration for the tokeniser'''

from pathlib import Path
import json
from typing import Union
from pydantic import BaseModel, PositiveInt, StrictStr
from enum import Enum


class TokeniserType(str, Enum):
    '''Class that holds the different tokeniser types'''
    bpe = 'bpe'
    wordpiece = 'wordpiece'
    unigram = 'unigram'


class TokeniserConfig(BaseModel):
    '''Class to hold tokeniser configuration.

    Args:
        tokeniser_type (str):
            Type of tokeniser to use. Can be either 'bpe', 'wordpiece' or
            'unigram'.
        vocab_size (int):
            Size of vocabulary to use. Must be greater than 0.
        lower_case (bool):
            Whether to lower case the text.
        sentence_piece (bool):
            Whether to enable Sentence Piece, meaning that the document will
            not be pre-tokenised into words, and instead everything will be
            handled directly by the tokeniser. In particular, this means that
            whitespace will also be tokenised.
        add_prefix_space (bool):
            Whether to add a space to the start of the text. This is, e.g.,
            requred by the RoBERTa tokeniser.
        byte_level (bool):
            Whether to use byte level tokenisation. This means that the
            documents will be UTF-8 encoded and then tokenised.
        add_sep_and_cls_tokens (bool, optional):
            Whether to add the special tokens to the beginning and end of the
            document, as is used by many BERT models. Defaults to True.
        padding (bool, optional):
            Whether to pad the documents to a fixed length. Defaults to True.
        truncation (bool, optional):
            Whether to truncate the documents to a fixed length. Defaults to
            True.
        max_length (int, optional):
            Maximum number of tokens in a document. Only relevant if either
            `padding` or `truncation` is True. Defaults to 512. Must be greater
            than 0.
        nfkc_normalisation (bool, optional):
            Whether to normalise the text using NFKC. Defaults to True.
        pad_token (str, optional):
            Token to use for padding. Defaults to '<pad>'.
        bos_token (str, optional):
            Token to use for beginning of sentence. Defaults to '<s>'.
        eos_token (str, optional):
            Token to use for end of sentence. Defaults to '</s>'.
        unk_token (str, optional):
            Token to use for unknown tokens. Defaults to '<unk>'.
        mask_token (str, optional):
            Token to use for masking. Defaults to '<mask>'.
    '''
    tokeniser_type: TokeniserType
    vocab_size: PositiveInt
    lower_case: bool
    sentence_piece: bool
    add_prefix_space: bool
    byte_level: bool
    add_sep_and_cls_tokens: bool = True
    padding: bool = True
    truncation: bool = True
    max_length: PositiveInt = 512
    nfkc_normalisation: bool = True
    pad_token: StrictStr = '<pad>'
    bos_token: StrictStr = '<s>'
    eos_token: StrictStr = '</s>'
    unk_token: StrictStr = '<unk>'
    mask_token: StrictStr = '<mask>'

    def save(self, filename: Union[str, Path]):
        '''Save tokeniser configuration to file.

        Args:
            filename (str or Path):
                File to save tokeniser configuration to.
        '''
        with Path(filename).open('w') as f:
            json.dump(dict(self), f, indent=4)

    @classmethod
    def load(cls, filename: Union[str, Path]):
        '''Load tokeniser configuration from file.

        Args:
            filename (str or Path):
                File to load tokeniser configuration from.

        Returns:
            TokeniserConfig:
                Tokeniser configuration.
        '''
        with Path(filename).open('r') as f:
            config = json.load(f)
        return cls(**config)
