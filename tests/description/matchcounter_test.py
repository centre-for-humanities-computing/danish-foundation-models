import pytest
from dfm.description import MatchCounter
import spacy


class TestMatchCounter:
    @pytest.fixture(scope="class")
    def texts(self):
        texts = [
            "Der kom en soldat marcherende hen ad landevejen: én, to! én, to! Han havde sit tornyster på ryggen og en sabel ved siden, for han havde været i krigen, og nu skulle han hjem.",
            "Så mødte han en gammel heks på landevejen; hun var så ækel, hendes underlæbe hang hende lige ned på brystet.",
            "Hun sagde: God aften, soldat! Hvor du har en pæn sabel og et stort tornyster, du er en rigtig soldat! Nu skal du få så mange penge, du vil eje!",
        ]

        return texts

    @pytest.fixture(scope="class")
    def regex_patterns(self):
        return [{"soldat": [{"LOWER": {"REGEX": "soldat.+"}}]}]

    @pytest.fixture(scope="class")
    def term_pattern_list(self):
        return MatchCounter.term_list_to_lowercase_match_patterns(
            term_list=["heks", "soldat"]
        )

    @pytest.fixture(scope="class")
    def nlp(self):
        return spacy.blank("da")

    @pytest.fixture(scope="class")
    def mc_basic(self, nlp, term_pattern_list):
        return MatchCounter(match_patterns=term_pattern_list, nlp=nlp)

    def test_term_list_pattern_generation(self, term_pattern_list):
        assert term_pattern_list == [
            {"heks": [{"LOWER": "heks"}]},
            {"soldat": [{"LOWER": "soldat"}]},
        ]

    def test_matcher_object_generation(self, regex_patterns, mc_basic):
        matcher_objects = mc_basic.gen_matcher_objects_from_pattern_list(
            pattern_container_list=regex_patterns
        )

        assert len(matcher_objects) == 1

    def test_counting(self, texts, mc_basic):
        counts = mc_basic.count(texts)

        assert counts == {"heks": [0, 1, 0], "soldat": [1, 0, 2]}
