'''Script to train tokenizers from a Hugging Face dataset'''

from tokenizers import (trainers, pre_tokenizers, tokenizers, normalizers,
                        models, AddedToken, processors, decoders)
from datasets import Dataset
from pathlib import Path
from typing import Union
from tokeniser_config import TokeniserConfig


def train_tokeniser(config: Union[TokeniserConfig, dict],
                    dataset: Dataset,
                    output_path: Union[str, Path] = 'tokeniser.json'):
    '''Train a tokeniser on a dataset.

    Args:
        config (TokeniserConfig or dict):
            Configuration for the tokeniser.
        dataset (Dataset):
            Dataset to train the tokeniser on. Must have a feature named
            'text'.
        output_dir (str or Path, optional):
            Path to save the tokeniser to. Defaults to './tokeniser.json'.
    '''
    # Convert config to `TokeniserConfig` instance if a dict is given
    if isinstance(config, dict):
        config = TokeniserConfig(**config)

    # Instantiate the tokeniser model
    if config.tokeniser_type == 'bpe':
        model = models.BPE(unk_token=config.unk_token,
                           continuing_subword_prefix='##')
    elif config.tokeniser_type == 'wordpiece':
        model = models.WordPiece(unk_token=config.unk_token)  # noqa
    elif config.tokeniser_type == 'unigram':
        model = models.Unigram()  # noqa

    # Instantiate the tokeniser
    tokeniser = tokenizers.Tokenizer(model)

    # Initialise the special tokens and add them to the tokeniser
    special_tokens = [
        AddedToken(config.pad_token, single_word=True, normalized=False),
        AddedToken(config.bos_token, single_word=True, normalized=False),
        AddedToken(config.eos_token, single_word=True, normalized=False),
        AddedToken(config.unk_token, single_word=True, normalized=False),
        AddedToken(config.mask_token, single_word=True, normalized=False)
    ]
    tokeniser.add_special_tokens(special_tokens)

    # Initialise the normaliser and add it to the tokeniser
    normaliser_list = list()
    if config.nfkc_normalisation:
        normaliser_list.append(normalizers.NFKC())
    if config.lower_case:
        normaliser_list.append(normalizers.Lowercase())
    normaliser = normalizers.Sequence(normaliser_list)  # noqa
    tokeniser.normalizer = normaliser

    # Shorthand for whether a prefix whitespace should be added to words
    pre_ws = config.add_prefix_space

    # Initialise the pre-tokeniser and add it to the tokeniser
    pre_tok_list = list()
    if config.byte_level:
        pre_tok_list.append(pre_tokenizers.ByteLevel(add_prefix_space=pre_ws))
    if config.sentence_piece:
        pre_tok_list.append(pre_tokenizers.Metaspace(add_prefix_space=pre_ws))
    if not config.byte_level and not config.sentence_piece:
        pre_tok_list.append(pre_tokenizers.Whitespace())
    pre_tokeniser = pre_tokenizers.Sequence(pre_tok_list)
    tokeniser.pre_tokenizer = pre_tokeniser

    # Initialise the post-processor
    proc_list = list()
    if config.byte_level:
        proc_list.append(processors.ByteLevel(trim_offsets=True))
    if config.add_sep_and_cls_tokens:
        params = dict(cls=(config.bos_token, 1), sep=(config.eos_token, 2))
        proc_list.append(processors.BertProcessing(**params))
    tokeniser.post_processor = processors.Sequence(proc_list)  # noqa

    # Initialise the decoder
    dec_list = list()
    if config.tokeniser_type == 'bpe':
        dec_list.append(decoders.BPEDecoder(suffix='</w>'))
    elif config.tokeniser_type == 'wordpiece':
        dec_list.append(decoders.WordPiece(prefix='##', cleanup=True))
    if config.sentence_piece:
        dec_list.append(decoders.Metaspace(add_prefix_space=pre_ws))
    if config.byte_level:
        dec_list.append(decoders.ByteLevel())
    tokeniser.decoder = decoders.Sequence(dec_list)  # noqa

    # Enable truncation and padding
    tokeniser.enable_truncation(max_length=config.max_length)
    tokeniser.enable_padding(pad_id=0,
                             pad_type_id=0,
                             pad_token=config.pad_token)

    # Initialise the trainer
    if config.tokeniser_type == 'bpe':
        trainer = trainers.BpeTrainer(vocab_size=config.vocab_size,
                                      special_tokens=special_tokens)
    elif config.tokeniser_type == 'wordpiece':
        trainer = trainers.WordPieceTrainer(vocab_size=config.vocab_size,
                                            special_tokens=special_tokens)
    elif config.tokeniser_type == 'unigram':
        trainer = trainers.UnigramTrainer(vocab_size=config.vocab_size,
                                          special_tokens=special_tokens,
                                          unk_token='<unk>')

    # Train the tokeniser
    tokeniser.train_from_iterator(iterator=dataset['text'],
                                  trainer=trainer)

    # Save the tokeniser
    tokeniser.save(str(output_path))

    return tokeniser
