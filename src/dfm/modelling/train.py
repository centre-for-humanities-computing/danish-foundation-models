"""Training script for training masked language models with sweeps
Inspiration: https://github.com/huggingface/transformers/blob/master/examples/pytorch/language-modeling/run_mlm.py

CMD: train.py --path_to_config_file
"""

from dataclasses import dataclass, field
import json
from typing import List, Optional

import wandb
from transformers import (
    AutoConfig,
    AutoModelForMaskedLM,
    AutoModelForPreTraining,
    Trainer,
    TrainingArguments,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
)
from datasets import interleave_datasets

from dfm.data.load import dfm_load_dataset
from dfm.data.preprocess import preprocess_dataset
from dfm.utils import read_json
from dfm.modelling.model_types import MODEL_TYPES


def main():
    d = DataArguments.from_json("tests/test_configs/pretrain_config.json")
    trainer = DFMTrainer(
        pretraining_config_path="tests/test_configs/pretrain_config.json",
    )
    trainer.train()


# TODO:
# create configs for models (training + model)
# create collator for T5
# remove variables and make it more IaC
@dataclass
class DataArguments(object):
    dataset_names: List[str]
    interleave: bool
    interleave_probabilities: List[float]

    @classmethod
    def from_json(cls, config_path: str):
        file = json.load(open(config_path))
        keys = cls.__dataclass_fields__.keys()
        json_data = file["data_arguments"]
        normal_json_data = {key: json_data[key] for key in json_data if key in keys}
        anormal_json_data = {
            key: json_data[key] for key in json_data if key not in keys
        }
        tmp = cls(**normal_json_data)
        for anormal_key in anormal_json_data:
            setattr(tmp, anormal_key, anormal_json_data[anormal_key])
        return tmp


@dataclass
class ModelArguments(object):
    model_type: str
    model_name: str

    @classmethod
    def from_json(cls, config_path: str):
        file = json.load(open(config_path))
        keys = cls.__dataclass_fields__.keys()
        json_data = file["model_arguments"]
        normal_json_data = {key: json_data[key] for key in json_data if key in keys}
        anormal_json_data = {
            key: json_data[key] for key in json_data if key not in keys
        }
        tmp = cls(**normal_json_data)
        for anormal_key in anormal_json_data:
            setattr(tmp, anormal_key, anormal_json_data[anormal_key])
        return tmp


class DFMTrainer:
    """class for training a Danish Foundation Model."""

    def __init__(
        self,
        pretraining_config_path: str,
        model_type: Optional[str] = None,
        dataset_names: Optional[List[str]] = None,
        model_name: Optional[str] = None,
        interleave_probabilities: Optional[List[float]] = [0.5, 0.5],
        mlm_probability: int = 0.15,
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
        self.training_args = read_json(self.pretraining_config_path)[
            "training_arguments"
        ]
        self.data_args = DataArguments.from_json(self.pretraining_config_path)
        self.model_args = ModelArguments.from_json(self.pretraining_config_path)

        self.dataset_names = self.data_args.dataset_names
        self.interleave = self.data_args.interleave
        self.interleave_probabilities = self.data_args.interleave_probabilities

        self.model_type = self.model_args.model_type
        self.model_name = self.model_args.model_name

        if self.model_type not in MODEL_TYPES:
            raise ValueError(f"Invalid model type. Choose one from: {MODEL_TYPES}")

    def train(
        self,
    ):

        # wandb.login()

        HF_config = AutoConfig.from_pretrained(self.model_name)
        tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, return_special_tokens_mask=True
        )

        # Load and preprocess datasets
        datasets = [dfm_load_dataset(d) for d in self.dataset_names]
        # might want to set num_proc to more than 4 in `preprocess_dataset``
        datasets = [preprocess_dataset(d, tokenizer=tokenizer) for d in datasets]
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
        if self.model_type == "autoenconding":
            # Data Collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer, mlm_probability=self.mlm_probability
            )

        elif self.model_type == "seq-to-seq":
            # data_collator = DataCollatorForLanguageModeling(
            #     tokenizer=tokenizer, mlm_probability=0.15
            # )
            # model = AutoModelForMaskedLM.from_config(HF_config)
            raise ValueError(
                f"Sorry. Model type: {self.model_type} has not yet been implemented."
            )

        # Load model
        model = AutoModelForPreTraining.from_config(HF_config)

        # Training args
        training_args = TrainingArguments(
            f"models/{model.name_or_path}", **pretrain_config
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_datasets,
            eval_dataset=eval_datasets,
            data_collator=data_collator,
        )

        # Train
        trainer.train()
        trainer.push_to_hub()


if __name__ == "__main__":
    main()
