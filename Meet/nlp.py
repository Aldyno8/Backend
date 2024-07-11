import spacy
import random
from spacy.training import Example

# Charger le modèle français
nlp = spacy.load('fr_core_news_md')

# Exemples annotés pour l'entraînement
exemples = [
    ("Organise moi une réunion pour discuter des détails de la nouvelle politique de confidentialité demain à 14h",
     {"entities": [(17, 24, "EVENT"), (30, 94, "SUBJECT"), (95, 101, "DATE"), (104, 107, "TIME")]}),
    ("Planifie un meeting avec Dylane pour discuter des nouvelles technologies le 15 août à 14h",
     {"entities": [(12, 19, "EVENT"), (25, 31, "PER"), (37, 72, "SUBJECT"), (76, 83, "DATE"), (86, 89, "TIME")]}),
    ("Prépare une réunion avec Ravaka pour discuter des détails du nouveau projet le 07 juillet à 08h",
    {"entities": [(12, 19, "EVENT"), (25, 31, "PER"), (37, 75, "SUBJECT"), (79, 89, "DATE"), (92, 95, "TIME")]}),
    ("Convoque BEN pour une réunion afin de discuter des détails des nouveaux venus ce 07 Novembre à 08h",
    {"entities": [(9, 12, "PER"), (22, 29, "EVENT"), (38, 77, "SUBJECT"), (81, 92, "DATE"), (95, 98, "TIME")]})
]

# Vérification et ajustement des annotations
for text, annotations in exemples:
    doc = nlp.make_doc(text)
    tags = spacy.training.offsets_to_biluo_tags(doc, annotations['entities'])
    print(f"Text: {text}")
    print(f"BILOU tags: {tags}")

# Ajout des exemples personnalisés dans les exemples d'entraînement de spaCy
training_examples = []
for text, annotations in exemples:
    doc = nlp.make_doc(text)
    example = Example.from_dict(doc, annotations)
    training_examples.append(example)

# Optimiseur pour l'entraînement
optimizer = nlp.resume_training()

# Boucle d'itérations d'entraînement
for i in range(20):
    random.shuffle(training_examples)
    for example in training_examples:
        nlp.update([example], sgd=optimizer)

# Enregistrer le modèle affiné
nlp.to_disk("./spacy_model")

# # Charger le modèle affiné
# nlp = spacy.load("./../nlp")

# # Texte de test pour vérifier le modèle affiné
# text = "Organise moi une réunion avec Jonathan et Xav pour discuter des détails de la logique de l'application demain à 14h"

# doc = nlp(text)

# # Afficher les entités reconnues et leurs étiquettes
# for ent in doc.ents:
#     print(f"{ent.text}: {ent.label_}")
