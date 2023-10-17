"""Script for rating text quality of mC4."""
from datetime import date

from datasets import load_dataset
from dfm.dataset_validation.rating_interface import ExampleRater


def main(name: str, session: str, seed: int, n_to_rate: int, max_len: int):
    """
    Main function.

    Args:
        name (str): Name of the dataset.
        session (str): Session identifier.
        seed (int): Seed for the random number generator.
        n_to_rate (int): Number of texts to rate.
        max_len (int): Maximum length of text to clean.
    """

    mc4 = load_dataset("mc4", "da", streaming=True, split="train")
    mc4 = iter(mc4.shuffle(seed=seed))
    # train
    texts = [next(mc4)["text"] for i in range(n_to_rate)]

    text_splits = [
        text[i : i + max_len] for text in texts for i in range(0, len(text), max_len)
    ]

    rater = ExampleRater(
        examples=text_splits,
        output_path=f"data/tagging/mc4/{name}_{session}_{date.today()}.csv",
    )

    rater.rate_examples()


if __name__ == "__main__":
    MY_NAME = "kenneth"
    SESSION = "session_1"
    N_TO_RATE = 100
    seed = 2  # seeds already used: 2,
    max_len = 1000

    main(MY_NAME, SESSION, seed, N_TO_RATE, max_len)
