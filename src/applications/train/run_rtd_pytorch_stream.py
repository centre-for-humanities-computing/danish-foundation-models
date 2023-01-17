"""
Fine-tuning ELECTRA on a text file or a dataset.

Outline copied from:
https://github.com/huggingface/transformers/blob/main/examples/pytorch/language-modeling/run_mlm.py
Adapted for streaming datasets. The adaption took inspiration from:
https://github.com/huggingface/transformers/blob/main/examples/research_projects/jax-projects/dataset-streaming/run_mlm_flax_stream.py


Here is the full list of checkpoints on the hub that can be fine-tuned by this script:
https://huggingface.co/models?filter=fill-mask

Note: requires the dev version of HF datasets:
https://github.com/huggingface/datasets

Example usage:

.. code::

    python src/applications/train/run_mlm_pytorch_stream.py \
        --train_file test.txt \
        --model_name_or_path roberta-base \
        --output_dir /tmp/models/ \
        --do_train \
        --overwrite_output_dir \
        --streaming \
        --validation_split 1000 \
        --max_steps 1 \
        --max_train_samples 1000
"""
import json
import logging
import math
import os
import sys
from dataclasses import dataclass, field
from itertools import chain
from pathlib import Path
from typing import Optional, Tuple, Union

import datasets
import transformers
import wandb
from datasets import Dataset, DatasetDict, IterableDataset, load_dataset, load_metric

# from dfm.data import load_dcc
from electra import ElectraDataCollator, ELECTRAModel, ElectraTrainer
from transformers import (
    CONFIG_MAPPING,
    MODEL_FOR_MASKED_LM_MAPPING,
    AutoConfig,
    AutoModelForMaskedLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    ElectraConfig,
    ElectraForMaskedLM,
    ElectraForPreTraining,
    ElectraTokenizerFast,
    HfArgumentParser,
    PreTrainedTokenizerFast,
    Trainer,
    TrainingArguments,
    is_torch_tpu_available,
    set_seed,
)
from transformers.trainer_utils import get_last_checkpoint

from dfm.data import load_dcc
from electra import ElectraDataCollator, ElectraTrainer, ELECTRAModel

os.environ["TOKENIZERS_PARALLELISM"] = "true"

logger = logging.getLogger(__name__)
MODEL_CONFIG_CLASSES = list(MODEL_FOR_MASKED_LM_MAPPING.keys())
MODEL_TYPES = tuple(conf.model_type for conf in MODEL_CONFIG_CLASSES)


@dataclass
class ModelArguments:
    """Arguments pertaining to which model/config/tokenizer we are going to fine-tune, or train from scratch."""

    model_name_or_path: Optional[str] = field(
        default=None,
        metadata={
            "help": (
                "The model checkpoint for weights initialization.Don't set if you want to train a model from scratch."
            )
        },
    )
    model_type: Optional[str] = field(
        default=None,
        metadata={
            "help": "If training from scratch, pass a model type from the list: "
            + ", ".join(MODEL_TYPES)
        },
    )
    config_overrides: Optional[str] = field(
        default=None,
        metadata={
            "help": (
                "Override some existing default config settings when a model is trained from scratch. Example: "
                "n_embd=10,resid_pdrop=0.2,scale_attn_weights=false,summary_type=cls_index"
            )
        },
    )
    config_name: Optional[str] = field(
        default=None,
        metadata={
            "help": "Pretrained config name or path if not the same as model_name"
        },
    )
    discriminator_config_name: Optional[str] = field(
        default=None,
        metadata={
            "help": "Pretrained config name or path if not the same as model_name for the discriminator"
        },
    )
    generator_config_name: Optional[str] = field(
        default=None,
        metadata={
            "help": "Pretrained config name or path if not the same as model_name for the generator"
        },
    )
    tokenizer_name: Optional[str] = field(
        default=None,
        metadata={
            "help": "Pretrained tokenizer name or path if not the same as model_name"
        },
    )
    cache_dir: Optional[str] = field(
        default=None,
        metadata={
            "help": "Where do you want to store the pretrained models downloaded from huggingface.co"
        },
    )
    use_fast_tokenizer: bool = field(
        default=True,
        metadata={
            "help": "Whether to use one of the fast tokenizer (backed by the tokenizers library) or not."
        },
    )
    use_pretrained_tokenizer: bool = field(
        default=False,
        metadata={
            "help": "Whether to use a pretrained tokenizer, see https://huggingface.co/docs/transformers/fast_tokenizers"
        },
    )
    model_revision: str = field(
        default="main",
        metadata={
            "help": "The specific model version to use (can be a branch name, tag name or commit id)."
        },
    )
    use_auth_token: bool = field(
        default=False,
        metadata={
            "help": (
                "Will use the token generated when running `transformers-cli login` (necessary to use this script "
                "with private models)."
            )
        },
    )

    def __post_init__(self):
        if self.config_overrides is not None and (
            self.config_name is not None or self.model_name_or_path is not None
        ):
            raise ValueError(
                "--config_overrides can't be used in combination with --config_name or --model_name_or_path"
            )


