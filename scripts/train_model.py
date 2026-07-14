"""
Entraîne le modèle de régression logistique sur les tweets annotés stockés
en base MySQL (table `tweets`), et sauvegarde le modèle + le vectorizer
sur disque (models/).

Si la base MySQL n'est pas accessible (ex. environnement de démo local sans
MySQL), le script utilise automatiquement le CSV de secours
`data/tweets_dataset.csv` généré par `scripts/generate_dataset.py`.

Usage:
    python scripts/train_model.py
"""
import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from app import db
from app.model import SentimentModel, build_dataframe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train_model")

FALLBACK_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "tweets_dataset.csv")


def load_training_data():
    try:
        rows = db.fetch_all_tweets()
        if not rows:
            raise ValueError("La table `tweets` est vide.")
        logger.info("%d tweets chargés depuis MySQL.", len(rows))
        return build_dataframe(rows)
    except Exception as exc:
        logger.warning("Impossible de charger les données depuis MySQL (%s). "
                        "Utilisation du CSV de secours : %s", exc, FALLBACK_CSV)
        df = pd.read_csv(FALLBACK_CSV)
        return build_dataframe(df.to_dict(orient="records"))


def main():
    df = load_training_data()
    logger.info("Distribution des classes :\n%s", df["label"].value_counts())

    model = SentimentModel()
    model.fit(df)
    model.save()
    logger.info("Modèle entraîné et sauvegardé dans models/.")


if __name__ == "__main__":
    main()
