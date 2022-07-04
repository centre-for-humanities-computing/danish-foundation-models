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
        """Tests that the sentences are correctly."""
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


class TestHasFewTitleCasedWords:

    @pytest.fixture(scope='class')
    def sentence_filter(self):
        yield SentenceFilter(filter_names=["has_few_title_cased_words"])

    @pytest.fixture(scope='class')
    def sentences(self):
        yield [
            "Det her er en sætning, som kun har ét ord, der starter med stort bogstav.",
            "Om os Indkøbskurv Shop Find butik Kontakt",
            "Han hedder John Hansen, blev der sagt.",
        ]

    @pytest.fixture(scope='class')
    def clean_sentence_indices(self):
        yield [0, 2]

    @pytest.fixture(scope='class')
    def document(self, sentences):
        yield "\n".join(sentences)

    @pytest.fixture(scope='class')
    def cleaned_document(self, sentences, clean_sentence_indices):
        yield "\n".join([sentences[i] for i in clean_sentence_indices])

    def test_has_few_title_cased_words(
            self, sentences, sentence_filter, clean_sentence_indices
        ) -> None:
        """Tests that the sentences are correctly filtered."""
        filter_outputs = [
            sentence_filter._has_few_title_cased_words(sentence)
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


class TestHasEnoughWords:

    @pytest.fixture(scope='class')
    def sentence_filter(self):
        yield SentenceFilter(filter_names=["has_enough_words"])

    @pytest.fixture(scope='class')
    def sentences(self):
        yield [
            "Det her er en sætning, som har nok ord.",
            "Få ord!",
            "Hej",
            "",
            "Denne her er god nok",
        ]

    @pytest.fixture(scope='class')
    def clean_sentence_indices(self):
        yield [0, 4]

    @pytest.fixture(scope='class')
    def document(self, sentences):
        yield "\n".join(sentences)

    @pytest.fixture(scope='class')
    def cleaned_document(self, sentences, clean_sentence_indices):
        yield "\n".join([sentences[i] for i in clean_sentence_indices])

    def test_has_enough_words(
            self, sentences, sentence_filter, clean_sentence_indices
        ) -> None:
        """Tests that the sentences are correctly filtered."""
        filter_outputs = [
            sentence_filter._has_enough_words(sentence)
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


class TestFewCurlyBrackets:

    @pytest.fixture(scope='class')
    def sentence_filter(self):
        yield SentenceFilter(filter_names=["has_few_curly_brackets"])

    @pytest.fixture(scope='class')
    def sentences(self):
        yield [
            "Det her er bare en helt normal sætning.",
            "En sætning må gerne have nogle krølleparanteser :-}",
            "Men den må ikke have {nogle stykker}.",
            "if (x > 0) { console.log(x); } else { console.log('error!'); }",
        ]

    @pytest.fixture(scope='class')
    def clean_sentence_indices(self):
        yield [0, 1]

    @pytest.fixture(scope='class')
    def document(self, sentences):
        yield "\n".join(sentences)

    @pytest.fixture(scope='class')
    def cleaned_document(self, sentences, clean_sentence_indices):
        yield "\n".join([sentences[i] for i in clean_sentence_indices])

    def test_has_few_curly_brackets(
            self, sentences, sentence_filter, clean_sentence_indices
        ) -> None:
        """Tests that the sentences are correctly filtered."""
        filter_outputs = [
            sentence_filter._has_few_curly_brackets(sentence)
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
