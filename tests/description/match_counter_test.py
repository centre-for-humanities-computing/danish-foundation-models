import pytest
import spacy
from src.dfm.description import MatchCounter


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
        return [
            {"soldat": [{"LOWER": {"REGEX": "soldat.+"}}]},
            {"tokens": [{"LOWER": {"REGEX": ".+"}}]},
        ]

    @pytest.fixture(scope="class")
    def term_pattern_list(self):
        return MatchCounter.term_list_to_spacy_match_patterns(
            term_list=["heks", "soldat"]
        )

    @pytest.fixture(scope="class")
    def nlp(self):
        return spacy.blank("da")

    @pytest.fixture(scope="class")
    def mc_basic(self, nlp, term_pattern_list):
        return MatchCounter(match_patterns=term_pattern_list, nlp=nlp)

    @pytest.fixture(scope="class")
    def pæn_matcher(self, nlp):
        pæn_match_patterns = MatchCounter.term_list_to_spacy_match_patterns(
            term_list=["pæn"]
        )

        return MatchCounter(match_patterns=pæn_match_patterns, nlp=nlp)

    def test_term_list_pattern_generation(self, term_pattern_list):
        assert term_pattern_list == [
            {"heks": [{"LOWER": "heks"}]},
            {"soldat": [{"LOWER": "soldat"}]},
        ]

    def test_matcher_object_generation(self, regex_patterns, mc_basic):
        matcher_objects = mc_basic.create_matcher_object_from_pattern_list(
            pattern_container_list=regex_patterns
        )

        assert len(matcher_objects) == 2

    def test_token_counts(self, regex_patterns, nlp):
        mc = MatchCounter(match_patterns=regex_patterns, nlp=nlp)

        texts = ["Været på Altevatnet kl. "]

        assert mc.count(texts)["tokens"] == [4]

    def test_get_counts_from_each_doc(self, texts, mc_basic):
        """
        Gets counts from all docs in texts. For e.g. "heks", the list means that the token occurs:
            0 times in doc 1,
            1 time on doc 2,
            0 times in doc 3
        """

        counts = mc_basic.count(texts)

        assert counts == {"heks": [0, 1, 0], "soldat": [1, 0, 2]}

    def test_multiple_matches_under_same_label(self, nlp):
        from dfm.description.description_patterns import get_religion_patterns

        mc = MatchCounter(match_patterns=get_religion_patterns(), nlp=nlp)

        texts = ["En kristen er en del af de kristne, og kristne tror på kristendommen"]

        assert mc.count(texts)["rel_christian"] == [4]

    def test_genders_not_matching_on_prefix(self, nlp):
        gender_pronoun_patterns = [
            {"male_pronoun": [{"LOWER": "han"}]},
            {"female_pronoun": [{"LOWER": "hun"}]},
        ]

        mc = MatchCounter(match_patterns=gender_pronoun_patterns, nlp=nlp)

        texts = ["Handlekraftig, handlekraft, handlekraften"]

        assert mc.count(texts)["male_pronoun"] == [0]

    def test_labelled_term_list_generation(self):
        labelled_term_list = [{"christian": ["christian", "christianity"]}]

        output = MatchCounter.list_of_labelled_term_lists_to_spacy_match_patterns(
            list_of_labelled_term_lists=labelled_term_list, lowercase=True
        )

        assert output == [
            {"christian": [{"LOWER": "christian"}]},
            {"christian": [{"LOWER": "christianity"}]},
        ]

    def test_count_token_multipel_times(self, mc_basic):
        texts = ["En soldat er en soldat som en soldat er"]
        counts = mc_basic.count(texts)

        assert counts == {"heks": [0], "soldat": [3]}

    def test_lowercasing(self, mc_basic):
        texts = ["Soldat"]
        counts = mc_basic.count(texts)

        assert counts == {"heks": [0], "soldat": [1]}

    def test_normalisation(self, pæn_matcher):
        texts = ["pæn", "paen", "pœn"]

        assert pæn_matcher.count(texts) == {"pæn": [1, 0, 0]}

    def test_symbols(self, pæn_matcher):
        texts = ["pæn", "pæn,", "pæn?"]

        assert pæn_matcher.count(texts) == {"pæn": [1, 1, 1]}

    def test_newlines(self, pæn_matcher):
        texts = ["pæn", "p\næn,"]

        assert pæn_matcher.count(texts) == {"pæn": [1, 0]}

    def test_lemmatization(self, pæn_matcher):
        texts = ["pæn", "pænere", "pænest"]

        assert pæn_matcher.count(texts) == {"pæn": [1, 0, 0]}
