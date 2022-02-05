from dfm.description.gen_description import get_match_counts_from_doc, gen_matcher_object_from_pattern_list
import spacy
import pytest


@pytest.fixture
def nlp():
    return spacy.blank("da")


def test_multiple_match_counts(nlp):
    """
    Ensure that regex doesn't match multiple times on the same token,
    e.g. athei.* might match 4 times on atheisme.
    """

    pattern_container_list = [
        {"atheism": [{"LOWER": {"REGEX": "athei.+"}}]},
        {"atheism": [{"LOWER": {"REGEX": "atei.+"}}]},
        {"skøde": [{"LOWER": "skøde"}]},
    ]

    doc = nlp("Atheisterne, atheisme, atheist, ateisterne, ateist, atelier")
    expected = {"atheism": 5, "skøde": 0}

    matcher_object = gen_matcher_object_from_pattern_list(pattern_container_list, nlp)

    assert get_match_counts_from_doc(doc, matcher_object, nlp) == expected
