import os
import spacy


current_dir = os.path.dirname(__file__)

model_path = os.path.join(
    current_dir,
    "..",
    "maritime_ner_model"
)

nlp = spacy.load(model_path)


text = """
Cargo Corn from Paranagua to Doha
58000 DWT vessel
Laycan 16-20 July
"""


doc = nlp(text)


print("Detected Entities:\n")

for ent in doc.ents:

    print(
        "TEXT:", ent.text,
        "| LABEL:", ent.label_
    )

if len(doc.ents) == 0:

    print("No entities detected")