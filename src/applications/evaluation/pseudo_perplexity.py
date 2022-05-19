"""
script for calculating pseudo perplexity in accordance with
https://arxiv.org/pdf/1910.14659.pdf
"""

from typing import Dict, List
from transformers import (
    AutoModel,
    AutoTokenizer,
    FlaxAutoModelForMaskedLM,
    AutoModelForMaskedLM,
)
from scipy.special import expit
import numpy as np

model = FlaxAutoModelForMaskedLM.from_pretrained("KennethEnevoldsen/dfm-bert-base")
tokenizer = AutoTokenizer.from_pretrained("KennethEnevoldsen/dfm-bert-base")

# model = AutoModel.from_pretrained("KennethEnevoldsen/dfm-bert-base", from_flax=True)
# pytorch_total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
# 110617344

# pytorch_total_params = sum(p.numel() for p in model.parameters())
# 110617344


def ppl(
    text: str, model: AutoModelForMaskedLM, tokenizer: AutoTokenizer
) -> Dict[str, float]:
    inputs = tokenizer(text, return_tensors="np")
    special_tokens = set(tokenizer.all_special_ids)
    special_tokens = np.isin(inputs["input_ids"][0], tokenizer.all_special_ids)
    non_special_tokens = np.logical_not(special_tokens)
    n_non_special_tokens = sum(non_special_tokens)

    batch = np.vstack([inputs["input_ids"]] * n_non_special_tokens)

    # mask out each tokens in text w. a sliding window of 1
    arr = batch[:, non_special_tokens]
    arr[np.identity(n_non_special_tokens, dtype="bool")] = tokenizer.mask_token_id
    batch[:, non_special_tokens] = arr

    # recreate input as a masked batch
    inputs_ = {
        "input_ids": batch,
        "token_type_ids": np.vstack([inputs["token_type_ids"]] * n_non_special_tokens),
        "attention_mask": np.vstack([inputs["attention_mask"]] * n_non_special_tokens),
    }

    # forward pass through model
    token_logits = model(**inputs_).logits
    # extract logit of gold token
    gold_token = inputs["input_ids"][0][non_special_tokens]
    mask_token_index = np.argwhere(inputs_["input_ids"] == tokenizer.mask_token_id)
    mask_token_logits = token_logits[mask_token_index[:, 0], mask_token_index[:, 1], :]
    gold_token_logits = mask_token_logits[np.arange(n_non_special_tokens), gold_token]

    # calculate PPL in accordance with https://arxiv.org/pdf/1910.14659.pdf
    pll = np.sum(np.log(expit(gold_token_logits)))
    return {"ppl": pll, "n_tokens": len(gold_token_logits)}


text = "Jeg er så glad for min cykel."
ppl(text, model, tokenizer)


def pppl(
    texts: List[str], model: AutoModelForMaskedLM, tokenizer: AutoTokenizer
) -> float:
    ppl_values_ = [ppl(text, model=model, tokenizer=tokenizer) for text in texts]
    ppl_values, token_lengths = zip(
        *[(ppl_["ppl"], ppl_["n_tokens"]) for ppl_ in ppl_values_]
    )
    return np.exp(-np.sum(ppl_values) / np.sum(token_lengths))


texts = [
    "Jeg er så glad for min cykel.",
    "Fuck hvor har vejret været godt de her dage!",
]
pppl(texts, model, tokenizer)


text = "Jeg er så glad for min cykel."
print(ppl(text, model, tokenizer))
text = "Hej med dig arne. Går det godt?"
print(ppl(text, model, tokenizer))
text = "bib bobity bob bob ding ding!"
print(ppl(text, model, tokenizer))
text = "bib bobity bob bob ding ding! "*2
print(ppl(text, model, tokenizer))
text = "bib bobity bob bob ding ding! "*3
print(ppl(text, model, tokenizer))