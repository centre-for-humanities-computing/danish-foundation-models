from dfm.cleaning import ProfanityFilter
import pytest

from dfm.data.load import (
    load_mc4
)

class TestProfanityFilter:
    def test_filters_inappropriate_text(self):
        profanity_filter = ProfanityFilter()
        
        assert (
                list(profanity_filter(["Penis"])) == []
        )

    def test_does_not_filter_appropriate_text(self):
        profanity_filter = ProfanityFilter()
        
        assert (
                list(profanity_filter(["Hello"])) == ["Hello"]
        )

    def test_filter_on_mc4(self):
        profanity_filter = ProfanityFilter()
        ds = load_mc4(streaming = True)
        texts = (d['text'] for d in ds['train'])
        list(profanity_filter(texts))
