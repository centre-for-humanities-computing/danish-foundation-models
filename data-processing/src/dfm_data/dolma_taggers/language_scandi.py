"""

Dolma taggers for Scandinavian language detection.

"""
from collections.abc import Iterable

import pycld2 as cld2
import regex
from anyascii import anyascii
from dolma.core.data_types import DocResult, Document, Span, TextSlice
from dolma.core.ft_tagger import BaseFastTextTagger, Prediction
from dolma.core.registry import TaggerRegistry
from dolma.core.taggers import BaseTagger
from dolma.core.utils import split_paragraphs

LANGS = {
    "ENGLISH": "en",
    "DANISH": "da",
    "SWEDISH": "sv",
    "NORWEGIAN": "no",
    "ICELANDIC": "is",
    "FAROESE": "fo",  # Note that FAROESE is not supported by cld2 or fasttext
}


@TaggerRegistry.add("cld2_scandi_doc")
class Cld2ScandiLanguageTagger(BaseTagger):
    """This tagger runs the Compact Language Detect 2 model on a full document
    and will return a score between 0 and 1 for each language in LANGS.
    It uses the pretrained model from the pycld2 package."""

    RE_BAD_CHARS = regex.compile(r"[\p{Cc}\p{Cs}]+")

    def _sanitize_input(self, text: str) -> str:
        return self.RE_BAD_CHARS.sub("", text)

    def _to_ascii_input(self, text: str) -> str:
        return anyascii(text)

    def _identity_fn(self, text: str) -> str:
        return text

    def _predict_text(self, text: str) -> dict[str, float]:
        """Predict the language of a string and return the detected languages in a dictionary."""
        is_reliable = False
        details: Iterable[tuple[str, str, int, float]] = []
        for fn in (self._identity_fn, self._to_ascii_input, self._sanitize_input):
            try:
                retvals = cld2.detect(fn(text))
                assert len(retvals) == 3
                is_reliable, _, details = retvals
                # is_reliable is True if the detection is "high confidence"
                # details is a Tuple of up to three detected languages, where each is
                # tuple is (languageName, languageCode, percent, score).  percent is
                # what percentage of the original text was detected as this language
                # and score is the confidence score for that language.
                break
            except cld2.error:
                ...

        scores: dict[str, float] = {}
        if is_reliable:
            for lang, _, score, _ in details:
                if lang in LANGS:
                    scores[LANGS[lang]] = score / 100.0

        return scores

    def predict(self, doc: Document) -> DocResult:
        lang_scores = self._predict_text(doc.text)
        spans: list[Span] = []
        for lang_code in LANGS.values():
            # If the language was not detected we will still tag
            # the sentence with a score of 0
            score = lang_scores.get(lang_code, 0)

            positive_span = Span(
                start=0,
                end=len(doc.text),
                type=lang_code,
                score=score,
            )
            negative_span = Span(
                start=0,
                end=len(doc.text),
                type=f"not_{lang_code}",
                score=1.0 - score,
            )
            spans.append(positive_span)
            spans.append(negative_span)
        return DocResult(doc=doc, spans=spans)


@TaggerRegistry.add("cld2_scandi_paragraph")
class Cld2ScandiLanguageParagraphTagger(Cld2ScandiLanguageTagger):
    """This tagger runs the Compact Language Detect 2 model on each paragraph,
    and will save a score between 0 and 1 for each language in LANGS"""

    def predict(self, doc: Document) -> DocResult:
        paragraphs = split_paragraphs(doc.text)
        spans: list[Span] = []
        for paragraph in paragraphs:
            lang_scores = self._predict_text(paragraph.text)
            for lang_code in LANGS.values():
                score = lang_scores.get(lang_code, 0.0)

                positive_span = Span(
                    start=paragraph.start,
                    end=paragraph.end,
                    type=lang_code,
                    score=score,
                )
                negative_span = Span(
                    start=paragraph.start,
                    end=paragraph.end,
                    type=f"not_{lang_code}",
                    score=1.0 - score,
                )
                spans.extend((positive_span, negative_span))
        return DocResult(doc=doc, spans=spans)


