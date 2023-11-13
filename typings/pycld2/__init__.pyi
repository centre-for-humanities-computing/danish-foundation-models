"""
Type stub file for pycld2
"""

from typing import Union, TypeAlias

from pycld2 import DETECTED_LANGUAGES, ENCODINGS, LANGUAGES, VERSION, __version__, error

IsReliable: TypeAlias = bool
TextBytesFound: TypeAlias = int
DetectDetails: TypeAlias = tuple[tuple[str, str, int, float], ...]
Vectors: TypeAlias = tuple[tuple[int, int, str, str], ...]

def detect(
    text: str, returnVectors: bool = False
) -> Union[
    tuple[IsReliable, TextBytesFound, DetectDetails],
    tuple[IsReliable, TextBytesFound, DetectDetails, Vectors],
]: ...

__all__ = ("DETECTED_LANGUAGES", "ENCODINGS", "LANGUAGES", "VERSION", "detect", "error")
