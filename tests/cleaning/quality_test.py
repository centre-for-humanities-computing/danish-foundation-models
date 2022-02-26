"""Tests for the quality filter"""

from dfm.cleaning import QualityFilter
import pytest


class TestQualityFilter:
    """Unit tests for the QualityFilter class"""

    @pytest.fixture(scope="class")
    def texts(self):
        texts = [
            "jeg er glad",
            "56789okd23456789098765sds",
            "jeg er glad...",
            "jeg er glad…",
            "67 54 13 B7",
            "#yolo # test ##",
        ]

        texts.append(
            """
        Helt normal tekst:
        Første vindstød af stærk storm - andre steder i landet ramt
        Frederikshavn blev det første sted, der mærkede vindstød af stormstyrke,
        og nu er det også det første sted, der har mærket vindstød af stærk storm. Hvis det er noget at prale af.

        Der er nemlig målt vindstød på 29,3 meter i sekundet. Det er stærk storm,
        når det er over 28,5 meter i sekundet.

        Andre dele af landet har nu også mærket de første vindstød af stormstyrke.

        Odense Lufthavn har haft 24,5 meter i sekundet, mens Grønlandshavnen i Aalborg har ramt 24,7
        meter i sekundet. Det er mest centrale sted i landet, hvor der indtil videre er målet stormstyrke.
        """
        )

        texts.append(
            """
        [summary]

        - test 1
        - test 1
            - test 2
            - test 3
                - test 1
        """
        )

        texts.append(
            """
        [summary]

        * test 1
            * test 2
            * test 3
        * test 1
            * test 2
                * test 3
        """
        )
        texts.append(
            """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit,
        sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        """
        )

        return texts

    @pytest.fixture(scope="class")
    def qfilter(self):
        return QualityFilter()

    def test_stop_word(self, texts, qfilter):
        stop_words = set(
            [
                "er",
                "jeg",
                "det",
                "du",
                "ikke",
                "at",
                "en",
                "og",
                "har",
                "vi",
                "til",
                "på",
                "hvad",
                "mig",
                "med",
                "de",
                "for",
                "den",
                "så",
                "der",
                "dig",
                "han",
                "kan",
                "af",
            ]
        )
        assert (
            qfilter.stop_word(qfilter.nlp(texts[0]), n=2, stop_words=stop_words) is True
        )
        assert (
            qfilter.stop_word(qfilter.nlp(texts[1]), n=1, stop_words=stop_words)
            is False
        )

    def test_line_bullets_or_ellipsis(self, texts, qfilter):
        # bullet
        assert (
            qfilter.line_bullets_or_ellipsis(
                qfilter.nlp(texts[1]), max_p_bullets=0.5, max_p_ellipsis=1
            )
            is True
        )
        assert (
            qfilter.line_bullets_or_ellipsis(
                qfilter.nlp(texts[8]), max_p_bullets=0.5, max_p_ellipsis=1
            )
            is False
        )
        assert (
            qfilter.line_bullets_or_ellipsis(
                qfilter.nlp(texts[7]), max_p_bullets=0.5, max_p_ellipsis=1
            )
            is False
        )

        # ellipsis
        assert (
            qfilter.line_bullets_or_ellipsis(
                qfilter.nlp(texts[8]), max_p_bullets=1.0, max_p_ellipsis=0.5
            )
            is True
        )
        assert (
            qfilter.line_bullets_or_ellipsis(
                qfilter.nlp(texts[2]), max_p_bullets=1.0, max_p_ellipsis=0.5
            )
            is False
        )
        assert (
            qfilter.line_bullets_or_ellipsis(
                qfilter.nlp(texts[3]), max_p_bullets=1.0, max_p_ellipsis=0.5
            )
            is False
        )

    def test_alpha(self, texts, qfilter):
        assert qfilter.alpha(qfilter.nlp(texts[4]), ratio=0.8) is False
        assert qfilter.alpha(qfilter.nlp(texts[0]), ratio=0.8) is True

    def test_mean_word_length(self, texts, qfilter):
        assert (
            qfilter.mean_word_length(qfilter.nlp(texts[1]), mean_word_length=(3, 10))
            is False
        )
        assert (
            qfilter.mean_word_length(qfilter.nlp(texts[0]), mean_word_length=(3, 10))
            is True
        )

    def test_doc_length(self, texts, qfilter):
        assert qfilter.doc_length(qfilter.nlp(texts[0]), doc_length=(5, 100)) is False
        assert qfilter.doc_length(qfilter.nlp(texts[-1]), doc_length=(5, 100)) is True

    def test_qualityFilter(self, texts, qfilter):
        filtered = list(qfilter(texts))
        assert len(filtered) == 1
        assert sum(qfilter.filtered.values()) == (len(texts) - 1)

    def test_string_filter(self, texts, qfilter):
        assert (
            qfilter.string_filter(qfilter.nlp(texts[0]), string="lorem ipsum") is True
        )
        assert qfilter.string_filter(qfilter.nlp(texts[0])) is True
        assert (
            qfilter.string_filter(qfilter.nlp(texts[9]), string="lorem ipsum") is False
        )
