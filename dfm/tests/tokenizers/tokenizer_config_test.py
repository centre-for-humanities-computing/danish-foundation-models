import pytest
from pathlib import Path
from pydantic import ValidationError
import os
from dfm.tokenizers import TokenizerConfig

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


class TestTokenizerConfig:
    """Unit tests for the TokenizerConfig class"""

    @pytest.fixture(scope="class")
    def config_path(self):
        yield Path("test_config.json")

    def test_tokenizer_config_init(self, valid_config_dict):
        TokenizerConfig(**valid_config_dict)

    def test_invalid_tokenizer_type(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["tokenizer_type"] = 0
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)
        config_dict["tokenizer_type"] = "invalid"
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_vocab_size(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["vocab_size"] = "invalid"
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)
        config_dict["vocab_size"] = -1
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_lower_case(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["lower_case"] = "invalid"
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_sentence_piece(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["sentence_piece"] = "invalid"
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_add_prefix_space(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["add_prefix_space"] = "invalid"
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_byte_level(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["byte_level"] = "invalid"
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_add_sep_and_cls_tokens(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["add_sep_and_cls_tokens"] = "invalid"
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_padding(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["padding"] = "invalid"
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_truncation(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["truncation"] = "invalid"
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_max_length(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["max_length"] = "invalid"
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)
        config_dict["max_length"] = -1
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_nfkc_normalization(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["nfkc_normalization"] = "invalid"
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_pad_token(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["pad_token"] = 0
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_bos_token(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["bos_token"] = 0
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_eos_token(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["eos_token"] = 0
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_unk_token(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["unk_token"] = 0
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_invalid_mask_token(self, valid_config_dict):
        config_dict = valid_config_dict.copy()
        config_dict["mask_token"] = 0
        with pytest.raises(ValidationError):
            TokenizerConfig(**config_dict)

    def test_repr(self, valid_config_dict):
        tokenizer_config = TokenizerConfig(**valid_config_dict)
        repr_string = repr(tokenizer_config)
        assert isinstance(repr_string, str)
        assert repr_string.startswith("TokenizerConfig")

    def test_dict(self, valid_config_dict):
        tokenizer_config = TokenizerConfig(**valid_config_dict)
        config_dct = dict(tokenizer_config)
        assert isinstance(config_dct, dict)
        assert valid_config_dict == config_dct

    def test_save(self, valid_config_dict, config_path):
        tokenizer_config = TokenizerConfig(**valid_config_dict)
        if config_path.exists():
            config_path.unlink()
        tokenizer_config.save(config_path)
        assert config_path.exists()

    def test_load(self, valid_config_dict, config_path):
        config = TokenizerConfig(**valid_config_dict)
        loaded_config = TokenizerConfig.load(config_path)
        assert dict(config) == dict(loaded_config)
        if config_path.exists():
            config_path.unlink()
