"""Unit tests for the sentence filter."""

import pytest
from src.dfm.cleaning.sentence_filter import SentenceFilter


class TestSentenceFilter:

    @pytest.fixture(scope='class')
    def sentence_filter(self):
        yield SentenceFilter()

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
    def document(self, sentences):
        yield sentences.join("\n")

    def test_sentence_ends_with_punctuation_or_emoji(
            self, sentences, sentence_filter
        ) -> None:
        """Tests that the sentences are correctly filtered by ending character."""
        filter_outputs = [
            sentence_filter._ends_with_punctuation_or_emoji(sentence)
            for sentence in sentences
        ]
        assert filter_outputs == [True, True, False, True, False]

    def test_filter_corpus(self, sentence_filter, document, sentences) -> None:
        """Tests that the corpus is correctly filtered."""
        filtered_corpus = list(sentence_filter.filter_corpus([document]))
        assert len(filtered_corpus) == 1
        assert filtered_corpus[0] == "\n".join(sentences[i] for i in [0, 1, 3])
