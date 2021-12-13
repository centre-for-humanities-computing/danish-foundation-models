"""Training script for training language models with sweeps
Inspiration: https://colab.research.google.com/github/wandb/examples/blob/master/colabs/pytorch/Organizing_Hyperparameter_Sweeps_in_PyTorch_with_W%26B.ipynb#scrollTo=r4VjKui20N3j

train.py --arg1 arg2 ...
"""

from utils import read_json
import wandb
from transformers import AutoConfig, AutoModelForPreTraining, Trainer, TrainingArguments
from pathlib import Path
from typing import List

SWEEP_CONFIG_PATH = Path.cwd() / "sweep_config.json"
SWEEPS = read_json(SWEEP_CONFIG_PATH)

HF_CONFIG_PATH = Path.cwd() / "model_config.json"
HF_CONFIG = read_json(HF_CONFIG_PATH)


def train(config=None):

    with wandb.init(config=config):

        config = wandb.config

        HF_config = AutoConfig.from_pretrained(HF_CONFIG)

        dataset = load_dataset(config.datasets)

        mdl = AutoModelForPreTraining(config.model_name, HF_config)

        training_args = TrainingArguments(
            f"{model_checkpoint}-wikitext2",
            evaluation_strategy="epoch",
            learning_rate=2e-5,
            weight_decay=0.01,
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


def load_dataset(datasets: List[str]):
    # parse dataset names
    # load required dataset
    # apply relevant filters
    # train test validation split
    # (dont to shuffling, tokenization etc. here)
    pass
