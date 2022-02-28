from typing import List

from dfm.cleaning import QualityFilter
import pytest


class TestQualityFilter:
    """Unit tests for the QualityFilter class"""

    @pytest.fixture(scope="class")
    def tweet_texts(self):
        return [
            "jeg er glad",
            "56789okd23456789098765sds",
            "jeg er glad...",
            "jeg er glad…",
            "67 54 13 B7",
            "#yolo # test ##",
        ]

    @pytest.fixture(scope="class")
    def long_text(self):
        return """
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

    @pytest.fixture(scope="class")
    def bullets_texts(self):
        t1 = """
        [summary]

        - test 1
        - test 1
            - test 2
            - test 3
                - test 1
        """

        t2 = """
        [summary]

        * test 1
            * test 2
            * test 3
        * test 1
            * test 2
                * test 3
        """
        return [t1, t2]

    @pytest.fixture(scope="class")
    def all_texts(self, tweet_texts, long_text, bullets_texts):
        return tweet_texts + [long_text] + [bullets_texts]

    @pytest.fixture(scope="class")
    def stop_words(self):
        return set(
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

    @pytest.fixture(scope="class")
    def quality_filter(self):
        return QualityFilter()

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("jeg er glad", True),
            ("56789okd23456789098765sds", False),
        ],
    )
    def test_stop_words(self, quality_filter, stop_words, text: str, expected: bool):
        assert (
            quality_filter.stop_word(
                quality_filter.nlp(text), n=2, stop_words=stop_words
            )
            is expected
        )

    @pytest.mark.parametrize(
        "texts,expected",
        [
            (pytest.lazy_fixture("bullets_texts"), False),
            (["56789okd23456789098765sds"], True),
        ],
    )
    def test_line_bullets(self, quality_filter, texts: List[str], expected: bool):
        for t in texts:
            assert (
                quality_filter.line_bullets_or_ellipsis(
                    quality_filter.nlp(t), max_p_bullets=0.5, max_p_ellipsis=1
                )
                is expected
            )

    @pytest.mark.parametrize(
        "text,expected",
        [("jeg er glad", True), ("jeg er glad...", False), ("jeg er glad…", False)],
    )
    def test_line_ellipsis(self, quality_filter, text: str, expected: bool):
        assert (
            quality_filter.line_bullets_or_ellipsis(
                quality_filter.nlp(text),
                max_p_bullets=1.0,
                max_p_ellipsis=0.5,
            )
            is expected
        )

    @pytest.mark.parametrize(
        "text,expected", [("jeg er glad", True), ("67 54 13 B7", False)]
    )
    def test_find_alpha(self, quality_filter, text: str, expected: bool):
        assert quality_filter.alpha(quality_filter.nlp(text), ratio=0.8) is expected

    @pytest.mark.parametrize(
        "text,expected", [("jeg er glad", True), ("56789okd23456789098765sds", False)]
    )
    def test_mean_word_length(self, quality_filter, text: str, expected: bool):
        assert (
            quality_filter.mean_word_length(
                quality_filter.nlp(text), mean_word_length=(3, 10)
            )
            is expected
        )

    @pytest.mark.parametrize(
        "text,expected",
        [(pytest.lazy_fixture("long_text"), True), ("jeg er glad", False)],
    )
    def test_doc_length(self, quality_filter, text: str, expected: bool):
        assert (
            quality_filter.doc_length(quality_filter.nlp(text), doc_length=(5, 150))
            is expected
        )

    def test_quality_filter(self, quality_filter, all_texts):
        filtered = list(quality_filter(all_texts))
        assert len(filtered) == 1
        assert sum(quality_filter.filtered.values()) == (len(all_texts) - 1)
