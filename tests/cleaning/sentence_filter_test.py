"""Unit tests for the sentence filter."""

import pytest
from src.dfm.cleaning.sentence_filter import SentenceFilter


class TestEndsWithPunctuationOrEmoji:

    @pytest.fixture(scope='class')
    def sentence_filter(self):
        yield SentenceFilter(filter_names=["ends_with_punctuation_or_emoji"])

    @pytest.fixture(scope='class')
    def sentences(self):
        yield [
            "Det her er en sætning, som slutter med et punktum.",
            "Denne her sætning, skrevet af Hr. Mortensen, slutter med en smiley 🎉",
            "Denne her slutter ikke",
            "Her er en, som slutter med en anden smiley :-)",
            "Def{} sdjsjsdx@(£)@!£",
        ]

    @pytest.fixture(scope='class')
    def clean_sentence_indices(self):
        yield [0, 1, 3]

    @pytest.fixture(scope='class')
    def document(self, sentences):
        yield "\n".join(sentences)

    @pytest.fixture(scope='class')
    def cleaned_document(self, sentences, clean_sentence_indices):
        yield "\n".join([sentences[i] for i in clean_sentence_indices])

    def test_sentence_ends_with_punctuation_or_emoji(
            self, sentences, sentence_filter, clean_sentence_indices
        ) -> None:
        """Tests that the sentences are correctly filtered by ending character."""
        filter_outputs = [
            sentence_filter._ends_with_punctuation_or_emoji(sentence)
            for sentence in sentences
        ]
        assert filter_outputs == [
            i in clean_sentence_indices for i in range(len(sentences))
        ]

    def test_filter_corpus(self, sentence_filter, document, cleaned_document) -> None:
        """Tests that the corpus is correctly filtered."""
        filtered_corpus = list(sentence_filter.filter_corpus([document]))
        assert len(filtered_corpus) == 1
        assert filtered_corpus[0] == cleaned_document