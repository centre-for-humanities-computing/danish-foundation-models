import json

from transformers import PreTrainedTokenizerFast

tokenizer_file = "/data-big-projects/danish-foundation-models/tokenizers/unigram_100000_docs_32000_vocab/tokenizer.json"
tokenizer = PreTrainedTokenizerFast(
    tokenizer_file=tokenizer_file,
)

config = "/data-big-projects/danish-foundation-models/tokenizers/unigram_100000_docs_32000_vocab/config.json"
with open(config, "r") as f:
    config = json.load(f)

tokenizer

tokenizer.save_pretrained(
    "/data-big-projects/danish-foundation-models/tokenizers/unigram_100000_docs_32000_vocab/test"
)

from tokenizers import Tokenizer

tokenizer = Tokenizer.from_file(tokenizer_file)

fast_tokenizer = PreTrainedTokenizerFast(tokenizer_object=tokenizer)
fast_tokenizer.mask_token = config["mask_token"]
fast_tokenizer.unk_token = config["unk_token"]
fast_tokenizer.sep_token = config["sep_token"]
fast_tokenizer.bos_token = config["bos_token"]
fast_tokenizer.eos_token = config["eos_token"]
