import pytest

from src.dfm.cleaning.doc_filter import DocumentFilter

class TestLanguageDetection: 
    
    @pytest.fixture(scope="class")
    def doc_filter(self): 
        return {
            'luga': DocumentFilter(filter_names=['detect_language'], language_detection_tool='luga'),
            'langdetect': DocumentFilter(filter_names=['detect_language'], language_detection_tool='langdetect') 
        } 
    
    @pytest.fixture(scope="class")
    def documents(self): 
        docs = ["""
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
        """
        ]
        return docs
    
    @pytest.fixture(scope="class")
    def correct_document_indicies(self): 
        return [1, 2]

    def test_language_detection_luga(self, doc_filter, documents, correct_document_indicies): 
        filter = doc_filter.get('luga')
        passed_indicies = [
            i for i, doc in enumerate(documents) if filter(doc) 
        ]
        assert(passed_indicies == correct_document_indicies)
    
    def test_language_detection_langdetect(self, doc_filter, documents, correct_document_indicies): 
        filter = doc_filter.get('langdetect')
        passed_indicies = [
            i for i, doc in enumerate(documents) if filter(doc) 
        ]
        assert(passed_indicies == correct_document_indicies)



    


    