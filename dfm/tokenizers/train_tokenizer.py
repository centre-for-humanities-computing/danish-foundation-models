"""Script to train tokenizers"""

from tokenizers import (
    trainers,
    pre_tokenizers,
    tokenizers,
    normalizers,
    models,
    AddedToken,
    processors,
    decoders,
)
from datasets.arrow_dataset import Dataset
from datasets.iterable_dataset import IterableDataset
from pathlib import Path
from typing import Union, Iterable
from .tokenizer_config import TokenizerConfig


def train_tokenizer(
    corpus: Union[Dataset, IterableDataset, Iterable[str]],
    config: Union[TokenizerConfig, dict],
    save_tokenizer: bool = True,
    output_dir: Union[str, Path] = ".",
    show_progress: bool = True,
):
    """Train a tokenizer on a dataset.

    Args:
        corpus (Dataset, IterableDataset or iterable of strings):
            Corpus to train the tokenizer on. Can either be a Hugging Face
            `Dataset` or `IterableDataset` object with a feature named 'text',
            or simply an iterable of strings.
        config (TokenizerConfig or dict):
            Configuration for the tokenizer.
        save_tokenizer (bool, optional):
            Whether to save the tokenizer to disk. Defaults to True.
        output_dir (str or Path, optional):
            Directory to save the tokenizer to. Only relevant if
            `save_tokenizer` is True. Defaults to the current directory.
        show_progress (bool, optional):
            Whether to show progress bars. Defaults to True.

    Returns:
        Tokenizer:
            Trained tokenizer.
    """
    # Convert config to `TokenizerConfig` instance if a dict is given
    if isinstance(config, dict):
        config = TokenizerConfig(**config)

    # Convert corpus to an iterable of strings if a Dataset is given
    if isinstance(corpus, Dataset) or isinstance(corpus, IterableDataset):
        corpus = (sample["text"] for sample in corpus)

    # Instantiate the tokenizer model
    if config.tokenizer_type == "bpe":
        model = models.BPE(unk_token=config.unk_token)
    elif config.tokenizer_type == "wordpiece":
        model = models.WordPiece(unk_token=config.unk_token)  # noqa
    elif config.tokenizer_type == "unigram":
        model = models.Unigram()  # noqa

    # Instantiate the tokenizer
    tokenizer = tokenizers.Tokenizer(model)

    # Initialise the special tokens and add them to the tokenizer
    special_tokens = [
        AddedToken(config.pad_token, single_word=True, normalized=False),
        AddedToken(config.bos_token, single_word=True, normalized=False),
        AddedToken(config.eos_token, single_word=True, normalized=False),
        AddedToken(config.unk_token, single_word=True, normalized=False),
        AddedToken(config.mask_token, single_word=True, normalized=False),
    ]
    tokenizer.add_special_tokens(special_tokens)

    # Initialise the normalizer and add it to the tokenizer
    normalizer_list = list()
    if config.nfkc_normalization:
        normalizer_list.append(normalizers.NFKC())
    if config.lower_case:
        normalizer_list.append(normalizers.Lowercase())
    normalizer = normalizers.Sequence(normalizer_list)  # noqa
    tokenizer.normalizer = normalizer

    # Shorthand for whether a prefix whitespace should be added to words
    pre_ws = config.add_prefix_space

    # Initialise the pre-tokenizer and add it to the tokenizer
    pre_tok_list = list()
    if config.byte_level:
        pre_tok_list.append(pre_tokenizers.ByteLevel(add_prefix_space=pre_ws))
    if config.sentence_piece:
        pre_tok_list.append(pre_tokenizers.Metaspace(add_prefix_space=pre_ws))
    if not config.byte_level and not config.sentence_piece:
        pre_tok_list.append(pre_tokenizers.Whitespace())
    pre_tokenizer = pre_tokenizers.Sequence(pre_tok_list)
    tokenizer.pre_tokenizer = pre_tokenizer

    # Initialise the post-processor
    if config.add_sep_and_cls_tokens:
        params = dict(
            cls=(config.bos_token, 1),
            sep=(config.eos_token, 2),
            trim_offsets=True,
            add_prefix_space=pre_ws,
        )
        tokenizer.post_processor = processors.RobertaProcessing(**params)
    elif config.byte_level:
        tokenizer.post_processor = processors.ByteLevel(trim_offsets=True)

    # Initialise the decoder
    if config.tokenizer_type == "bpe":
        tokenizer.decoder = decoders.BPEDecoder()
    elif config.tokenizer_type == "wordpiece":
        tokenizer.decoder = decoders.WordPiece(prefix="##", cleanup=True)
    elif config.sentence_piece:
        tokenizer.decoder = decoders.Metaspace(add_prefix_space=pre_ws)
    elif config.byte_level:
        tokenizer.decoder = decoders.ByteLevel()

    # Enable truncation
    if config.truncation:
        tokenizer.enable_truncation(max_length=config.max_length)

    # Enable padding
    if config.padding:
        tokenizer.enable_padding(pad_id=0, pad_type_id=0, pad_token=config.pad_token)

    # Initialise the trainer
    if config.tokenizer_type == "bpe":
        trainer = trainers.BpeTrainer(
            vocab_size=config.vocab_size,
            show_progress=show_progress,
            special_tokens=special_tokens,
        )
    elif config.tokenizer_type == "wordpiece":
        trainer = trainers.WordPieceTrainer(
            vocab_size=config.vocab_size,
            show_progress=show_progress,
            special_tokens=special_tokens,
        )
    elif config.tokenizer_type == "unigram":
        trainer = trainers.UnigramTrainer(
            vocab_size=config.vocab_size,
            special_tokens=special_tokens,
            show_progress=show_progress,
            unk_token="<unk>",
        )

    # Train the tokenizer
    tokenizer.train_from_iterator(iterator=corpus, trainer=trainer)

    # If the output directory does not exist, create it
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save the tokenizer and configuration
    if save_tokenizer:
        tokenizer.save(str(output_dir / "tokenizer.json"))
        config.save(str(output_dir / "tokenizer_config.json"))

    return tokenizer
