from dfm.dataset_validation.rating_interface import ExampleRater
from datetime import date


def text_generator(seed=2):
    from transformers import AutoTokenizer

    from dfm.data.load_datasets import load_nat

    tokenizer = AutoTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
    datasets = load_nat(seed=seed)["train"]
    texts = (text["text"].replace("\xa0", "\n") for text in iter(datasets))
    for t in texts:
        input_ids = tokenizer(t)["input_ids"]
        i = 0
        len_input_ids = len(input_ids)
        while True:
            yield tokenizer.decode(input_ids[i : i + 512])
            i += 512
            if i > len_input_ids:
                break


if __name__ == "__main__":
    MY_NAME = "martin"
    N_TO_RATE = 100

    gen = text_generator(seed=2)
    texts = [next(gen) for i in range(N_TO_RATE)]

    rater = ExampleRater(examples=texts, output_path=f"{MY_NAME}_{date.today()}.csv", resume_from_index=50)

    rater.rate_examples()
