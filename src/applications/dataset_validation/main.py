from datetime import date

from dfm.dataset_validation.rating_interface import ExampleRater


def text_generator(seed):
    from transformers import AutoTokenizer

    from dfm.data.load_datasets import load_nat

    tokenizer = AutoTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
    datasets = load_nat(seed=seed)["train"]
    texts = (text["text"].replace("\xa0", "\n") for text in iter(datasets))
    for text in texts:
        for newline in text.split("\n"):
            if newline:
                yield newline


if __name__ == "__main__":
    MY_NAME = "kenneth2"
    N_TO_RATE = 100

    gen = text_generator(seed=2)
    texts = [next(gen) for i in range(N_TO_RATE)]
    
    rater = ExampleRater(
        examples=texts,
        output_path=f"{MY_NAME}_{date.today()}.csv"
    )

    rater.rate_examples()
