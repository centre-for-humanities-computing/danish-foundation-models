"""Test for the quality filter"""

from typing import List

import pytest
from pytest_lazyfixture import lazy_fixture

from src.dfm.cleaning import QualityFilter


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
    def quality_filter(self):
        return QualityFilter(top_ngram_min_count=1)

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("jeg er glad", True),
            ("56789okd23456789098765sds", False),
        ],
    )
    def test_stop_words(self, quality_filter, text: str, expected: bool):
        assert quality_filter.stop_word(quality_filter.nlp(text), n=2) is expected

    @pytest.mark.parametrize(
        "texts,expected",
        [
            (lazy_fixture("bullets_texts"), False),
            (["56789okd23456789098765sds"], True),
        ],
    )
    def test_line_bullets(self, quality_filter, texts: List[str], expected: bool):
        for t in texts:
            assert (
                quality_filter.line_bullets_or_ellipsis(
                    quality_filter.nlp(t),
                    max_p_bullets=0.5,
                    max_p_ellipsis=1,
                    min_bullets=0,
                    min_ellipsis=0,
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
                min_bullets=0,
                min_ellipsis=0,
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

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("dasdsadasdasdddddddddd\njeg er glad\n" * 2, False),
            ("jeg er glad\n\n" * 4, False),
        ],
    )
    def test_duplicate_line_chr_fraction(
        self, quality_filter, text: str, expected: bool
    ):
        filter_func = quality_filter.filters["duplicate_lines_chr_fraction"]
        nlp = quality_filter.nlp
        assert filter_func(nlp(text)) is expected

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("dasdsadasdasdddddddddd\njeg er glad\n" * 2, True),
            ("jeg er glad\n\n" * 4, False),
        ],
    )
    def test_duplicate_para_chr_fraction(
        self, quality_filter, text: str, expected: bool
    ):
        filter_func = quality_filter.filters["duplicate_paragraph_chr_fraction"]
        nlp = quality_filter.nlp
        assert filter_func(nlp(text)) is expected

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("Jeg er jeg er jeg, JeG ER, jeg er", False),
            ("jeg er glad, men også noglegange sur...", True),
        ],
    )
    def test_top_ngram_chr_fraction(self, quality_filter, text: str, expected: bool):
        filter_func = quality_filter.filters["top_ngram_chr_fraction"]
        nlp = quality_filter.nlp
        assert filter_func(nlp(text)) is expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("jeg er glad, men også noglegange sur måske hvertfald." * 10, False),
            ("jeg er glad, men også noglegange sur...", True),
        ],
    )
    def test_duplicate_ngram_chr_fraction(
        self, quality_filter, text: str, expected: bool
    ):
        filter_func = quality_filter.filters["duplicate_ngram_chr_fraction"]
        nlp = quality_filter.nlp
        assert filter_func(nlp(text)) is expected

    @pytest.mark.parametrize(
        "documents_language, correct_document_indicies",
        [
            (
                [
                    """
        This is not a danish sentence, nor is the entire document danish. This will hopefully not be flagged as danish.
        We've added a new sentence on a new line in order to introduce a newline character.
        """,
                    """
        Dette er en dansk sætning, som burde blive klassificeret korrekt af diverse værktøjer.
        Vi har igen introduceret en ny linje, således at vi får specielle karakterer med.
        """,
                    # Text from quality filter test
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
        """,
                    # Norwegian text from https://huggingface.co/datasets/norwegian_ner
                    """
        Lam og piggvar på bryllupsmenyen
        Kamskjell, piggvar og lammefilet sto på menyen under den kongelige gallamiddagen.
        Hagen forsøkte i går å holde spenningen ved like -og dermed sikre seg nok et døgns medieoppmerksomhet
        """,
                    # Swedish text from https://huggingface.co/datasets/swedish_reviews
                    """
        Undvik för allt i världen detta oseriösa företag! Anlitade dem två gånger. Trodde naivt att första gången var en engångsföreteelse men de utför helt enkelt inte arbetet som de utlovar korrekt.
        Detta leder till att man måste sitta i telefonväxel om och om igen med dem och försöka reda ut saker när hela poängen med såna tjänster är att slippa strul.
        """,
                ],
                [1, 2],
            )
        ],
    )
    def test_language_detection_luga(
        self, quality_filter, documents_language, correct_document_indicies
    ):
        filter = quality_filter.filters["detect_language"]
        nlp = quality_filter.nlp
        passed_indicies = [
            i for i, doc in enumerate(documents_language) if filter(nlp(doc))
        ]
        assert passed_indicies == correct_document_indicies

    @pytest.mark.parametrize(
        "documents_language, expected",
        [
            (
                """Denne paragraf
          burde blive
          eklsuderet, da der
          næsten ikke er nogen lange sætninger.
          Den lange sætning kommer her, og den skal have minimum 30 tegn, eller bliver den klassificeret som kort
          """,
                False,
            ),
            (
                """Frederikshavn blev det første sted, der mærkede vindstød af stormstyrke,
        og nu er det også det første sted, der har mærket vindstød af stærk storm. Hvis det er noget at prale af.
        Kort sætning her
        """,
                True,
            ),
        ],
    )
    def test_short_long_sentence(
        self, quality_filter, documents_language: str, expected: bool
    ):
        filter = quality_filter.filters["short_long_sentece"]
        nlp = quality_filter.nlp
        assert filter(nlp(documents_language)) == expected
