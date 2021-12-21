"""Training script for training language models with sweeps
Inspiration: https://colab.research.google.com/github/wandb/examples/blob/master/colabs/pytorch/Organizing_Hyperparameter_Sweeps_in_PyTorch_with_W%26B.ipynb#scrollTo=r4VjKui20N3j

train.py --arg1 arg2 ...
"""

from utils import read_json
import wandb
from transformers import AutoConfig, AutoModelForPreTraining, Trainer, TrainingArguments
from pathlib import Path
from typing import List

from dfm.data.load import load_dataset
from dfm.data.preprocess import preprocess_dataset


def train(
    model_path: str, model_config_path: str = None, sweeps_config_path: str = None
):
    """Training function with sweeps from Weights & Biases implemented for hyperparameter optimization.

    Args:
        model_path (str): Path to a model
        model_config_path (str, optional): Path to a model config. Defaults to None.
        sweeps_config_path (str, optional): Path to a sweeps config. Defaults to None.
    """

    # Configuration
    if model_config_path is None:
        model_config_path = Path() / model_path / "config.json"
    if sweeps_config_path is None:
        sweeps_config_path = Path() / model_path / "sweep_config.json"
    model_config = read_json(model_config_path)
    sweeps_config = read_json(sweeps_config_path)

    with wandb.init(config=sweeps_config):

        config = wandb.config

        HF_config = AutoConfig.from_pretrained(model_config)

        dataset = load_dataset(config.datasets)
        dataset = preprocess_dataset(dataset)

        mdl = AutoModelForPreTraining(config.model_name, HF_config)

        training_args = TrainingArguments(
            output_dir=f"{model_checkpoint}-dfm",
            evaluation_strategy="epoch",
            learning_rate=config.learning_rate,
            weight_decay=config.weight_decay,
            push_to_hub=True,
        )

        trainer = Trainer(
            model=mdl,
            args=training_args,
            train_dataset=dataset["train"],
            eval_dataset=dataset["validation"],
        )

        trainer.train()
        trainer.push_to_hub()
