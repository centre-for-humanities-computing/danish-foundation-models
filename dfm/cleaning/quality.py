from typing import List
from nltk import word_tokenize

class GopherFilter():
    """Danish implementation of quality filter described in the paper:
     "Scaling Language Models: Methods, Analysis & Insights from Training Gopher"
     link: https://arxiv.org/abs/2112.11446
    """
    
    def __init__(self):
        self.stop_words = [
            'er', 'jeg', 'det', 'du', 'ikke', 'at',
            'en', 'og', 'har', 'vi', 'til', 'på', 
            'hvad', 'mig', 'med', 'de', 'for', 'den',
            'så', 'der', 'dig', 'han', 'kan', 'af'
        ]


    
    def __call__(self, doc: str) -> bool:
        
        tokens = self.word_tokenize(doc) # bottleneck

        # doc len filter
        if not 50 <= len(doc) <= 100000:
            return False

        # mean word lenght filter
        mwl = self.mean_word_length(tokens)
        if not 3 <= mwl <= 10:
            return False
        
        # hash2word + ellipsis2word filter (wierd filter?)
        h2w = self.hash2word_ratio(tokens)
        e2w = self.ellip2word_ratio(tokens)
        if (h2w > 0.1) | (e2w > 0.1):
            return False
        
        # less than 90% lines start with bulletpoint filter (not implemented)
        
        # less than 30% lines end with ellipsis filter (not implemented)
        
        # min 80% of word contain 1 alphabetic char 
        alph = self.alpha_check(tokens)
        if not alph >= 0.8:
            return False
        
        # stop word filter
        if not self.stop_word_check(doc):
            return False
        
        return True
        
    
    def word_tokenize(self, doc: str) -> List[str]:
        return word_tokenize(doc, language='danish')
    
    def mean_word_length(self, tokens: List[str]) -> float:
        return sum([len(word) for word in tokens])/len(tokens)
    
    def hash2word_ratio(self, tokens: List[str]) -> float:
        n_hash, n_word = 0, 0
        for token in tokens:
            if token.isalpha():
                n_word += 1
            if '#' in token:
                n_hash += 1
        h2w = n_hash / n_word if n_word != 0 else 1
        return h2w
    
    def ellip2word_ratio(self, tokens: List[str]) -> float:
        n_ellip, n_word = 0, 0
        for token in tokens:
            if token.isalpha():
                n_word += 1
            if '…' in token:
                n_ellip += 1
        e2w = n_ellip / n_word if n_word != 0 else 1
        return e2w
    
    def alpha_check(self, tokens: List[str]) -> float:
        n_alpha = 0
        for t in tokens:
            for c in t:
                if c.isalpha():
                    n_alpha += 1
                    break
        return n_alpha / len(tokens)
    
    def stop_word_check(self, doc: str) -> bool:
        cnt = 0
        for w in self.stop_words:
            w = ' '+w+' '
            if w in doc:
                cnt += 1
            if cnt == 2:
                return True
        return False
        