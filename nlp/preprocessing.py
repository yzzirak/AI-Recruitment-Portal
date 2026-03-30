"""
preprocessing.py
Step 3 of AI pipeline — NLP text cleaning using spaCy.
Pipeline: lowercase → remove noise → tokenize → remove stopwords → lemmatize
"""
import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
    nlp = spacy.load("en_core_web_sm")


def preprocess_text(text: str) -> str:
    """
    Full NLP preprocessing as described in synopsis methodology:
    1. Lowercase
    2. Remove URLs, emails, phone numbers, special characters
    3. spaCy tokenisation
    4. Stopword removal
    5. Lemmatisation (running→run, companies→company)
    """
    if not text or not text.strip():
        return ""

    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\+?\d[\d\s\-().]{7,}\d", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    doc = nlp(text[:100000])
    tokens = [
        token.lemma_ for token in doc
        if not token.is_stop
        and not token.is_punct
        and not token.is_space
        and len(token.lemma_) > 2
        and token.lemma_.isalpha()
    ]
    return " ".join(tokens)