@TaggerRegistry.add("ft_lang_id_scandi_doc")
class FastTextScandiLanguageDocumentTagger(BaseFastTextTagger):
    """This tagger runs the FastText language detection model on each document.
    The score is between 0 and 1 and provided for each language in LANGS.

    The method is described in the following papers:

    @article{joulin2016bag,
      title={Bag of Tricks for Efficient Text Classification},
      author={Joulin, Armand and Grave, Edouard and Bojanowski, Piotr and Mikolov, Tomas},
      journal={arXiv preprint arXiv:1607.01759},
      year={2016}
    }
    @article{joulin2016fasttext,
      title={FastText.zip: Compressing text classification models},
      author={Joulin, Armand and Grave, Edouard and Bojanowski, Piotr and Douze, Matthijs and J{\'e}gou, H{\'e}rve and Mikolov, Tomas},
      journal={arXiv preprint arXiv:1612.03651},
      year={2016}
    }

    The pretrained model is automatically downloaded (link publically available at):
    https://fasttext.cc/docs/en/language-identification.html

    """

    MODEL_PATH = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"

    def __init__(self):
        super().__init__(
            model_path=self.MODEL_PATH,
            model_mode=self.DOCUMENT_LEVEL_TAGGER,
        )

    def predict_slice(self, text_slice: TextSlice) -> Iterable[Prediction]:
        pred = self.classifier.predict(
            text_slice.text.lower().replace("\n", " ").strip(),
            k=-1,
        )
        # Initialize scores to 0
        scores = {k: 0.0 for k in LANGS.values()}

        for label, score in zip(*pred):
            # label is of the form __label__[code]
            label_code = label[-2:]
            if label_code in scores:
                scores[label_code] = score

        predictions_positive = [Prediction(label=k, score=v) for k, v in scores.items()]
        predictions_negative = [
            Prediction(label=f"not_{k}", score=1.0 - v) for k, v in scores.items()
        ]

        return predictions_positive + predictions_negative


@TaggerRegistry.add("ft_lang_id_scandi_paragraph")
class FastTextScandiLanguageParagraphTagger(FastTextScandiLanguageDocumentTagger):
    """This tagger runs the FastText language detection model on each paragraph.
    The score is between 0 and 1 and provided for each language in LANGS.
    """

    def __init__(self):
        BaseFastTextTagger.__init__(
            self,
            model_path=self.MODEL_PATH,
            model_mode=self.PARAGRAPH_LEVEL_TAGGER,
        )


def add_global_language_score_from_slice_score(result: DocResult) -> DocResult:
    # the total document score is # of characters in each "lang" span multiplied by the likelihood
    # of said span being lang
    for lang in LANGS.values():
        try:
            doc_lang_score = sum(
                (s.end - s.start) * s.score for s in result.spans if s.type == lang
            ) / len(
                result.doc.text,
            )
            doc_not_lang_score = 1 - doc_lang_score
        except ZeroDivisionError:
            doc_lang_score = doc_not_lang_score = 0.0

        doc_level = (
            Span(
                start=0,
                end=len(result.doc.text),
                type=f"doc_{lang}",
                score=doc_lang_score,
            ),
            Span(
                start=0,
                end=len(result.doc.text),
                type=f"doc_not_{lang}",
                score=doc_not_lang_score,
            ),
        )
        result.spans.extend(doc_level)
    return result


# Composite tagger that provides both paragraph and doc scores
@TaggerRegistry.add("cld2_scandi_paragraph_with_doc_score")
class Cld2ScandiLanguageParagraphWithDocScoreTagger(
    Cld2ScandiLanguageParagraphTagger,
):
    """This tagger runs the Compact Language Detect 2 model on each paragraph
    and will also provide a total score for each document.
    The score is between 0 and 1 and provided for each language in LANGS."""

    def predict(self, doc: Document) -> DocResult:
        doc_result = super().predict(doc)
        doc_result = add_global_language_score_from_slice_score(doc_result)
        return doc_result


# Composite tagger that provides both paragraph and doc scores
@TaggerRegistry.add("ft_lang_id_scandi_paragraph_with_doc_score")
class FastTextScandiLanguageParagraphWithDocScoreTagger(
    FastTextScandiLanguageParagraphTagger,
):
    """This tagger runs the FastText language detection model on each paragraph,
    and will also provide a total score for each document.
    The score is between 0 and 1 and provided for each language in LANGS.
    """

    def predict(self, doc: Document) -> DocResult:
        doc_result = super().predict(doc)
        doc_result = add_global_language_score_from_slice_score(doc_result)
        return doc_result
