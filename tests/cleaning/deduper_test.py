from dfm.cleaning import Deduper

import pytest
import tempfile
from pathlib import Path
import json

class TestDeduper:
    def dedup(self, corpus):
        temp = tempfile.NamedTemporaryFile()
        deduper = Deduper(split_method="none", random_seed=42, similarity_threshold=0.001, num_minhashes=2)
        deduper.deduplicate(corpus, output_fname=temp.name, overwrite=True)
        return [json.loads(line)['text'] for line in Path(temp.name).open("r")]

    def test_removes_exact_duplicates(self):
        assert (
            self.dedup(["hej", "hej", "farvel"]) == ["hej", "farvel"]
        )

    @pytest.mark.skip(reason="Not implemented")
    def test_removes_near_duplicates(self):
        assert (
            self.dedup([
                "Der kom en soldat marcherende hen ad landevejen: én, to! én, to! Han havde sit tornyster på ryggen og en sabel ved siden, for han havde været i krigen, og nu skulle han hjem. Så mødte han en gammel heks på landevejen; hun var så ækel, hendes underlæbe hang hende lige ned på brystet. Hun sagde: 'God aften, soldat! Hvor du har en pæn sabel og et stort tornyster, du er en rigtig soldat! Nu skal du få så mange penge, du vil eje!'",
                "er kom en soldat marcherende hen ad landevejen: én, to! én, to! Han havde sit tornyster på ryggen og en sabel ved siden, for han havde været i krigen, og nu skulle han hjem. Så mødte han en gammel heks på landevejen; hun var så ækel, hendes underlæbe hang hende lige ned på brystet. Hun sagde: 'God aften, soldat! Hvor du har en pæn sabel og et stort tornyster, du er en rigtig soldat! Nu skal du få så mange penge, du vil eje!'"
            ]) == ["Der kom en soldat marcherende hen ad landevejen: én, to! én, to! Han havde sit tornyster på ryggen og en sabel ved siden, for han havde været i krigen, og nu skulle han hjem. Så mødte han en gammel heks på landevejen; hun var så ækel, hendes underlæbe hang hende lige ned på brystet. Hun sagde: 'God aften, soldat! Hvor du har en pæn sabel og et stort tornyster, du er en rigtig soldat! Nu skal du få så mange penge, du vil eje!'"]
        )
