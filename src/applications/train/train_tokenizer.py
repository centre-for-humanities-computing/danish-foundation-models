"""
Trains the tokenizer on the DFM corpus
"""
from wasabi import msg
from datasets import interleave_datasets

from dfm.data import load_dfm_dataset
from dfm.dfm_tokenizers import train_tokenizer, TokenizerConfig
from dfm.data.load_datasets import load_danews, load_dagw_dfm, load_hopetwitter, load_nat

columns_to_keep = ["text", "source"]
danews = load_danews(columns_to_keep=columns_to_keep)["train"]
dagw_dfm = load_dagw_dfm(columns_to_keep=columns_to_keep)["train"]
hopetwitter = load_hopetwitter(columns_to_keep = columns_to_keep)["train"]
nat = load_nat(columns_to_keep=columns_to_keep)["train"]
dataset = interleave_datasets([danews, dagw_dfm, hopetwitter, nat], probabilities=[0.10, 0.20, 0.20, 0.50])

msg.info("Started unigram training tokenizer")
t_config = TokenizerConfig(
    tokenizer_type = "unigram",
    vocab_size = 55000,
    lower_case = False,
    sentence_piece = True,
    add_prefix_space = True,
    byte_level = False)
tokenizer = train_tokenizer(corpus = dataset.take(500_000), config=t_config, save_tokenizer=True, output_dir="ucloud-setup/dfm_tokenizer/unigram_500000")
msg.good("Finished unigram training tokenizer")

msg.info("Started bpe training tokenizer")
t_config = TokenizerConfig(
    tokenizer_type = "bpe",
    vocab_size = 55000,
    lower_case = False,
    sentence_piece = False,
    add_prefix_space = False,
    byte_level = False)
tokenizer = train_tokenizer(corpus = dataset.take(100_000), config=t_config, save_tokenizer=True, output_dir="ucloud-setup/dfm_tokenizer/bpe")
msg.good("Finished bpe training tokenizer")

msg.info("Started wordpiece training tokenizer")
t_config = TokenizerConfig(
    tokenizer_type = "wordpiece",
    vocab_size = 55000,
    lower_case = False,
    sentence_piece = False,
    add_prefix_space = False,
    byte_level = False)
tokenizer = train_tokenizer(corpus = dataset.take(100_000), config=t_config, save_tokenizer=True, output_dir="ucloud-setup/dfm_tokenizer/wordpiece")
msg.good("Finished wordpiece training tokenizer")
# load tokenizer
# from tokenizers import Tokenizer
# tokenizer = Tokenizer.from_file("/work/ucloud-setup/dfm_tokenizer/tokenizer.json")
# texts = [t["text"] for t in dataset.take(100_000)]
# t = tokenizer.encode_batch(texts, add_special_tokens=False)
# sum([len([id for id in i.ids if id]) for i in t])/100_000
# 249.8751*100_000 # 24 987 510
# 249.8751*1_000_000

