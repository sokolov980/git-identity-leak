from collections import Counter
from schemas import Signal
import re

def analyze_stylometry(signals: list[Signal]):
    """
    Basic textual fingerprinting from posts.
    """
    word_counter = Counter()
    for s in signals:
        if s.type == "post":
            words = re.findall(r"\w+", s.value.lower())
            word_counter.update(words)
    return {
        "top_words": word_counter.most_common(20),
        "note": "Experimental; do not rely solely on this for identity."
    }
