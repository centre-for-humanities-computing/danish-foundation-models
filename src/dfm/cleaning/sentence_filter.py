"""Filter on a sentence level, most of which are from [1].

Authors:
    Dan Saattrup Nielsen (dan.nielsen@alexandra.dk)
    Philip Krejler (pk@capacit.com)

References:
    [1] Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M., ... &
        Liu, P. J. (2020). Exploring the limits of transfer learning with a unified
        text-to-text transformer. J. Mach. Learn. Res., 21(140), 1-67.
"""

from typing import Iterable, Union, Tuple, Any, Dict, Callable, Sequence, Optional
from collections import Counter
import emoji


class SentenceFilter:
    """Filter on a sentence level, most of which are from [1].

    Args:
        filter_names (sequence of str or None, optional):
            A sequence of filter names to be applied to the corpus. Must be among the
            following:
                - ends_with_punctuation_or_emoji
                - has_few_title_cased_words
            If None then all filters will be applied. Defaults to None.
        title_cased_words_threshold (float, optional):
            The threshold for the number of title cased words in a sentence. If the
            number of title cased words in a sentence is greater than this threshold,
            then the sentence will be filtered out. Must be between 0 and 1, inclusive.
            Defaults to 0.9.

    Attributes:
        filters (dict):
            A dictionary with all the sentence filters to be applied. Keys are the
            names of the filters and values are the filter functions.
        filter_counts (Counter):
            A counter keeping track of how many sentences each filter removed.

    References:
        [1] Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M., ...
            & Liu, P. J. (2020). Exploring the limits of transfer learning with a
            unified text-to-text transformer. J. Mach. Learn. Res., 21(140), 1-67.
    """
    def __init__(
            self,
            filter_names: Optional[Sequence[str]] = None,
            title_cased_words_threshold: float = 0.9,
        ):

        # Store arguments as attributes
        self.title_cased_words_threshold = title_cased_words_threshold

        # Create a dictionary with all the sentence filters
        _all_filters: Dict[str, Callable[[str], bool]] = dict(
            ends_with_punctuation_or_emoji=self._ends_with_punctuation_or_emoji,
            has_few_title_cased_words=self._has_few_title_cased_words,
        )

        # Create variable storing the filters to be used
        self.filters: Dict[str, Callable[[str], bool]] = dict()
        if filter_names is None:
            self.filters = _all_filters
        else:
            self.filters = {
                filter_name: _all_filters[filter_name]
                for filter_name in filter_names
            }

        # Create a counter for keeping track of how many documents each filter removed
        self.filter_counts = Counter()

    def filter_corpus(
        self, texts: Union[Iterable[str], Iterable[Tuple[str, Optional[Any]]]],
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

                # Split the document into sentences, splitting on newlines
                sentences = [
                    sentence.strip() for sentence in doc.split("\n")
                    if len(sentence.strip()) > 0
                ]

                # Apply the filters to the sentences
                filters_triggered = list(map(self.apply_filters, sentences))

                # Create a new document from the sentences that didn't trigger any
                # filters
                new_doc = "\n".join(
                    sentence
                    for sentence, filter_name in zip(sentences, filters_triggered)
                    if filter_name is None
                )

                # If all sentences were filtered, then we don't yield anything, and
                # instead just skip to the next document
                if new_doc == "":
                    continue

                # Otherwise, we yield the new document, where we also include the
                # context if it was passed in
                if isinstance(doc_or_tuple, tuple):
                    yield new_doc, context
                else:
                    yield new_doc

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

    def _ends_with_punctuation_or_emoji(self, sentence: str) -> bool:
        """Checks if a sentence ends with punctuation or an emoji.

        Args:
            sentence (str):
                The sentence to check.

        Returns:
            bool:
                True if the sentence ends with punctuation, False otherwise.
        """
        # Initialise the list of emojis
        emojis = list()

        # Add all unicode emojis as well as the codes for them, like :blush:. The codes
        # are the keys in the `emoji.UNICODE_EMOJI["en"]` dictionary, and the emojis
        # are the values.
        emoji_dict = emoji.UNICODE_EMOJI["en"]
        emojis += list(emoji_dict.keys())
        emojis += list(emoji_dict.values())

        # Add all the "manual" emojis, like ":)" and ":-("
        mouths = list(")(DPpOo@")
        noses = ["", "-"]
        eyes = list(":;")
        emojis += [
            f"{eye}{nose}{mouth}" for eye in eyes for nose in noses for mouth in mouths
        ]
        emojis += [
            f"{mouth}{nose}{eye}" for eye in eyes for nose in noses for mouth in mouths
        ]

        # Add punctuation symbols which signify the end of a sentence. We include
        # quotation marks as quotes may end in these symbols
        punctuation = list(".!?\"'")

        # Return whether the input sentence ends with any of the symbols
        return any(sentence.endswith(char) for char in emojis + punctuation)

    def _has_few_title_cased_words(self, sentence: str) -> bool:
        """Checks if a sentence contains few title cased words.

        This is to exclude menus and lists, which are often all title cased. Note that
        actual titles in Danish are not title cased.

        Args:
            sentence (str):
                The sentence to check.

        Returns:
            bool:
                True if the sentence contains many title cased words, False otherwise.
        """
        # Split the sentence into words
        words = [word for word in sentence.split() if len(word) > 0]

        # Count the number of title cased words
        num_title_cased_words = len(list(filter(lambda word: word.istitle(), words)))

        # Compute the proportion of title cased words in the sentence
        proportion_title_cased_words = num_title_cased_words / len(words)

        # Return whether the proportion of title cased words is sufficiently low
        return proportion_title_cased_words < self.title_cased_words_threshold
