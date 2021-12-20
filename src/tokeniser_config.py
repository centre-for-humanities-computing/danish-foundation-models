'''Class to hold the configuration for the tokeniser'''

from pathlib import Path
import json
from typing import Union


class TokeniserConfig:
    '''Class to hold tokeniser configuration.

    Args:
        tokeniser_type (str):
            Type of tokeniser to use. Can be either 'bpe', 'wordpiece' or
            'unigram'.
        vocab_size (int):
            Size of vocabulary to use.
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
            `padding` or `truncation` is True. Defaults to 512.
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
    def __init__(self,
                 tokeniser_type: str,
                 vocab_size: int,
                 lower_case: bool,
                 sentence_piece: bool,
                 add_prefix_space: bool,
                 byte_level: bool,
                 add_sep_and_cls_tokens: bool = True,
                 padding: bool = True,
                 truncation: bool = True,
                 max_length: int = 512,
                 nfkc_normalisation: bool = True,
                 pad_token: str = '<pad>',
                 bos_token: str = '<s>',
                 eos_token: str = '</s>',
                 unk_token: str = '<unk>',
                 mask_token: str = '<mask>'):
        # Set the configuration
        self.tokeniser_type = tokeniser_type
        self.vocab_size = vocab_size
        self.lower_case = lower_case
        self.sentence_piece = sentence_piece
        self.add_prefix_space = add_prefix_space
        self.byte_level = byte_level
        self.add_sep_and_cls_tokens = add_sep_and_cls_tokens
        self.padding = padding
        self.truncation = truncation
        self.max_length = max_length
        self.nfkc_normalisation = nfkc_normalisation
        self.pad_token = pad_token
        self.bos_token = bos_token
        self.eos_token = eos_token
        self.unk_token = unk_token
        self.mask_token = mask_token

        # Lower case `tokeniser_type` if possible
        try:
            self.tokeniser_type = self.tokeniser_type.lower()
        except AttributeError:
            pass

        # Check whether the configuration is valid
        self.check_config()

    def check_config(self):
        '''Check that the configuration is valid.

        This both checks that the data types of the inputs are correct, as well
        as the values.

        Raises:
            ValueError:
                If the configuration is invalid.
        '''
        # Check that the tokeniser type is valid
        if (not isinstance(self.tokeniser_type, str) or
                self.tokeniser_type not in ['bpe', 'wordpiece', 'unigram']):
            raise ValueError(f'Invalid tokeniser type: {self.tokeniser_type}')

        # Check that the vocab size is valid
        if not isinstance(self.vocab_size, int) or self.vocab_size < 1:
            raise ValueError(f'Invalid vocab size: {self.vocab_size}')

        # Check that the lower case is valid
        if not isinstance(self.lower_case, bool):
            raise ValueError(f'Invalid lower case: {self.lower_case}')

        # Check that the sentence piece is valid
        if not isinstance(self.sentence_piece, bool):
            raise ValueError(f'Invalid sentence piece: {self.sentence_piece}')

        # Check that the add prefix space is valid
        if not isinstance(self.add_prefix_space, bool):
            raise ValueError(f'Invalid add prefix space: '
                             f'{self.add_prefix_space}')

        # Check that the byte level is valid
        if not isinstance(self.byte_level, bool):
            raise ValueError(f'Invalid byte level: {self.byte_level}')

        # Check that the add sep and cls tokens is valid
        if not isinstance(self.add_sep_and_cls_tokens, bool):
            raise ValueError(f'Invalid add sep and cls tokens: '
                             f'{self.add_sep_and_cls_tokens}')

        # Check that the padding is valid
        if not isinstance(self.padding, bool):
            raise ValueError(f'Invalid padding: {self.padding}')

        # Check that the truncation is valid
        if not isinstance(self.truncation, bool):
            raise ValueError(f'Invalid truncation: {self.truncation}')

        # Check that the max length is valid
        if not isinstance(self.max_length, int) or self.max_length < 1:
            raise ValueError(f'Invalid max length: {self.max_length}')

        # Check that the nfkc normalisation is valid
        if not isinstance(self.nfkc_normalisation, bool):
            raise ValueError(f'Invalid NFKC normalisation: '
                             f'{self.nfkc_normalisation}')

        # Check that the pad token is valid
        if not isinstance(self.pad_token, str):
            raise ValueError(f'Invalid pad token: {self.pad_token}')

        # Check that the bos token is valid
        if not isinstance(self.bos_token, str):
            raise ValueError(f'Invalid bos token: {self.bos_token}')

        # Check that the eos token is valid
        if not isinstance(self.eos_token, str):
            raise ValueError(f'Invalid eos token: {self.eos_token}')

        # Check that the unk token is valid
        if not isinstance(self.unk_token, str):
            raise ValueError(f'Invalid unk token: {self.unk_token}')

        # Check that the mask token is valid
        if not isinstance(self.mask_token, str):
            raise ValueError(f'Invalid mask token: {self.mask_token}')

    def __repr__(self) -> str:
        '''Return a string representation of the configuration.

        Returns:
            str:
                String representation of the configuration.
        '''
        return (f'{self.__class__.__name__}('
                f'tokeniser_type={self.tokeniser_type}, '
                f'vocab_size={self.vocab_size}, '
                f'lower_case={self.lower_case}, '
                f'sentence_piece={self.sentence_piece}, '
                f'add_prefix_space={self.add_prefix_space}, '
                f'byte_level={self.byte_level}, '
                f'add_sep_and_cls_tokens={self.add_sep_and_cls_tokens}, '
                f'padding={self.padding}, '
                f'truncation={self.truncation}, '
                f'max_length={self.max_length}, '
                f'nfkc_normalisation={self.nfkc_normalisation}, '
                f'pad_token={self.pad_token}, '
                f'bos_token={self.bos_token}, '
                f'eos_token={self.eos_token}, '
                f'unk_token={self.unk_token}, '
                f'mask_token={self.mask_token})')

    def __iter__(self):
        '''Return an iterator over the configuration.

        Returns:
            iterator:
                Iterator over the configuration, yielding (key, value) tuples.
        '''
        def iterable_fn():
            for key, val in self.__dict__().items():
                yield key, val
        return iterable_fn()

    def __dict__(self):
        '''Get dictionary representation of tokeniser configuration.

        Return:
            dict: Dictionary representation of tokeniser configuration.
        '''
        return dict(tokeniser_type=self.tokeniser_type,
                    vocab_size=self.vocab_size,
                    lower_case=self.lower_case,
                    sentence_piece=self.sentence_piece,
                    add_prefix_space=self.add_prefix_space,
                    byte_level=self.byte_level,
                    add_sep_and_cls_tokens=self.add_sep_and_cls_tokens,
                    padding=self.padding,
                    truncation=self.truncation,
                    max_length=self.max_length,
                    nfkc_normalisation=self.nfkc_normalisation,
                    pad_token=self.pad_token,
                    bos_token=self.bos_token,
                    eos_token=self.eos_token,
                    unk_token=self.unk_token,
                    mask_token=self.mask_token)

    def save(self, filename: Union[str, Path]):
        '''Save tokeniser configuration to file.

        Args:
            filename (str or Path):
                File to save tokeniser configuration to.
        '''
        with Path(filename).open('w') as f:
            json.dump(dict(self), f, indent=4)
