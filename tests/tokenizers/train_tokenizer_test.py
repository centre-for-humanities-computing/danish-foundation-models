import pytest
import pandas as pd
from datasets import load_dataset
import os
from dfm.tokenizers import TokenizerConfig, train_tokenizer


# Disable tokenizer parallelization
os.environ["TOKENIZERS_PARALLELISM"] = "false"


@pytest.fixture(scope="module")
def valid_config_dict():
    yield dict(
        tokenizer_type="bpe",
        vocab_size=1000,
        lower_case=False,
        sentence_piece=False,
        add_prefix_space=False,
        byte_level=False,
        add_sep_and_cls_tokens=False,
        padding=False,
        truncation=False,
        max_length=512,
        nfkc_normalization=False,
        pad_token="<pad>",
        bos_token="<bos>",
        eos_token="<eos>",
        unk_token="<unk>",
        mask_token="<mask>",
    )


class TestTrainTokenizer:
    """Unit tests for the tok = train_tokenizer function"""

    @pytest.fixture(scope="class")
    def dataset(self):
        yield load_dataset("DDSC/lcc", split="test")

    @pytest.fixture(scope="class")
    def streamed_dataset(self):
        yield load_dataset("DDSC/lcc", split="test", streaming=True)

    @pytest.fixture(scope="class")
    def train_params(self):
        yield dict(save_tokenizer=False, show_progress=False)

    @pytest.fixture(scope="class")
    def test_docs(self):
        yield ["Dette er en dårlig <mask>.", "Test…"]

    def test_iterable_of_texts(
        self, dataset, valid_config_dict, train_params, test_docs
    ):
        config = TokenizerConfig(**valid_config_dict)
        tok = train_tokenizer(
            corpus=(s["text"] for s in dataset), config=config, **train_params
        )
        tokens = ["Det", "te", "er", "en", "dår", "lig", "<mask>", "."]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_list_of_texts(self, dataset, valid_config_dict, train_params, test_docs):
        config = TokenizerConfig(**valid_config_dict)
        tok = train_tokenizer(
            corpus=[s["text"] for s in dataset], config=config, **train_params
        )
        tokens = ["Det", "te", "er", "en", "dår", "lig", "<mask>", "."]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_series_of_texts(self, dataset, valid_config_dict, train_params, test_docs):
        config = TokenizerConfig(**valid_config_dict)
        series = pd.Series([s["text"] for s in dataset])
        tok = train_tokenizer(corpus=series, config=config, **train_params)
        tokens = ["Det", "te", "er", "en", "dår", "lig", "<mask>", "."]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_streaming(
        self, streamed_dataset, valid_config_dict, train_params, test_docs
    ):
        config = TokenizerConfig(**valid_config_dict)
        tok = train_tokenizer(corpus=streamed_dataset, config=config, **train_params)
        tokens = ["Det", "te", "er", "en", "dår", "lig", "<mask>", "."]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_bpe(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["tokenizer_type"] = "bpe"
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = ["Det", "te", "er", "en", "dår", "lig", "<mask>", "."]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_wordpiece(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["tokenizer_type"] = "wordpiece"
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = ["Det", "##te", "er", "en", "dår", "##lig", "<mask>", "."]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_unigram(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["tokenizer_type"] = "unigram"
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = ["Det", "te", "er", "en", "dårlig", "<mask>", "."]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_lower_case(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["lower_case"] = True
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = ["dette", "er", "en", "dår", "lig", "<mask>", "."]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_sentence_piece(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["sentence_piece"] = True
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = ["Det", "te", "▁er", "▁en", "▁dår", "lig", "▁", "<mask>", "."]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_add_prefix_space(
        self, dataset, valid_config_dict, train_params, test_docs
    ):
        config_dict = valid_config_dict.copy()
        config_dict["add_prefix_space"] = True
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = ["Det", "te", "er", "en", "dår", "lig", "<mask>", "."]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_byte_level(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["byte_level"] = True
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = ["Det", "te", "Ġer", "Ġen", "ĠdÃ¥r", "lig", "Ġ", "<mask>", "."]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_add_special_tokens(
        self, dataset, valid_config_dict, train_params, test_docs
    ):
        config_dict = valid_config_dict.copy()
        config_dict["add_sep_and_cls_tokens"] = True
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = [
            "<bos>",
            "Det",
            "te",
            "er",
            "en",
            "dår",
            "lig",
            "<mask>",
            ".",
            "<eos>",
        ]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_padding(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["padding"] = True
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = ["T", "est", "…", "<pad>", "<pad>", "<pad>", "<pad>", "<pad>"]
        assert tok.encode_batch(test_docs)[1].tokens == tokens

    def test_truncation(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["truncation"] = True
        config_dict["max_length"] = 3
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = ["Det", "te", "er"]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_nfkc_normalization(
        self, dataset, valid_config_dict, train_params, test_docs
    ):
        config_dict = valid_config_dict.copy()
        config_dict["nfkc_normalization"] = True
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = ["T", "est", "..", "."]
        assert tok.encode(test_docs[1]).tokens == tokens

    def test_pad_token(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["padding"] = True
        config_dict["pad_token"] = "[PAD]"
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = ["T", "est", "…", "[PAD]", "[PAD]", "[PAD]", "[PAD]", "[PAD]"]
        assert tok.encode_batch(test_docs)[1].tokens == tokens

    def test_bos_token(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["add_sep_and_cls_tokens"] = True
        config_dict["bos_token"] = "[CLS]"
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = [
            "[CLS]",
            "Det",
            "te",
            "er",
            "en",
            "dår",
            "lig",
            "<mask>",
            ".",
            "<eos>",
        ]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_eos_token(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["add_sep_and_cls_tokens"] = True
        config_dict["eos_token"] = "[SEP]"
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = [
            "<bos>",
            "Det",
            "te",
            "er",
            "en",
            "dår",
            "lig",
            "<mask>",
            ".",
            "[SEP]",
        ]
        assert tok.encode(test_docs[0]).tokens == tokens

    def test_unk_token(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["unk_token"] = "[UNK]"
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        new_test_doc = str(test_docs[0]) + "<>"
        tokens = [
            "Det",
            "te",
            "er",
            "en",
            "dår",
            "lig",
            "<mask>",
            ".",
            "[UNK]",
            "[UNK]",
        ]
        assert tok.encode(new_test_doc).tokens == tokens

    def test_mask_token(self, dataset, valid_config_dict, train_params, test_docs):
        config_dict = valid_config_dict.copy()
        config_dict["mask_token"] = "[MASK]"
        config = TokenizerConfig(**config_dict)
        tok = train_tokenizer(corpus=dataset, config=config, **train_params)
        tokens = [
            "Det",
            "te",
            "er",
            "en",
            "dår",
            "lig",
            "[MASK]",
            ".",
        ]
        new_test_doc = str(test_docs[0]).replace("<mask>", "[MASK]")
        assert tok.encode(new_test_doc).tokens == tokens
