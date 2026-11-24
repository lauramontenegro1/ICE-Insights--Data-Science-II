"""
TaskBridge - second cleaning: text standardization

clean_text : clean text, but with capital letters, accents and ponctuation 
match_key  : comparing key for text comparison, normalized text
"""
import re
import unicodedata
import pandas as pd

_INVISIBLE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff\u00ad]")   # zero-width, soft hyphen
_DASHES    = re.compile(r"[\u2010\u2011\u2012\u2013\u2014\u2212]")   # ‐ ‑ ‒ – — −
_QUOTES_S  = re.compile(r"[\u2018\u2019\u201a\u00b4`]")              # ‘ ’ ‚ ´ `
_QUOTES_D  = re.compile(r"[\u201c\u201d\u201e]")                     # “ ” „

def _nfkc(x):
    return unicodedata.normalize("NFKC", x) if pd.notna(x) else x    # ﬁ->fi, nbsp->espaço

#keep capital letters, accents and ponctuation
def clean_text(s: pd.Series) -> pd.Series:
    s = s.astype("string").map(_nfkc).astype("string")
    s = s.str.replace(_INVISIBLE, "", regex=True)
    s = s.str.replace(_DASHES, "-", regex=True)
    s = s.str.replace(_QUOTES_S, "'", regex=True).str.replace(_QUOTES_D, '"', regex=True)
    return s.str.replace(r"\s+", " ", regex=True).str.strip()

def _strip_accents(x):
    if pd.isna(x):
        return x
    return "".join(c for c in unicodedata.normalize("NFKD", x) if not unicodedata.combining(c))

#normalized text
def match_key(s: pd.Series) -> pd.Series:
    s = clean_text(s).str.casefold()                      # casefold: ß -> ss
    s = s.map(_strip_accents).astype("string")
    s = s.str.replace(r"[^\w\s+#.\-/]", " ", regex=True)  # remove ( ) , ; : ! etc.
    s = s.str.replace(r"\.+$", "", regex=True)            # final point
    return s.str.replace(r"\s+", " ", regex=True).str.strip()