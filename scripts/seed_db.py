"""
Charge le CSV data/tweets_dataset.csv dans la table MySQL `tweets`.

Prérequis : avoir exécuté scripts/setup_db.sql puis
scripts/generate_dataset.py (ou disposer de son propre CSV annoté avec les
colonnes text, positive, negative).

Usage:
    python scripts/seed_db.py
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from app import db

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tweets_dataset.csv")


def main():
    df = pd.read_csv(CSV_PATH)
    rows = list(df[["text", "positive", "negative"]].itertuples(index=False, name=None))
    inserted = db.insert_tweets_bulk(rows)
    print(f"{inserted} tweets insérés dans la table `tweets`.")


if __name__ == "__main__":
    main()
