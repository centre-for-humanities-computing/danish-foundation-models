from dfm.dataset_validation.rating_interface import ExampleRater

if __name__ == "__main__":
    str_iterable = ["I'm a true string!", "Je suis un string", "jfidlaso gjfidka" * 32]

    rater = ExampleRater(examples=str_iterable, output_path="test.csv")

    rater.rate_examples()
