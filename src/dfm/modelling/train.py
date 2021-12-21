"""Training script for training language models with sweeps
Inspiration: https://colab.research.google.com/github/wandb/examples/blob/master/colabs/pytorch/Organizing_Hyperparameter_Sweeps_in_PyTorch_with_W%26B.ipynb#scrollTo=r4VjKui20N3j

https://colab.research.google.com/github/huggingface/notebooks/blob/master/examples/language_modeling_from_scratch.ipynb


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
    model_name: str,
    model_config_path: str,
    pretraining_config_path: str,
    datasets: List[str],
):
    """
    # TODO:
        # testes med reddit
        # create configs for models (training + model)
        # test 3 modeller t5, deberta v2, gpt

    Training function with Weights & Biases logging.

    Args:
        model_name (str): Path to a model.
        model_config_path (str): Path to a model config.
        pretraining_config_path (str): Path to a pretraining config.
        datasets (list(str)): List of dataset names from the Hugging Face hub.
    """

    wandb.login()

    # Configuration
    if model_config_path is None:
        model_config_path = Path() / model_name / "config.json"
    model_config = read_json(model_config_path)
    pretrain_config = read_json(pretraining_config_path)

    HF_config = AutoConfig.from_pretrained(model_config)

    # Load and preprocess datasets
    dataset = load_dataset(datasets)
    dataset = preprocess_dataset(dataset)

    # Load model
    mdl = AutoModelForPreTraining(model_name, HF_config)

    training_args = TrainingArguments(
        output_dir=f"{model_name}-dfm",
        evaluation_strategy="epoch",
        learning_rate=pretrain_config.learning_rate,
        weight_decay=pretrain_config.weight_decay,
        push_to_hub=True,
        report_to="wandb",
    )

    trainer = Trainer(
        model=mdl,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
    )

    # Train
    trainer.train()
    trainer.push_to_hub()
