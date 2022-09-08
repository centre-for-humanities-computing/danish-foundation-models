from datetime import date

from datasets import load_dataset

from dfm.dataset_validation.rating_interface import ExampleRater

if __name__ == "__main__":
    MY_NAME = "kenneth"
    SESSION = "session_1"
    N_TO_RATE = 100
    seed = 2  # seeds already used: 2,
    max_len = 1000

    mc4 = load_dataset("mc4", "da", streaming=True, split="train")
    mc4 = iter(mc4.shuffle(seed=seed))
    # train
    texts = [next(mc4)["text"] for i in range(N_TO_RATE)]

    text_splits = [
        text[i : i + max_len] for text in texts for i in range(0, len(text), max_len)
    ]

    rater = ExampleRater(
        examples=text_splits,
        output_path=f"data/tagging/mc4/{MY_NAME}_{SESSION}_{date.today()}.csv",
    )

    rater.rate_examples()
    # is highly repititous: 1
