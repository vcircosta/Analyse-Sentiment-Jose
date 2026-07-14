"""
Génère un jeu de données synthétique de tweets annotés (positive/negative)
pour alimenter la table `tweets` et permettre l'entraînement / évaluation
du modèle de régression logistique.

Usage:
    python scripts/generate_dataset.py
"""
import csv
import random

random.seed(42)

POSITIVE_TEMPLATES = [
    "J'adore {sujet}, c'est vraiment {adj_pos} !",
    "{sujet} est incroyable, je suis {adj_pos} aujourd'hui",
    "Quelle {adj_pos} journée grâce à {sujet} !",
    "Je recommande {sujet} à 100%, {adj_pos} expérience",
    "Merci à {sujet}, vous êtes {adj_pos}",
    "{sujet} a dépassé mes attentes, {adj_pos} !",
    "Trop content d'avoir découvert {sujet}, {adj_pos}",
    "{sujet} rend ma vie tellement plus {adj_pos}",
    "Bravo à toute l'équipe de {sujet}, travail {adj_pos}",
    "Je ne pensais pas que {sujet} serait aussi {adj_pos}",
]

NEGATIVE_TEMPLATES = [
    "Je déteste {sujet}, c'est vraiment {adj_neg}",
    "{sujet} est {adj_neg}, quelle déception",
    "Encore un problème avec {sujet}, {adj_neg}",
    "Je ne recommande pas {sujet}, service {adj_neg}",
    "{sujet} m'a mis en colère, expérience {adj_neg}",
    "Plus jamais {sujet}, c'est {adj_neg}",
    "{sujet} ne fonctionne pas, {adj_neg} comme d'habitude",
    "Franchement {sujet} est {adj_neg}, évitez",
    "Quelle {adj_neg} surprise avec {sujet}",
    "{sujet} a ruiné ma journée, {adj_neg}",
]

NEUTRAL_TEMPLATES = [
    "{sujet} a publié une mise à jour aujourd'hui.",
    "Quelqu'un a des infos sur {sujet} ?",
    "{sujet} sera disponible la semaine prochaine.",
    "Article intéressant sur {sujet}, à lire.",
    "Réunion prévue concernant {sujet} demain.",
]

SUJETS = [
    "ce produit", "le nouveau service client", "l'application mobile",
    "la livraison", "le restaurant du coin", "cette série", "le dernier film",
    "ce concert", "l'équipe support", "le site web", "la nouvelle mise à jour",
    "ce jeu vidéo", "l'hôtel", "ce vol Air France", "la formation en ligne",
    "ce livre", "la conférence", "le stade", "cette voiture", "le smartphone",
]

ADJ_POS = ["génial", "excellent", "fantastique", "super", "parfait", "magnifique", "top", "incroyable"]
ADJ_NEG = ["nul", "catastrophique", "décevant", "horrible", "médiocre", "lamentable", "affreux", "pénible"]

# Tweets ambigus / sarcastiques volontairement difficiles pour le modèle :
# vocabulaire positif employé dans un sens négatif (sarcasme), négations,
# et phrases mitigées. Cela reproduit les biais réels observés sur des
# tweets (le modèle "bag of words" a du mal à capter la négation/l'ironie).
AMBIGUOUS_NEGATIVE = [
    "Génial, encore un retard de {sujet}, bravo l'équipe",
    "Super, {sujet} qui plante encore une fois",
    "Magnifique, j'attends {sujet} depuis 3 heures",
    "Pas terrible {sujet}, je m'attendais à mieux",
    "{sujet} n'est pas vraiment top finalement",
    "Franchement pas convaincu par {sujet}",
    "{sujet}... on a vu mieux",
]

AMBIGUOUS_POSITIVE = [
    "Pas mal du tout {sujet}, plutôt agréable surprise",
    "{sujet} n'est pas parfait mais franchement pas mal",
    "Rien à redire sur {sujet}, ça fait le job",
    "{sujet} sans être exceptionnel reste correct",
]

# Fautes de frappe / abréviations typiques des réseaux sociaux
TYPO_SUFFIXES = ["", " mdr", " ptdr", " svp", "...", " !!", " :)", " :("]


def _add_typo_noise(text):
    if random.random() < 0.35:
        text = text + random.choice(TYPO_SUFFIXES)
    return text


def generate_rows(n_positive=110, n_negative=90, n_neutral=45,
                   n_ambiguous_negative=35, n_ambiguous_positive=25):
    rows = []
    for _ in range(n_positive):
        tpl = random.choice(POSITIVE_TEMPLATES)
        text = tpl.format(sujet=random.choice(SUJETS), adj_pos=random.choice(ADJ_POS))
        rows.append((_add_typo_noise(text), 1, 0))
    for _ in range(n_negative):
        tpl = random.choice(NEGATIVE_TEMPLATES)
        text = tpl.format(sujet=random.choice(SUJETS), adj_neg=random.choice(ADJ_NEG))
        rows.append((_add_typo_noise(text), 0, 1))
    for _ in range(n_neutral):
        tpl = random.choice(NEUTRAL_TEMPLATES)
        text = tpl.format(sujet=random.choice(SUJETS))
        rows.append((_add_typo_noise(text), 0, 0))
    # Tweets étiquetés "negative" mais contenant du vocabulaire positif (sarcasme)
    for _ in range(n_ambiguous_negative):
        tpl = random.choice(AMBIGUOUS_NEGATIVE)
        text = tpl.format(sujet=random.choice(SUJETS))
        rows.append((_add_typo_noise(text), 0, 1))
    # Tweets étiquetés "positive" mais au ton mesuré / avec négation
    for _ in range(n_ambiguous_positive):
        tpl = random.choice(AMBIGUOUS_POSITIVE)
        text = tpl.format(sujet=random.choice(SUJETS))
        rows.append((_add_typo_noise(text), 1, 0))
    random.shuffle(rows)
    return rows


def inject_label_noise(rows, noise_rate=0.06):
    """
    Simule des erreurs d'annotation humaine (~6%) : un annotateur pressé qui
    se trompe parfois de case. C'est un phénomène courant et documenté dans
    les datasets de sentiment réels, et cela évite au modèle d'atteindre un
    score de 100% totalement artificiel.
    """
    noisy_rows = []
    for text, positive, negative in rows:
        if random.random() < noise_rate:
            # Inverse ou neutralise l'étiquette
            choice = random.choice(["flip", "neutral"])
            if choice == "flip":
                positive, negative = negative, positive
            else:
                positive, negative = 0, 0
        noisy_rows.append((text, positive, negative))
    return noisy_rows


if __name__ == "__main__":
    rows = generate_rows()
    rows = inject_label_noise(rows)
    with open("data/tweets_dataset.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "positive", "negative"])
        writer.writerows(rows)
    print(f"{len(rows)} tweets générés dans data/tweets_dataset.csv")
