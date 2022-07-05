from typing import Dict

from transformers import pipeline


class hate_speech_filter:
    def __init__(self):
        model_name = "DaNLP/da-bert-hatespeech-detection"
        self.pipe = pipeline(
            "sentiment-analysis",  # text classification == sentiment analysis
            model=model_name,
        )

    def __call__(self, examples: Dict[str, list], text_column="text"):
        texts = examples[text_column]
        output = self.pipe(texts, truncation=True)
        examples["offensive_prob"] = [
            t["score"] if t["label"] == "offensive" else 1 - t["score"] for t in output
        ]
        return examples
