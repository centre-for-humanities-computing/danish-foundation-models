"""

Filters.

"""
from collections.abc import Iterable
from typing import TYPE_CHECKING

import necessary
import pycld2 as cld2
import regex
from anyascii import anyascii
from dolma.core.data_types import DocResult, Document, Span, TextSlice
from dolma.core.ft_tagger import BaseFastTextTagger, Prediction
from dolma.core.registry import TaggerRegistry
from dolma.core.taggers import BaseTagger
from dolma.core.utils import split_paragraphs

with necessary.necessary("cld3", soft=True) as CLD3_AVAILABLE:
    if CLD3_AVAILABLE or TYPE_CHECKING:
        import cld3  # pyright:ignore pylint:disable=import-error


@TaggerRegistry.add("cld3_da_doc_v2")
class Cld3LanguageTaggerDa(BaseTagger):
    def __init__(self) -> None:
        if not CLD3_AVAILABLE:
            raise ImportError(
                f"cld3 is not install, cannot instantiate {self.__class__.__name__}"
            )

    def _predict_text(self, text: str) -> tuple[str, float]:
        pred = cld3.get_language(text)  # pyright: ignore
        score = pred.probability if pred.language == "da" else 0.0
        return "da", score

    def predict(self, doc: Document) -> DocResult:
        lang, score = self._predict_text(doc.text)
        positive_span = Span(start=0, end=len(doc.text), type=lang, score=score)
        negative_span = Span(
            start=0, end=len(doc.text), type=f"not_{lang}", score=1.0 - score
        )
        return DocResult(doc=doc, spans=[positive_span, negative_span])


@TaggerRegistry.add("cld3_da_paragraph_v2")
class Cld3LanguageTaggerParagraphDa(Cld3LanguageTaggerDa):
    def predict(self, doc: Document) -> DocResult:
        paragraphs = split_paragraphs(doc.text)
        spans: list[Span] = []
        for paragraph in paragraphs:
            lang, score = self._predict_text(paragraph.text)  # pyright: ignore
            positive_span = Span(
                start=paragraph.start, end=paragraph.end, type=lang, score=score
            )
            negative_span = Span(
                start=paragraph.start,
                end=paragraph.end,
                type=f"not_{lang}",
                score=1.0 - score,
            )
            spans.extend((positive_span, negative_span))
        return DocResult(doc=doc, spans=spans)


@TaggerRegistry.add("cld2_da_doc_v2")
class Cld2LanguageFilterDa(BaseTagger):
    RE_BAD_CHARS = regex.compile(r"[\p{Cc}\p{Cs}]+")

    def _sanitize_input(self, text: str) -> str:
        return self.RE_BAD_CHARS.sub("", text)

    def _to_ascii_input(self, text: str) -> str:
        return anyascii(text)

    def _identity_fn(self, text: str) -> str:
        return text

    def _predict_text(self, text: str) -> tuple[str, float]:
        details = []
        is_reliable = False
        for fn in (self._identity_fn, self._to_ascii_input, self._sanitize_input):
            try:
                is_reliable, _, details = cld2.detect(fn(text))
                break
            except cld2.error:
                ...

        score = max([d[2] for d in details if d[0] == "DANISH" and is_reliable] or [0])
        return "da", score / 100.0

    def predict(self, doc: Document) -> DocResult:
        lang, score = self._predict_text(doc.text)
        positive_span = Span(start=0, end=len(doc.text), type=lang, score=score)
        negative_span = Span(
            start=0, end=len(doc.text), type=f"not_{lang}", score=1.0 - score
        )
        return DocResult(doc=doc, spans=[positive_span, negative_span])


@TaggerRegistry.add("cld2_da_paragraph_v2")
class Cld2LanguageFilterParagraphDa(Cld2LanguageFilterDa):
    def predict(self, doc: Document) -> DocResult:
        paragraphs = split_paragraphs(doc.text)
        spans: list[Span] = []
        for paragraph in paragraphs:
            lang, score = self._predict_text(paragraph.text)  # pyright: ignore
            positive_span = Span(
                start=paragraph.start, end=paragraph.end, type=lang, score=score
            )
            negative_span = Span(
                start=paragraph.start,
                end=paragraph.end,
                type=f"not_{lang}",
                score=1.0 - score,
            )
            spans.extend((positive_span, negative_span))
        return DocResult(doc=doc, spans=spans)


@TaggerRegistry.add("ft_lang_id_da_doc_v2")
class FastTextDanishLanguageDocumentTagger(BaseFastTextTagger):
    MODEL_PATH = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"

    def __init__(self):
        super().__init__(
            model_path=self.MODEL_PATH, model_mode=self.DOCUMENT_LEVEL_TAGGER
        )

    def predict_slice(self, text_slice: TextSlice) -> Iterable[Prediction]:
        pred = self.classifier.predict(
            text_slice.text.lower().replace("\n", " ").strip(), k=-1
        )
        for label, score in zip(*pred):
            if label == "__label__da":
                return Prediction(label="da", score=score), Prediction(
                    label="not_da", score=1.0 - score
                )
        return Prediction(label="da", score=0.0), Prediction(label="not_da", score=1.0)


@TaggerRegistry.add("ft_lang_id_da_paragraph_v2")
class FastTextDanishLanguageParagraphTagger(FastTextDanishLanguageDocumentTagger):
    def __init__(self):
        BaseFastTextTagger.__init__(
            self, model_path=self.MODEL_PATH, model_mode=self.PARAGRAPH_LEVEL_TAGGER
        )


def add_global_language_score_from_slice_score_da(result: DocResult) -> DocResult:
    # the total document score is # of characters in each "danish" span multiplied by the likelihood
    # of said span being danish
    try:
        doc_da_score = sum(
            (s.end - s.start) * s.score for s in result.spans if s.type == "da"
        ) / len(
            result.doc.text,
        )
        doc_not_da_score = 1 - doc_da_score
    except ZeroDivisionError:
        doc_da_score = doc_not_da_score = 0.0

    doc_level = (
        Span(start=0, end=len(result.doc.text), type="doc_da", score=doc_da_score),
        Span(
            start=0, end=len(result.doc.text), type="doc_not_da", score=doc_not_da_score
        ),
    )
    result.spans.extend(doc_level)
    return result


@TaggerRegistry.add("cld2_da_paragraph_with_doc_score_v2")
class Cld2LanguageFilterParagraphWithDocScoreTaggerDa(Cld2LanguageFilterParagraphDa):
    def predict(self, doc: Document) -> DocResult:
        doc_result = super().predict(doc)
        doc_result = add_global_language_score_from_slice_score_da(doc_result)
        return doc_result


@TaggerRegistry.add("cld3_da_paragraph_with_doc_score_v2")
class Cld3LanguageFilterParagraphWithDocScoreTaggerDa(Cld3LanguageTaggerParagraphDa):
    def predict(self, doc: Document) -> DocResult:
        doc_result = super().predict(doc)
        doc_result = add_global_language_score_from_slice_score_da(doc_result)
        return doc_result


@TaggerRegistry.add("ft_lang_id_da_paragraph_with_doc_score_v2")
class FastTextDanishLanguageParagraphWithDocScoreTagger(
    FastTextDanishLanguageParagraphTagger
):
    def predict(self, doc: Document) -> DocResult:
        doc_result = super().predict(doc)
        doc_result = add_global_language_score_from_slice_score_da(doc_result)
        return doc_result