@dataclass
class DataTrainingArguments:
    """Arguments pertaining to what data we are going to input our model for training and eval."""

    dataset_name: Optional[str] = field(
        default=None,
        metadata={"help": "The name of the dataset to use (via the datasets library)."},
    )
    dataset_config_name: Optional[str] = field(
        default=None,
        metadata={
            "help": "The configuration name of the dataset to use (via the datasets library)."
        },
    )
    nat_weight: Optional[float] = field(
        default=0.25,
        metadata={
            "help": "The probability of sampling from the NAT dataset, assuming the dataset is DCC"
        },
    )
    danews_weight: Optional[float] = field(
        default=0.25,
        metadata={
            "help": "The probability of sampling from the DaNews dataset, assuming the dataset is DCC"
        },
    )
    hopetwitter_weight: Optional[float] = field(
        default=0.25,
        metadata={
            "help": "The probability of sampling from the HopeTwitter dataset, assuming the dataset is DCC"
        },
    )
    dagw_dfm_weight: Optional[float] = field(
        default=0.25,
        metadata={
            "help": "The probability of sampling from the DAGW_dfm dataset, assuming the dataset is DCC"
        },
    )

    streaming: bool = field(
        default=False,
        metadata={"help": "Whether to load the dataset using streaming"},
    )
    train_file: Optional[str] = field(
        default=None, metadata={"help": "The input training data file (a text file)."}
    )
    validation_file: Optional[str] = field(
        default=None,
        metadata={
            "help": "An optional input evaluation data file to evaluate the perplexity on (a text file)."
        },
    )
    overwrite_cache: bool = field(
        default=False,
        metadata={"help": "Overwrite the cached training and evaluation sets"},
    )
    validation_split: Optional[int] = field(
        default=5,
        metadata={
            "help": "The percentage of the train set used as validation set in case"
            + "there's no validation split. If streaming is True then this will be the count"
        },
    )
    max_seq_length: Optional[int] = field(
        default=None,
        metadata={
            "help": (
                "The maximum total input sequence length after tokenization. Sequences longer "
                "than this will be truncated."
            )
        },
    )
    preprocessing_num_workers: Optional[int] = field(
        default=None,
        metadata={"help": "The number of processes to use for the preprocessing."},
    )
    mlm_probability: float = field(
        default=0.15,
        metadata={"help": "Ratio of tokens to mask for masked language modeling loss"},
    )
    line_by_line: bool = field(
        default=False,
        metadata={
            "help": "Whether distinct lines of text in the dataset are to be handled as distinct sequences."
        },
    )
    pad_to_max_length: bool = field(
        default=False,
        metadata={
            "help": (
                "Whether to pad all samples to `max_seq_length`. "
                "If False, will pad the samples dynamically when batching to the maximum length in the batch."
            )
        },
    )
    max_train_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": (
                "For debugging purposes or quicker training, truncate the number of training examples to this "
                "value if set."
            )
        },
    )
    max_eval_samples: Optional[int] = field(
        default=None,
        metadata={
            "help": (
                "For debugging purposes or quicker training, truncate the number of evaluation examples to this "
                "value if set."
            )
        },
    )

    def __post_init__(self):
        if (
            self.dataset_name is None
            and self.train_file is None
            and self.validation_file is None
        ):
            raise ValueError(
                "Need either a dataset name or a training/validation file."
            )
        else:
            if self.train_file is not None:
                extension = self.train_file.split(".")[-1]
                if extension not in ["csv", "json", "txt"]:
                    raise ValueError(
                        "`train_file` should be a csv, a json or a txt file."
                    )
            if self.validation_file is not None:
                extension = self.validation_file.split(".")[-1]
                if extension not in ["csv", "json", "txt"]:
                    raise ValueError(
                        "`validation_file` should be a csv, a json or a txt file."
                    )


