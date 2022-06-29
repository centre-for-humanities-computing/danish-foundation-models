from doctest import Example

from dfm.dataset_validation.rating_interface import ExampleRater


def text_generator(seed=2):
    from dfm.data.load_datasets import load_nat
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Maltehb/danish-bert-botxo")
    datasets = load_nat(seed=seed)["train"]
    texts = (text["text"].replace("\xa0", "\n") for text in iter(datasets))
    for t in texts:
        input_ids = tokenizer(t)["input_ids"]
        i = 0
        len_input_ids = len(input_ids)
        while True:
            yield tokenizer.decode(input_ids[i:i+512])
            i += 512
            if i > len_input_ids:
                break

if __name__ == "__main__":

    gen = text_generator(seed=2)
    texts = [next(gen) for i in range(100)]
    rater = ExampleRater(examples=texts, output_path="test.csv")

    rater.rate_examples()
