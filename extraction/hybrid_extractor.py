import os
import spacy

from extraction.regex_engine import *
from extraction.regex_engine_v2 import extract_quantities_v2, extract_cargo_entries_v2, extract_port_pairs_v2
from extraction.knowledge_base import CARGO_KEYWORDS


# Load trained maritime ML model

current_dir = os.path.dirname(__file__)

model_path = os.path.join(
    current_dir,
    "..",
    "maritime_ner_model"
)

nlp = spacy.load(model_path)


def hybrid_extract(text):

    # REGEX EXTRACTION
    regex_data = {

        "cargo": extract_cargo(text),

        "load_port": extract_lp(text),

        "discharge_port": extract_dp(text),

        "dwt": extract_dwt(text),

        "laycan": extract_laycan(text),
        "cargo_entries": extract_cargo_entries_v2(text, CARGO_KEYWORDS),
        "quantity_entries": extract_quantities_v2(text),
        "port_pairs": extract_port_pairs_v2(text),
    }

    # ML ENTITY EXTRACTION
    doc = nlp(text)

    ml_entities = []

    for ent in doc.ents:

        ml_entities.append({

            "text": ent.text,

            "label": ent.label_
        })

    return {

        "regex_extraction": regex_data,

        "ml_entities": ml_entities
    }