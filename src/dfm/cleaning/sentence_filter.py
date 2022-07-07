"""Filter on a sentence level, most of which are from [1].

Authors:
    Dan Saattrup Nielsen (dan.nielsen@alexandra.dk)
    Philip Krejler (pk@capacit.com)

References:
    [1] Raffel, C., Shazeer, N., Roberts, A., Lee, K., Narang, S., Matena, M., ... &
        Liu, P. J. (2020). Exploring the limits of transfer learning with a unified
        text-to-text transformer. J. Mach. Learn. Res., 21(140), 1-67.
"""

from collections import Counter
from typing import Any, Callable, Dict, Iterable, Optional, Sequence, Tuple, Union
from joblib import Parallel, delayed
import multiprocessing as mp

import emoji


class SentenceFilter:
    """Filter on a sentence level, most of which are from [1].

    Args:
        filter_names (sequence of str or None, optional):
            A sequence of filter names to be applied to the corpus. Must be among the
            following:
                - ends_with_punctuation_or_emoji
                - has_few_title_cased_words
                - has_enough_words
                - has_few_curly_brackets
            If None then all filters will be applied. Defaults to None.
        title_cased_words_threshold (float, optional):
            The threshold for the maximal number of title cased words in a sentence. If
            the number of title cased words in a sentence is greater than this
            threshold, then the sentence will be filtered out. Must be between 0 and 1,
            inclusive. Defaults to 0.7.
        min_num_words (int, optional):
            The minimum number of words in a sentence. If the number of words in a
            sentence is less than this number, then the sentence will be filtered
            out. Defaults to 3.
        curly_brackets_threshold (int, optional):
            The threshold for the maximal number of curly brackets in a sentence. If
            the number of curly brackets in a sentence is greater than this threshold,
            then the sentence will be filtered out. Defaults to 2.

    Attributes:
        title_cased_words_threshold (float):
            The threshold for the number of title cased words in a sentence.
        min_num_words (int):
            The minimum number of words in a sentence.
        curly_brackets_threshold (float):
            The threshold for the number of curly brackets in a sentence.
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
        title_cased_words_threshold: float = 0.7,
        min_num_words: int = 3,
        curly_brackets_threshold: int = 2,
    ):

        # Store arguments as attributes
        self.title_cased_words_threshold = title_cased_words_threshold
        self.min_num_words = min_num_words
        self.curly_brackets_threshold = curly_brackets_threshold

        # Create a dictionary with all the sentence filters
        _all_filters: Dict[str, Callable[[str], bool]] = dict(
            ends_with_punctuation_or_emoji=self._ends_with_punctuation_or_emoji,
            has_few_title_cased_words=self._has_few_title_cased_words,
            has_enough_words=self._has_enough_words,
            has_few_curly_brackets=self._has_few_curly_brackets,
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
        self.filter_counts = Counter()

    def filter_corpus(
        self,
        texts: Union[Iterable[str], Iterable[Tuple[str, Optional[Any]]]],
        progress_bar: bool = True,
        total: Optional[int] = None,
    ) -> Union[Iterable[str], Iterable[Tuple[str, Union[Any, None]]]]:
        """Filters a corpus using the sentence filters.

        Args:
            texts (iter of str, or iter of pairs):
                An iterable of strings of the text to be filtered, or an iterable of
                pairs with the first element being the text to be filtered.
            progress_bar (bool, optional):
                Whether to show a progress bar. Defaults to True.
            total (int or None, optional):
                The total number of texts to be filtered, to be used in the progress
                bar. If None, then the progress bar will not have a total. Defaults
                to None.

        Yields:
            str or pair:
                The filtered text, either as a single string or as a tuple with the
                text being the first element.
        """
        # Ensure that the texts are iterable
        docs = iter(texts)

        def filter_sample(
                sample: Union[str, Tuple[str, Optional[Any]]]
            ) -> Union[str, Tuple[str, Optional[Any]]]:
            """Filter a sample.

            Args:
                sample (str or pair):
                    The sample to be filtered.

            Returns:
                str or pair:
                    The filtered sample.
            """
            # If the document is a tuple, then we expect the first element to
            # be the text, and the second element to be the metadata.
            if isinstance(sample, tuple):
                doc, context = sample
            elif isinstance(sample, str):
                doc = sample
                context = None
            else:
                raise TypeError(
                    "Expected either a string or a tuple, got {type(sample)}."
                )

            # Split the document into sentences, splitting on newlines
            sentences = [
                sentence.strip()
                for sentence in doc.split("\n")
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

            # Otherwise, we yield the new document, where we also include the
            # context if it was passed in
            if isinstance(sample, tuple):
                return new_doc, context
            else:
                return new_doc

        # Main filtering loop
        n_jobs = mp.cpu_count() - 1
        with Parallel(n_jobs=n_jobs) as parallel:

            # Set up iterator, depending on whether we have a progress bar or not
            if progress_bar:
                itr = tqdm(docs, desc="Filtering corpus", total=total)
            else:
                itr = docs

            # Filter all documents
            for doc in parallel(delayed(filter_sample)(sample) for sample in itr):
                yield doc

            # Close the progress bar, if we had one
            if progress_bar:
                itr.close()

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

        # Add all the "manual" emojis, like ":)" and ":-("
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

    def _has_enough_words(self, sentence: str) -> bool:
        """Checks if a sentence contains enough words.

        Args:
            sentence (str):
                The sentence to check.

        Returns:
            bool:
                True if the sentence contains enough words, False otherwise.
        """
        # Split the sentence into words
        words = [word for word in sentence.split() if len(word) > 0]

        # Return whether the number of words is sufficiently high
        return len(words) >= self.min_num_words

    def _has_few_curly_brackets(self, sentence: str) -> bool:
        """Checks if a sentence contains few curly brackets.

        Args:
            sentence (str):
                The sentence to check.

        Returns:
            bool:
                True if the sentence contains many curly brackets, False otherwise.
        """
        # Count the number of curly brackets
        num_curly_brackets = sentence.count("{") + sentence.count("}")

        # Return whether the number of curly brackets is sufficiently low
        return num_curly_brackets < self.curly_brackets_threshold


if __name__ == "__main__":
    from datasets import load_dataset
    from tqdm.auto import tqdm
    import time

    # Initialise the filter
    sentence_filter = SentenceFilter()

    # Load the dataset
    dagw = load_dataset(
        "DDSC/dagw_reddit_filtered_v1.0.0",
        split="train",
        use_auth_token=True,
    )

    # Create filter generator
    filtered_docs = sentence_filter.filter_corpus(dagw["text"], total=len(dagw))

    # Initialise timer
    t0 = time.time()

    # Filter the texts
    for doc in filtered_docs:
        pass

    # Record the time taken
    time_taken = time.time() - t0

    # Print the time taken
    print(f"Time taken: {time_taken} seconds.")

    breakpoint()
