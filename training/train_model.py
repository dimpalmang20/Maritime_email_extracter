import random
import spacy

from spacy.training.example import Example

from train_data import TRAIN_DATA


# Create blank English model
nlp = spacy.blank("en")


# Create NER pipeline
if "ner" not in nlp.pipe_names:

    ner = nlp.add_pipe("ner")

else:

    ner = nlp.get_pipe("ner")


# Add labels
for _, annotations in TRAIN_DATA:

    for ent in annotations["entities"]:

        ner.add_label(ent[2])


# Training
optimizer = nlp.begin_training()

for iteration in range(30):

    random.shuffle(TRAIN_DATA)

    losses = {}

    for text, annotations in TRAIN_DATA:

        doc = nlp.make_doc(text)

        example = Example.from_dict(doc, annotations)

        nlp.update(
            [example],
            drop=0.2,
            losses=losses
        )

    print("Iteration:", iteration)
    print("Losses:", losses)


# Save model
nlp.to_disk("maritime_ner_model")

print("MODEL TRAINED SUCCESSFULLY")