def get_dataset(
    model_args: ModelArguments, data_args: DataTrainingArguments
) -> DatasetDict:
    """Get the datasets.

    You can either provide your own CSV/JSON/TXT training and
    evaluation files (see below) or just provide the name of one of the public datasets
    available on the hub at https://huggingface.co/datasets/ (the dataset will be
    downloaded automatically from the Hugging Face Hub

    For CSV/JSON files, this script will use the column called 'text' or the first
    column. You can easily tweak this behavior (see below)

    In distributed training, the load_dataset function guarantee that only one local
    process can concurrently download the dataset.

    Args:
        model_args (ModelArguments): Arguments supplied to the model, including
            cache_dir and auth_token.
        data_args (DataTrainingArguments): Arguments for loading the dataset, including
            config_name, dataset_name, streaming etc.

    Returns:
        DatasetDict: a DatasetDict containing a train, test and validation
            split.
    """
    if data_args.dataset_name is not None:
        if data_args.dataset_name.startswith("dcc"):
            # must be streaming
            assert data_args.streaming is True
            version = data_args.dataset_name.split("_")[1][1:]  # ignore the v
            raw_datasets = load_dcc(
                version=version,
                probabilities={
                    "danews": data_args.danews_weight,
                    "dagw_dfm": data_args.dagw_dfm_weight,
                    "hopetwitter": data_args.hopetwitter_weight,
                    "nat": data_args.nat_weight,
                },
            )
        else:
            # Downloading and loading a dataset from the hub.
            raw_datasets = load_dataset(
                data_args.dataset_name,
                data_args.dataset_config_name,
                cache_dir=model_args.cache_dir,
                use_auth_token=True if model_args.use_auth_token else None,
                streaming=data_args.streaming,
            )
        if "validation" not in raw_datasets.keys():
            if data_args.streaming is False:
                raw_datasets["validation"] = load_dataset(
                    data_args.dataset_name,
                    data_args.dataset_config_name,
                    split=f"train[:{data_args.validation_split}%]",
                    cache_dir=model_args.cache_dir,
                    use_auth_token=True if model_args.use_auth_token else None,
                    streaming=data_args.streaming,
                )
                raw_datasets["train"] = load_dataset(
                    data_args.dataset_name,
                    data_args.dataset_config_name,
                    split=f"train[{data_args.validation_split}%:]",
                    cache_dir=model_args.cache_dir,
                    use_auth_token=True if model_args.use_auth_token else None,
                    streaming=data_args.streaming,
                )
            else:
                raw_datasets["validation"] = raw_datasets["train"].take(
                    data_args.validation_split
                )
                raw_datasets["train"] = raw_datasets["train"].skip(
                    data_args.validation_split
                )

    else:
        data_files = {}
        if data_args.train_file is not None:
            data_files["train"] = data_args.train_file
            extension = data_args.train_file.split(".")[-1]
        if data_args.validation_file is not None:
            data_files["validation"] = data_args.validation_file
            extension = data_args.validation_file.split(".")[-1]
        if extension == "txt":
            extension = "text"
        raw_datasets = load_dataset(
            extension,
            data_files=data_files,
            cache_dir=model_args.cache_dir,
            use_auth_token=True if model_args.use_auth_token else None,
            streaming=data_args.streaming,
        )

        # If no validation data is there, validation_split will be used to divide the dataset.
        if "validation" not in raw_datasets.keys():
            if data_args.streaming is False:
                raw_datasets["validation"] = load_dataset(
                    extension,
                    data_files=data_files,
                    split=f"train[:{data_args.validation_split}%]",
                    cache_dir=model_args.cache_dir,
                    use_auth_token=True if model_args.use_auth_token else None,
                    streaming=data_args.streaming,
                )
                raw_datasets["train"] = load_dataset(
                    extension,
                    data_files=data_files,
                    split=f"train[{data_args.validation_split}%:]",
                    cache_dir=model_args.cache_dir,
                    use_auth_token=True if model_args.use_auth_token else None,
                    streaming=data_args.streaming,
                )
            else:
                raw_datasets["validation"] = raw_datasets["train"].take(
                    data_args.validation_split
                )
                raw_datasets["train"] = raw_datasets["train"].skip(
                    data_args.validation_split
                )

    # See more about loading any type of standard or custom dataset (from files, python
    # dict, pandas DataFrame, etc) at
    # https://huggingface.co/docs/datasets/loading_datasets.html.
    return raw_datasets


