"""
Training script for training masked language models with sweeps

Authors:
    Lasse Hansen
    Malte Højmark-Bertelsen

```bash
pip install -e .
python dfm/train.py --config tests/test_configs/pretrain_config.yaml
```
"""

import argparse
from dataclasses import dataclass
from typing import List, Optional, Union

from datasets import interleave_datasets
from transformers import (AutoConfig, AutoModelForPreTraining, AutoTokenizer,
                          DataCollatorForLanguageModeling, Trainer,
                          TrainingArguments)

from .data.load import dfm_load_dataset
from .modelling.model_types import MODEL_TYPES
from .modelling.preprocess import preprocess_dataset
from .modelling.utils import read_yaml


def main(args):
    """Main function for running the training script."""
    trainer = DFMTrainer(
        pretraining_config_path=args.config,
    )
    trainer.train()


# TODO:
# create configs for models (training + model)
# create collator for T5
# consider whether to actually use dataclasses.
@dataclass
class DataArguments:
    """This is a dataclass for dataarguments.

    Args:
            dataset_names (list(str)): List of names of the datasets wanted to be used in training.
            interleave (bool): Whether to interleave datasets.
            interleave_probabilities (list(bool)): The different interleave probabilties.
            num_proc (int): How many cores to run the preprocessing with.
            mlm_probability (float): The masking probability.
    """

    dataset_names: List[str]
    interleave: bool
    interleave_probabilities: List[float]
    num_proc: int
    mlm_probability: float

    @classmethod
    def from_yaml(cls, config_path: str) -> dict:
        """Reads a yaml file into a dictionary.

        Args:
            config_path (str): Path to the configuration YAML file.

        Returns:
            dict: Dictionary containing the data arguments.
        """

        # Read dataarguments from yaml file
        file = read_yaml(config_path)
        keys = cls.__dataclass_fields__.keys()
        yaml_data = file["data_arguments"]

        # Get the yaml data
        normal_yaml_data = {key: yaml_data[key] for key in yaml_data if key in keys}
        tmp = cls(**normal_yaml_data)
        return tmp


@dataclass
class ModelArguments:
    """This is a dataclass for modelarguments.

    Args:
            model_type (str): What kind of model you want to train. Currently supported is 'autoencoding'.
            model_name (str): Name of the model.
    """

    model_type: str
    model_name: str

    @classmethod
    def from_yaml(cls, config_path: str) -> dict:
        """Reads a yaml file into a dictionary.

        Args:
            config_path (str): Path to the configuration YAML file.

        Returns:
            dict: Dictionary containing the model arguments.
        """

        # Read dataarguments from yaml file
        file = read_yaml(config_path)
        keys = cls.__dataclass_fields__.keys()
        yaml_data = file["model_arguments"]

        # Get the yaml data
        normal_yaml_data = {key: yaml_data[key] for key in yaml_data if key in keys}
        tmp = cls(**normal_yaml_data)
        return tmp


class DFMTrainer:
    """class for training a Danish Foundation Model."""

    def __init__(
        self,
        pretraining_config_path: str,
    ) -> None:
        """
        Training function with Weights & Biases logging.

        Args:
            model_name (str): Path to a model.
            pretraining_config_path (str): Path to a pretraining config.
            datasets (list(str)): List of dataset names from the Hugging Face hub.
            interleave_probabilities (List[float]): how to weight datasets in interleave
        """
        # Configuration arguments
        self.pretraining_config_path = pretraining_config_path
        self.training_args = read_yaml(self.pretraining_config_path)[
            "training_arguments"
        ]
        self.data_args = DataArguments.from_yaml(self.pretraining_config_path)
        self.model_args = ModelArguments.from_yaml(self.pretraining_config_path)

        self.dataset_names = self.data_args.dataset_names
        self.interleave = self.data_args.interleave
        self.interleave_probabilities = self.data_args.interleave_probabilities

        self.model_type = self.model_args.model_type
        self.model_name = self.model_args.model_name

        if self.model_type not in MODEL_TYPES:
            raise ValueError(f"Invalid model type. Choose one from: {MODEL_TYPES}")

    def train(
        self,
        resume_from_checkpoint: Optional[Union[str, bool]] = None,
    ):
        """Main training method for Danish Foundation Models

        Args:
            resume_from_checkpoint (Optional[Union[str, bool]], optional):
                Loads a model previously saved by a Trainer.
                If str it loads it from the path,
                if bool it looads it from the most recently
                save model from the training_args.output_dir. Defaults to None.

        Raises:
            NotImplementedError: Raises a NotImplementedError if a model type not yet supported is passed.
        """

        HF_config = AutoConfig.from_pretrained(self.model_name)
        tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, return_special_tokens_mask=True
        )

        # Load and preprocess datasets
        datasets = [dfm_load_dataset(d) for d in self.dataset_names]
        datasets = [
            preprocess_dataset(d, tokenizer=tokenizer, num_proc=self.data_args.num_proc)
            for d in datasets
        ]
        train_datasets = [d["train"] for d in datasets]
        eval_datasets = [d["val"] for d in datasets]

        # Interleave
        train_datasets = interleave_datasets(
            train_datasets, probabilities=self.interleave_probabilities
        )
        eval_datasets = interleave_datasets(
            eval_datasets, probabilities=self.interleave_probabilities
        )

        # Data collator
        if self.model_type == "autoencoding":
            # Data Collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer, mlm_probability=self.data_args.mlm_probability
            )

        elif self.model_type == "seq-to-seq":
            # TODO
            # Create DataCollatorForT5MLM.
            raise NotImplementedError(
                f"Model type: {self.model_type} has not yet been implemented."
            )
        else:
            raise NotImplementedError(
                f"Model type: {self.model_type} has not yet been implemented."
            )

        # Load model
        model = AutoModelForPreTraining.from_config(HF_config)

        # Training args
        training_args = TrainingArguments(**self.training_args)

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_datasets,
            eval_dataset=eval_datasets,
            data_collator=data_collator,
        )

        # Train
        trainer.train(resume_from_checkpoint=resume_from_checkpoint)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to a yaml config file.")
    args = parser.parse_args()
    main(args)
