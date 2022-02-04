from dfm.cleaning import ProfanityFilter
import pytest

class TestProfanityFilter:
    def test_filters_inappropriate_text(self):
        profanity_filter = ProfanityFilter()
        
        assert (
                profanity_filter(["Penis"]) == []
        )

    def test_does_not_filter_appropriate_text(self):
        profanity_filter = ProfanityFilter()
        
        assert (
                profanity_filter(["Hello"]) == ["Hello"]
        )
