"""Training script for training masked language models with sweeps

Authors:
    Lasse Hansen
    Malte Højmark-Bertelsen

```bash 
PYTHONPATH="." python dfm/train.py --path_to_config_file
```
"""

from dataclasses import dataclass, field
from typing import List, Optional

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
from dfm.modelling.preprocess import preprocess_dataset
from dfm.modelling.utils import read_yaml
from dfm.modelling.model_types import MODEL_TYPES


def main():
    d = DataArguments.from_yaml("tests/test_configs/pretrain_config.yaml")
    trainer = DFMTrainer(
        pretraining_config_path="tests/test_configs/pretrain_config.yaml",
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
    num_proc: int

    @classmethod
    def from_yaml(cls, config_path: str):
        file = read_yaml(config_path)
        keys = cls.__dataclass_fields__.keys()
        yaml_data = file["data_arguments"]
        normal_yaml_data = {key: yaml_data[key] for key in yaml_data if key in keys}
        anormal_yaml_data = {
            key: yaml_data[key] for key in yaml_data if key not in keys
        }
        tmp = cls(**normal_yaml_data)
        for anormal_key in anormal_yaml_data:
            setattr(tmp, anormal_key, anormal_yaml_data[anormal_key])
        return tmp


@dataclass
class ModelArguments(object):
    model_type: str
    model_name: str

    @classmethod
    def from_yaml(cls, config_path: str):
        file = read_yaml(config_path)
        keys = cls.__dataclass_fields__.keys()
        yaml_data = file["model_arguments"]
        normal_yaml_data = {key: yaml_data[key] for key in yaml_data if key in keys}
        anormal_yaml_data = {
            key: yaml_data[key] for key in yaml_data if key not in keys
        }
        tmp = cls(**normal_yaml_data)
        for anormal_key in anormal_yaml_data:
            setattr(tmp, anormal_key, anormal_yaml_data[anormal_key])
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

        self.mlm_probability = mlm_probability

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
        # TODO
        # Make flag for num_proc
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
            f"models/{model.name_or_path}", **self.training_args
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


if __name__ == "__main__":
    main()
