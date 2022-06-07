"""
script for calculating pseudo perplexity in accordance with
https://arxiv.org/pdf/1910.14659.pdf

Note: this script could be optimized more by sampling instead of calculating the full document
"""

from typing import Dict, List
from transformers import (
    AutoModel,
    AutoTokenizer,
    FlaxAutoModelForMaskedLM,
    AutoModelForMaskedLM
)
from scipy.special import expit
import numpy as np

from dfm.data.load_datasets import load_danews, load_dagw_dfm, load_hopetwitter
import torch
def ppl(
    text: str, model: AutoModelForMaskedLM, tokenizer: AutoTokenizer, batch_size=64,
) -> Dict[str, float]:
    inputs = tokenizer(text, return_tensors="np", truncation=True, max_length=512)
    special_tokens = set(tokenizer.all_special_ids)
    special_tokens = np.isin(inputs["input_ids"][0], tokenizer.all_special_ids)
    non_special_tokens = np.logical_not(special_tokens)
    n_non_special_tokens = sum(non_special_tokens)

    batch = np.vstack([inputs["input_ids"]] * n_non_special_tokens)

    # mask out each tokens in text w. a sliding window of 1
    arr = batch[:, non_special_tokens]
    arr[np.identity(n_non_special_tokens, dtype="bool")] = tokenizer.mask_token_id
    batch[:, non_special_tokens] = arr
    attention_mask = np.vstack([inputs["attention_mask"]] * n_non_special_tokens)
    # removed samples without a mask
    contains_mask = (batch == tokenizer.mask_token_id).sum(axis=0) == 1
    batch = batch[:,contains_mask]
    attention_mask = attention_mask[:,contains_mask]

    # recreate input as a masked batch
    inputs_ = {
        "input_ids": batch,
        "attention_mask": attention_mask,
    }

    ppl = 0
    n_samples = inputs_["input_ids"].shape[0]
    for i in range(0, n_samples, batch_size):
        batch_input = {
            "input_ids": inputs_["input_ids"][:, i:i+batch_size],
            "attention_mask": inputs_["attention_mask"][:, i:i+batch_size],
        }
        if hasattr(model, "device"):
            batch_input_ = {
                "input_ids": torch.from_numpy(batch_input["input_ids"]).to(model.device),
                "attention_mask": torch.from_numpy(batch_input["attention_mask"]).to(model.device),
                }
        else:
            batch_input_ = batch_input
        # forward pass through model
        token_logits = model(**batch_input_).logits

        if isinstance(token_logits, torch.Tensor):
            token_logits = token_logits.cpu().detach().numpy()

        # extract logit of gold token
        gold_token = inputs["input_ids"][0][non_special_tokens]
        mask_token_index = np.argwhere(batch_input["input_ids"] == tokenizer.mask_token_id)
        mask_token_logits = token_logits[mask_token_index[:, 0], mask_token_index[:, 1], :]
        gold_token_logits = mask_token_logits[np.arange(mask_token_logits.shape[0]), gold_token[i:i+batch_size]]

        # calculate PPL in accordance with https://arxiv.org/pdf/1910.14659.pdf
        ppl += np.sum(np.log(expit(gold_token_logits)))
    return {"ppl": ppl, "n_tokens": len(gold_token_logits)}

def pppl(
    texts: List[str], model: AutoModelForMaskedLM, tokenizer: AutoTokenizer
) -> float:
    texts_ = [t for t in texts if t]
    if not texts:
        raise ValueError("list of texts is empty or contain only empty strings.")
    ppl_values_ = [ppl(text, model=model, tokenizer=tokenizer) for text in texts_]
    ppl_values, token_lengths = zip(
        *[(ppl_["ppl"], ppl_["n_tokens"]) for ppl_ in ppl_values_]
    )
    return np.exp(-np.sum(ppl_values) / np.sum(token_lengths))

mdls = [
#    "KennethEnevoldsen/dfm-bert-base",  # 1.4349901347773766
    "vesteinn/ScandiBERT",  # 1.0686843661248284
]

datasets = {}
dagw = load_dagw_dfm()["test"]
for sample in iter(dagw):
    if sample["source"] not in datasets:
        datasets[sample["source"]] = []
    datasets[sample["source"]].append(sample["text"])
    
danews = load_danews()["test"]
datasets["danews"] = [t["text"] for t in danews]
hopetwitter = load_hopetwitter()["test"]
datasets["hopetwitter"] = [t["text"] for t in hopetwitter]



for mdl in mdls:
    if mdl == "KennethEnevoldsen/dfm-bert-base":
        model = FlaxAutoModelForMaskedLM.from_pretrained(mdl)
    else:
        model = AutoModelForMaskedLM.from_pretrained(mdl)
        model.cuda()
    tokenizer = AutoTokenizer.from_pretrained(mdl)

    print(f"Model:{mdl}")
    for name, texts in datasets.items():
        pppl_ = pppl(texts, model, tokenizer)
        print(f"\t{name}, {pppl_}")