def get_tokenizer_and_model(
    model_args: ModelArguments,
) -> Tuple[AutoTokenizer, ELECTRAModel]:
    """Load pretrained model and tokenizer.

    Distributed training:
    The .from_pretrained methods guarantee that only one local process can concurrently
    download model & vocab.

    Args:
        model_args (ModelArguments): Arguments for loading the model.

    Returns:
        Tuple[AutoTokenizer, AutoModelForMaskedLM]:
            A tuple containing the tokenizer and model for training.
    """
    config_kwargs = {
        "cache_dir": model_args.cache_dir,
        "revision": model_args.model_revision,
        "use_auth_token": True if model_args.use_auth_token else None,
    }
    if model_args.config_name:
        config = AutoConfig.from_pretrained(model_args.config_name, **config_kwargs)
    elif model_args.model_name_or_path:
        config = AutoConfig.from_pretrained(
            model_args.model_name_or_path, **config_kwargs
        )
    else:
        config = CONFIG_MAPPING[model_args.model_type]()
        logger.warning("You are instantiating a new config instance from scratch.")
        if model_args.config_overrides is not None:
            logger.info(f"Overriding config: {model_args.config_overrides}")
            config.update_from_string(model_args.config_overrides)
            logger.info(f"New config: {config}")

    if model_args.discriminator_config_name:
        disc_config = ElectraConfig.from_pretrained(
            model_args.discriminator_config_name,
            from_tf=bool(".ckpt" in model_args.model_name_or_path),
            cache_dir=model_args.cache_dir,
            revision=model_args.model_revision,
            use_auth_token=True if model_args.use_auth_token else None,
            ignore_mismatched_sizes=True,
        )
    else:
        disc_config = ElectraConfig.from_pretrained(
            "google/electra-small-discriminator"
        )

    if model_args.generator_config_name:
        gen_config = ElectraConfig.from_pretrained(model_args.generator_config_name)
    else:
        gen_config = ElectraConfig.from_pretrained("google/electra-small-generator")

    tokenizer_kwargs = {
        "cache_dir": model_args.cache_dir,
        "use_fast": model_args.use_fast_tokenizer,
        "revision": model_args.model_revision,
        "use_auth_token": True if model_args.use_auth_token else None,
    }
    if model_args.tokenizer_name:
        if model_args.use_pretrained_tokenizer:
            tok_path = Path(model_args.tokenizer_name)
            tokenizer = ElectraTokenizerFast(
                tokenizer_file=str(tok_path / "tokenizer.json"),
                model_max_length=gen_config.max_position_embeddings,
            )
            with open(tok_path / "config.json", "r") as f:
                tok_config = json.load(f)
            tokenizer.mask_token = tok_config["mask_token"]
            tokenizer.unk_token = tok_config["unk_token"]
            tokenizer.bos_token = tok_config["bos_token"]
            tokenizer.eos_token = tok_config["eos_token"]
            tokenizer.pad_token = tok_config["pad_token"]

        else:
            tokenizer = AutoTokenizer.from_pretrained(
                model_args.tokenizer_name, **tokenizer_kwargs
            )
    elif model_args.model_name_or_path:
        tokenizer = AutoTokenizer.from_pretrained(
            model_args.model_name_or_path, **tokenizer_kwargs
        )
    else:
        raise ValueError(
            "You are instantiating a new tokenizer from scratch. This is not supported by this script."
            "You can do it from another script, save it, and load it from here, using --tokenizer_name."
        )

    if model_args.model_name_or_path:
        generator = ElectraForMaskedLM(gen_config)
        discriminator = ElectraForPreTraining(disc_config)

        model = ELECTRAModel(
            generator,
            discriminator,
            config=config,
        )
    else:
        logger.info("Training new model from scratch")
        model = AutoModelForMaskedLM.from_config(config)

    model.resize_token_embeddings(len(tokenizer))
    return tokenizer, model


