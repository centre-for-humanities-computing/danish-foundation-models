"""
Type stub for kenlm
"""

class Model:
    def __init__(self, model_bin_path: str) -> None: ...
    def score(self, sentence: str) -> float: ...
