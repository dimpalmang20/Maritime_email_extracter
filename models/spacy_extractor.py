from pathlib import Path

try:
    import spacy
except ModuleNotFoundError:
    spacy = None


def _load_spacy_model():
    if spacy is None:
        return None
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Fallback to local maritime model path if present.
        maritime_model = Path(__file__).resolve().parent.parent / "maritime_ner_model"
        if maritime_model.exists():
            return spacy.load(str(maritime_model))
        # Last-resort fallback keeps pipeline running without hard failure.
        return spacy.blank("en")


nlp = _load_spacy_model()


def extract_entities(text):
    if nlp is None:
        return []

    doc = nlp(text)

    entities = []

    for ent in doc.ents:

        entities.append({
            "text": ent.text,
            "label": ent.label_
        })

    return entities