def preprocess_dataset(  # noqa: C901
    data_args: DataTrainingArguments,
    training_args: TrainingArguments,
    raw_datasets: DatasetDict,
    tokenizer: AutoTokenizer,
) -> DatasetDict:
    """Preprocess the datasets. Including tokenization and grouping of texts."""
    # First we tokenize the texts.
    if training_args.do_train:
        if data_args.streaming:
            example = next(iter(raw_datasets["train"]))
            column_names = list(example.keys())
        else:
            column_names = raw_datasets["train"].column_names
    else:
        if data_args.streaming:
            example = next(iter(raw_datasets["train"]))
            column_names = list(example.keys())
        else:
            column_names = raw_datasets["validation"].column_names
    text_column_name = "text" if "text" in column_names else column_names[0]

    if data_args.max_seq_length is None:
        max_seq_length = tokenizer.model_max_length
        if max_seq_length > 1024:
            logger.warning(
                f"The tokenizer picked seems to have a very large `model_max_length` ({tokenizer.model_max_length}). "
                "Picking 1024 instead. You can change that default value by passing --max_seq_length xxx."
            )
            max_seq_length = 1024
    else:
        if data_args.max_seq_length > tokenizer.model_max_length:
            logger.warning(
                f"The max_seq_length passed ({data_args.max_seq_length}) is larger than the maximum length for the"
                f"model ({tokenizer.model_max_length}). Using max_seq_length={tokenizer.model_max_length}."
            )
        max_seq_length = min(data_args.max_seq_length, tokenizer.model_max_length)

    if data_args.line_by_line:
        # When using line_by_line, we just tokenize each nonempty line.
        padding = "max_length" if data_args.pad_to_max_length else False

        def tokenize_function(examples):
            # Remove empty lines
            examples[text_column_name] = [
                line
                for line in examples[text_column_name]
                if len(line) > 0 and not line.isspace()
            ]
            return tokenizer(
                examples[text_column_name],
                padding=padding,
                truncation=True,
                max_length=max_seq_length,
                # We use this option because DataCollatorForLanguageModeling (see below) is more efficient when it
                # receives the `special_tokens_mask`.
                return_special_tokens_mask=True,
            )

        desc = "Running tokenizer on dataset line_by_line"
    else:
        # Otherwise, we tokenize every text, then concatenate them together before splitting them in smaller parts.
        # We use `return_special_tokens_mask=True` because DataCollatorForLanguageModeling (see below) is more
        # efficient when it receives the `special_tokens_mask`.
        def tokenize_function(examples):
            return tokenizer(
                examples[text_column_name], return_special_tokens_mask=True
            )

        desc = "Running tokenizer on every text in dataset"

    with training_args.main_process_first(desc="dataset map tokenization"):
        _map_config = dict(
            function=tokenize_function,
            batched=True,
            remove_columns=column_names,
        )
        if data_args.streaming is False:
            _map_config["num_proc"] = data_args.preprocessing_num_workers
            _map_config["load_from_cache_file"] = not data_args.overwrite_cache
            _map_config["desc"] = desc

        tokenized_datasets = raw_datasets.map(**_map_config)

        # Main data processing function that will concatenate all texts from our dataset and generate chunks of
        # max_seq_length.
        def group_texts(examples):
            # Concatenate all texts.
            concatenated_examples = {
                k: list(chain(*examples[k])) for k in examples.keys()
            }
            total_length = len(concatenated_examples[list(examples.keys())[0]])
            # We drop the small remainder, we could add padding if the model supported it instead of this drop, you can
            # customize this part to your needs.
            if total_length >= max_seq_length:
                total_length = (total_length // max_seq_length) * max_seq_length
            # Split by chunks of max_len.
            result = {
                k: [
                    t[i : i + max_seq_length]
                    for i in range(0, total_length, max_seq_length)
                ]
                for k, t in concatenated_examples.items()
            }
            return result

        # Note that with `batched=True`, this map processes 1,000 texts together, so group_texts throws away a
        # remainder for each of those groups of 1,000 texts. You can adjust that batch_size here but a higher value
        # might be slower to preprocess.
        #
        # To speed up this part, we use multiprocessing. See the documentation of the map method for more information:
        # https://huggingface.co/docs/datasets/package_reference/main_classes.html#datasets.Dataset.map

        with training_args.main_process_first(desc="grouping texts together"):
            _map_config = dict(
                function=group_texts,
                batched=True,
            )
            if data_args.streaming is False:
                _map_config["num_proc"] = (data_args.preprocessing_num_workers,)
                _map_config["load_from_cache_file"] = (not data_args.overwrite_cache,)
                _map_config["desc"] = f"Grouping texts in chunks of {max_seq_length}"
            tokenized_datasets = tokenized_datasets.map(**_map_config)
    return tokenized_datasets


def train(
    trainer: Trainer,
    train_dataset: Union[IterableDataset, Dataset],
    training_args: TrainingArguments,
    data_args: DataTrainingArguments,
    last_checkpoint,
) -> dict:
    """Train using the trainer

    Args:
        trainer (Trainer): The trainer.
        train_dataset (Union[IterableDataset, Dataset]): The training dataset.
        training_args (TrainingArguments): Training arguments including
            resume_from_checkpoint.
        data_args (DataTrainingArguments): Dataset arguments including streaming and
            max_train_samples.

    Returns:
        dict: a dict on informationed to be logged.
    """
    checkpoint = None
    if training_args.resume_from_checkpoint is not None:
        checkpoint = training_args.resume_from_checkpoint
    elif last_checkpoint is not None:
        checkpoint = last_checkpoint
    # log trainable parameters to wandb
    num_trainable_params = sum(
        p.numel() for p in trainer.model.parameters() if p.requires_grad
    )
    num_params = sum(p.numel() for p in trainer.model.parameters())
    wandb.config.update(
        {"num_trainable_params": num_trainable_params, "num_params": num_params}
    )

    train_result = trainer.train(resume_from_checkpoint=checkpoint)
    trainer.save_model()  # Saves the tokenizer too for easy upload
    metrics = train_result.metrics

    if data_args.streaming:
        if data_args.max_train_samples:
            metrics["train_samples"] = data_args.max_train_samples
    else:
        max_train_samples = (
            data_args.max_train_samples
            if data_args.max_train_samples is not None
            else len(train_dataset)
        )
        metrics["train_samples"] = min(max_train_samples, len(train_dataset))

    trainer.log_metrics("train", metrics)
    trainer.save_metrics("train", metrics)
    trainer.save_state()


def evaluate(
    trainer: Trainer,
    eval_dataset: Union[IterableDataset, Dataset],
    data_args: DataTrainingArguments,
    model_args: ModelArguments,
):
    """Evaluate model

    Args:
        trainer (Trainer): The trainer.
        eval_dataset (Union[IterableDataset, Dataset]): The evaluation dataset
        data_args (DataTrainingArguments): The dataset arguments, including
            max_eval_samples.
        model_args (ModelArguments): The model arguments, including model_name_or_path.

    Returns:
        dict: A dict of information to be logged.
    """
    logger.info("*** Evaluate ***")

    metrics = trainer.evaluate()

    if data_args.streaming is False:
        max_eval_samples = (
            data_args.max_eval_samples
            if data_args.max_eval_samples is not None
            else len(eval_dataset)
        )
        metrics["eval_samples"] = min(max_eval_samples, len(eval_dataset))
    try:
        perplexity = math.exp(metrics["eval_loss"])
    except OverflowError:
        perplexity = float("inf")
    metrics["perplexity"] = perplexity

    trainer.log_metrics("eval", metrics)
    trainer.save_metrics("eval", metrics)

    kwargs = {"finetuned_from": model_args.model_name_or_path, "tasks": "fill-mask"}
    if data_args.dataset_name is not None:
        kwargs["dataset_tags"] = data_args.dataset_name
        if data_args.dataset_config_name is not None:
            kwargs["dataset_args"] = data_args.dataset_config_name
            kwargs[
                "dataset"
            ] = f"{data_args.dataset_name} {data_args.dataset_config_name}"
        else:
            kwargs["dataset"] = data_args.dataset_name

    return kwargs


def main():  # noqa: C901
    # See all possible arguments in src/transformers/training_args.py
    # or by passing the --help flag to this script.
    # We now keep distinct sets of args, for a cleaner separation of concerns.

    parser = HfArgumentParser(
        (ModelArguments, DataTrainingArguments, TrainingArguments)
    )
    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        # If we pass only one argument to the script and it's the path to a json file,
        # let's parse it to get our arguments.
        model_args, data_args, training_args = parser.parse_json_file(
            json_file=os.path.abspath(sys.argv[1])
        )
    else:
        model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    wandb.init(
        project="danish-foundation-models",
        entity="chcaa",
        config=parser.parse_args(),
        tags=["mlm", "pytorch"],
        save_code=True,
        group="mlm",
    )

    # Setup logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    log_level = training_args.get_process_log_level()
    logger.setLevel(log_level)
    datasets.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.set_verbosity(log_level)
    transformers.utils.logging.enable_default_handler()
    transformers.utils.logging.enable_explicit_format()

    # Log on each process the small summary:
    logger.warning(
        f"Process rank: {training_args.local_rank}, device: {training_args.device}, n_gpu: {training_args.n_gpu}"
        + f"distributed training: {bool(training_args.local_rank != -1)}, 16-bits training: {training_args.fp16}"
    )
    # Set the verbosity to info of the Transformers logger (on main process only):
    logger.info(f"Training/evaluation parameters {training_args}")

    # Detecting last checkpoint.
    last_checkpoint = None
    if (
        os.path.isdir(training_args.output_dir)
        and training_args.do_train
        and not training_args.overwrite_output_dir
    ):
        last_checkpoint = get_last_checkpoint(training_args.output_dir)
        if last_checkpoint is None and len(os.listdir(training_args.output_dir)) > 0:
            raise ValueError(
                f"Output directory ({training_args.output_dir}) already exists and is not empty. "
                "Use --overwrite_output_dir to overcome."
            )
        elif (
            last_checkpoint is not None and training_args.resume_from_checkpoint is None
        ):
            logger.info(
                f"Checkpoint detected, resuming training at {last_checkpoint}. To avoid this behavior, change "
                "the `--output_dir` or add `--overwrite_output_dir` to train from scratch."
            )

    # Set seed before initializing model.
    set_seed(training_args.seed)

    raw_datasets = get_dataset(model_args, data_args)

    tokenizer, model = get_tokenizer_and_model(model_args)

    tokenized_datasets = preprocess_dataset(
        data_args, training_args, raw_datasets, tokenizer
    )

    if training_args.do_train:
        if "train" not in tokenized_datasets:
            raise ValueError("--do_train requires a train dataset")
        train_dataset = tokenized_datasets["train"]
        if data_args.max_train_samples is not None:
            if data_args.streaming:
                train_dataset = train_dataset.take(data_args.max_train_samples)
            else:
                max_train_samples = min(len(train_dataset), data_args.max_train_samples)
                train_dataset = train_dataset.select(range(max_train_samples))

    if training_args.do_eval:
        if "validation" not in tokenized_datasets:
            raise ValueError("--do_eval requires a validation dataset")
        eval_dataset = tokenized_datasets["validation"]
        if data_args.max_eval_samples is not None:
            if data_args.streaming:
                eval_dataset = eval_dataset.take(data_args.max_eval_samples)
            else:
                max_eval_samples = min(len(eval_dataset), data_args.max_eval_samples)
                eval_dataset = eval_dataset.select(range(max_eval_samples))

        def preprocess_logits_for_metrics(logits, labels):
            if isinstance(logits, tuple):
                # Depending on the model and config, logits may contain extra tensors,
                # like past_key_values, but logits always come first
                logits = logits[0]
            return logits.argmax(dim=-1)

        metric = load_metric("accuracy")
        # import evaluate
        # metric = evaluate.load_metric("accuracy")

        def compute_metrics(eval_preds):
            preds, labels = eval_preds
            # preds have the same shape as the labels, after the argmax(-1) has been calculated
            # by preprocess_logits_for_metrics
            labels = labels.reshape(-1)
            preds = preds.reshape(-1)
            mask = labels != -100
            labels = labels[mask]
            preds = preds[mask]
            return metric.compute(predictions=preds, references=labels)

    # Data collator
    data_collator = ElectraDataCollator(
        tokenizer=tokenizer,
        mlm_probability=data_args.mlm_probability,
        replace_prob=data_args.replace_probability,
        original_prob=data_args.original_probability,
    )

    # Initialize our Trainer
    _training_args = dict(
        model=model,
        args=training_args,
        train_dataset=train_dataset if training_args.do_train else None,
        eval_dataset=eval_dataset if training_args.do_eval else None,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics
        if training_args.do_eval and not is_torch_tpu_available()
        else None,
        preprocess_logits_for_metrics=preprocess_logits_for_metrics
        if training_args.do_eval and not is_torch_tpu_available()
        else None,
    )

    if data_args.streaming:
        # convert to pytorch iterable dataset
        if training_args.do_train:
            _training_args["train_dataset"] = train_dataset.with_format("torch")
        if training_args.do_eval:
            _training_args["eval_dataset"] = eval_dataset.with_format("torch")

    trainer = ElectraTrainer(**_training_args)

    # Training
    if training_args.do_train:
        train(trainer, train_dataset, training_args, data_args, last_checkpoint)

    # Evaluation
    if training_args.do_eval:
        kwargs = evaluate(trainer, eval_dataset, data_args, model_args)

        if training_args.push_to_hub:
            trainer.push_to_hub(**kwargs)
        else:
            trainer.create_model_card(**kwargs)


if __name__ == "__main__":
    main()
