"""Filter on a document level, some of which are from [1] and [2].

Authors:
    Dan Saattrup Nielsen (dan.nielsen@alexandra.dk)
    Philip Krejler (pk@capacit.com)

References:
    [1] Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M., ... &
        Liu, P. J. (2020). Exploring the limits of transfer learning with a unified
        text-to-text transformer. J. Mach. Learn. Res., 21(140), 1-67.

    [2] Abadji, Julien, et al. "Towards a Cleaner Document-Oriented Multilingual 
    Crawled Corpus." arXiv preprint arXiv:2201.06642 (2022).
"""
from typing import (Any, Callable, Dict, Iterable, Optional, Sequence, Tuple,
                    Union)

from collections import Counter

from luga import language 
from langdetect import detect_langs

class DocumentFilter: 
    """Filter on a document level, inspired by [1] and [2]
    
    Args: 
        filter_names (sequence of str or None, optional): 
            A sequence of filters are applied to the corpus. Must be among the following: 
                - detect_language
                - short_long_sentences_ratio
            If None then all filters are applied. Defaults to None
        language_threshold (float, optional): 
            The threshold used for minimum confidence in langauge detection. If the language detection model
            outputs a probability lower than the threshold, then the document will be discarded. Defaults to 0.99
        languages (sequence): 
            Sequence of languages to perform language detection for. Defaults to ['da'].
        short_long_sentence_length_split (int): 
            Number of characters to determine whether short or long sentence - if number of characters exceed short_long_sentence_length_split
            then it is classfied as a long sentence, and vice versa
        short_long_sentence_ratio (float): 
            The threshold for minimum ratio between short and long sentences. Short and long sentences are defined as ____. 
            If the ratio n_long / n_short (n_short = number of short sentences, n_long = number of long sentences) 
            is below the threshold, the document will be discarded. Defaults to 0.6
            
    Attributes: 
        filters (dict):
            A dictionary with all the document filters to be applied. Keys are the
            names of the filters and values are the filter functions.
        filter_counts (Counter):
            A counter keeping track of how many documents each filter removed.

    References: 
        [1] Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M., ... &
        Liu, P. J. (2020). Exploring the limits of transfer learning with a unified
        text-to-text transformer. J. Mach. Learn. Res., 21(140), 1-67.

        [2] Abadji, Julien, et al. "Towards a Cleaner Document-Oriented Multilingual 
        Crawled Corpus." arXiv preprint arXiv:2201.06642 (2022).
    """

    __available_language_detection_tools = ['langdetect', 'luga']

    def __init__(
        self, 
        filter_names: Optional[Sequence[str]] = None,
        language_detection_tool: str = 'luga', 
        language_threshold: float = 0.90, 
        languages: Sequence[str] = ['da'],  
        short_long_sentence_length_split: int = 100, 
        short_long_sentence_threshold: float = 0.5
    ): 

        if language_detection_tool not in self.__available_language_detection_tools: 
            raise AttributeError(f"{language_detection_tool} is not a valid language detection packages - must be in {self.__available_language_detection_tools}")
        
        # Store arguments as attributes
        self.language_threshold = language_threshold
        self.language_detection_tool = language_detection_tool
        self.languages = languages
        self.short_long_sentence_length_split = short_long_sentence_length_split
        self.short_long_sentence_threshold = short_long_sentence_threshold

        # Create a dictionary with all the sentence filters
        _all_filters: Dict[str, Callable[[str], bool]] = dict(
            detect_language=self._detect_language
        )

        # Create variable storing the filters to be used
        self.filters: Dict[str, Callable[[str], bool]] = dict()
        if filter_names is None:
            self.filters = _all_filters
        else:
            self.filters = {
                filter_name: _all_filters[filter_name] for filter_name in filter_names
            }

        # Create a counter for keeping track of how many documents each filter removed
        self.filter_counts: Counter = Counter()

    def filter_corpus(
        self,
        texts: Union[Iterable[str], Iterable[Tuple[str, Optional[Any]]]],
    ) -> Union[Iterable[str], Iterable[Tuple[str, Union[Any, None]]]]:
        """Filters a corpus using the sentence filters.

        Args:
            texts (iter of str, or iter of pairs):
                An iterable of strings of the text to be filtered, or an iterable of
                pairs with the first element being the text to be filtered.

        Yields:
            str or pair:
                The filtered text, either as a single string or as a tuple with the
                text being the first element.
        """
        # Ensure that the texts are iterable
        docs = iter(texts)

        # Iterate over all the documents in the corpus
        while docs:
            try:
                # Get the first document
                doc_or_tuple = next(docs)

                # If the document is a tuple, then we expect the first element to be the
                # text, and the second element to be the metadata.
                if isinstance(doc_or_tuple, tuple):
                    doc, context = doc_or_tuple
                elif isinstance(doc_or_tuple, str):
                    doc = doc_or_tuple
                    context = None
                else:
                    raise TypeError(
                        "Expected either a string or a tuple, "
                        f"got {type(doc_or_tuple)}."
                    )

                # Apply the filters to the sentences
                filters_triggered = list(map(self.apply_filters, doc))

                # If any filters were triggered, continue and dont return anything
                if len(filters_triggered) > 0:
                    continue

                # Otherwise, we yield the original document, where we also include the
                # context if it was passed in
                if isinstance(doc_or_tuple, tuple):
                    yield doc, context
                else:
                    yield doc

            except StopIteration:
                break

    def __call__(
        self, *args, **kwargs
    ) -> Union[Iterable[str], Iterable[Tuple[str, Union[Any, None]]]]:
        """Calls the `filter_corpus` method on the inputs.

        Args:
            *args:
                Positional arguments to be passed to `filter_corpus`.
            **kwargs:
                Keyword arguments to be passed to `filter_corpus`.

        Yields:
            str or pair:
                The filtered text, either as a single string or as a tuple with the
                text being the first element.
        """
        return self.filter_corpus(*args, **kwargs)

    def apply_filters(self, doc: str) -> Union[str, None]:
        """Applies all filters to document.

        Args:
            doc (str):
                The document the filters will be applied to.

        Returns:
            str or None:
                The name of the filter which filtered out the document, or None if the
                document wasn't filtered
        """
        # Iterate over all the filter functions
        for filter_name, filter_fn in self.filters.items():

            # Apply the filter function, which returns True if the document satisfied
            # the filter, and False if it didn't
            satisfied_filter = filter_fn(doc)

            # If the document did not satisfy the filter, then return the name of the
            # filter. This document will be removed from the corpus, and we return the
            # name to log what filter function was responsible for the removal of the
            # docuemnt
            if not satisfied_filter:
                self.filter_counts[filter_name] += 1
                return filter_name
        return None
    
    def _short_long_sentence(self, doc: str) -> bool: 
        """Checks that the ratio long sentences is above the minimum threshold 

        Inspired by implementation: https://github.com/oscar-corpus/ungoliant/blob/master/src/filtering/record.rs

        Args: 
            doc (str): 
                Document to check
        
        Returns: 
            bool: 
                True if the ratio long sentences is above the minimum threshold 
        """
        sentences = [sentence.strip() for sentence in doc.split("\n") if len(sentence.strip()) > 0]
        _long_count = 0
        _short_count = 0
        for sentence in sentences: 
            if len(sentence) > self.short_long_sentence_length_split: 
                _long_count += 1
            else: 
                _short_count += 1
        ratio = (_long_count + _short_count) / _long_count
        return ratio >= self.short_long_sentence_threshold

    def _detect_language(self, doc: str) -> bool: 
        """Checks if a language is detected and the confidence is higher than the minimum threshold

        Args: 
            doc (str): 
                Document to check
        
        Returns: 
            bool: 
                True if the probability of the detected language is higher than the minimum threshold
        """
        return self._detect_langs(doc)

    def _detect_langs(self, doc: str): 
        
        def luga_detect(doc: str) -> bool:

            doc = " ".join([sentence.strip() for sentence in doc.split("\n") if len(sentence.strip()) > 0])

            detected = language(doc) # type: ignore
            print(detected)
            lang, score = detected.name, detected.score
            if score >= self.language_threshold and lang in self.languages:
                return True
            else: 
                return False

        def langdetect_detect(doc: str) -> bool: 
            detected = detect_langs(doc) # type: ignore
            for l in detected:
                if l.lang in self.languages and l.prob >= self.language_threshold:
                    return True 
            return False

        detectors: Dict[str, Callable[[str], bool]] = {
            'luga': luga_detect,
            'langdetect': langdetect_detect
        }

        return detectors[self.language_detection_tool](doc)

if __name__ == "__main__": 
    dcf = DocumentFilter(
            filter_names=['detect_language'],
            language_detection_tool='luga',
            languages=['da', 'en']
        ) 
    documents = ["""
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

    print([
            i for i, doc in enumerate(documents) if dcf._detect_langs(doc) 
        ])
    


            
            



        







