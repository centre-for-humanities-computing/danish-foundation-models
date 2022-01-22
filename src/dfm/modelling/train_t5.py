"""Training script for training masked language models with sweeps
Inspiration: https://colab.research.google.com/github/wandb/examples/blob/master/colabs/pytorch/Organizing_Hyperparameter_Sweeps_in_PyTorch_with_W%26B.ipynb#scrollTo=r4VjKui20N3j

https://colab.research.google.com/github/huggingface/notebooks/blob/master/examples/language_modeling_from_scratch.ipynb


train.py --arg1 arg2 ...
"""

##### NOT CONVERTED TO SEQ2SEQ MODELLING YET - JUST A COPY OF MLM


from dfm.utils.utils import read_json
import wandb
from transformers import (
    AutoConfig,
    T5ForConditionalGeneration,
    T5TokenizerFast,
    Trainer,
    TrainingArguments,
    T5Tokenizer,
    DataCollatorForLanguageModeling,
)
from pathlib import Path
from typing import List, Optional
from datasets import interleave_datasets


from dfm.data.load import dfm_load_dataset
from dfm.data.preprocess import preprocess_dataset


def main():
    train(
        model_name="t5-small",
        pretraining_config_path="tests/test_configs/pretrain_config.json",
        dataset_names=["DDSC/reddit-da", "DDSC/angry-tweets"],
        interleave_probabilities=[0.5, 0.5],
    )


def train(
    model_name: str,
    pretraining_config_path: str,
    dataset_names: List[str],
    interleave_probabilities: Optional[List[float]],
):
    """
    # TODO:
        # testes med reddit
        # create configs for models (training + model)
        # test 3 modeller t5, deberta v2, gpt

    Training function with Weights & Biases logging.

    Args:
        model_name (str): Path to a model.
        pretraining_config_path (str): Path to a pretraining config.
        datasets (list(str)): List of dataset names from the Hugging Face hub.
        interleave_probabilities (List[float]): how to weight datasets in interleave
    """

    wandb.login()

    # Configuration
    pretrain_config = read_json(pretraining_config_path)

    HF_config = AutoConfig.from_pretrained(model_name)
    tokenizer = T5TokenizerFast.from_pretrained(model_name)

    # Load and preprocess datasets
    datasets = [dfm_load_dataset(d) for d in dataset_names]
    # might want to set num_proc to more than 4 in `preprocess_dataset``
    datasets = [preprocess_dataset(d, tokenizer=tokenizer) for d in datasets]
    train_datasets = [d["train"] for d in datasets]
    eval_datasets = [d["validation"] for d in datasets]
    # Interleave
    train_datasets = interleave_datasets(
        train_datasets, probabilities=interleave_probabilities
    )
    eval_datasets = interleave_datasets(
        eval_datasets, probabilities=interleave_probabilities
    )
    # Data Collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm_probability=0.15
    )

    # Load model
    mdl = T5ForConditionalGeneration(model_name, HF_config)

    training_args = TrainingArguments(**pretrain_config)

    trainer = Trainer(
        model=mdl,
        args=training_args,
        train_dataset=datasets["train"],
        eval_dataset=datasets["validation"],
        data_collator=data_collator,
    )

    # Train
    trainer.train()
    trainer.push_to_hub()


if __name__ == "__main__":
    main()
