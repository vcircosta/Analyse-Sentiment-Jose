"""
Script de ré-entraînement automatique du modèle.

Ce script est conçu pour être exécuté une fois par semaine par un cronjob
(voir README.md pour la configuration). Il :
  1. Récupère l'intégralité des tweets annotés disponibles en base MySQL
     (le ré-entraînement se fait sur tout l'historique pour éviter
     l'oubli catastrophique, mais peut être limité aux N derniers jours
     via fetch_recent_tweets si on préfère ne s'adapter qu'aux tendances
     récentes).
  2. Ré-entraîne le modèle de régression logistique.
  3. Sauvegarde le nouveau modèle en écrasant l'ancien.
  4. Journalise l'opération dans logs/retrain.log.

Usage manuel :
    python scripts/retrain.py

Usage via cron (voir README pour la mise en place détaillée) :
    0 3 * * 1 /path/to/venv/bin/python /path/to/project/scripts/retrain.py >> logs/retrain_cron.log 2>&1
"""
import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import db
from app.model import SentimentModel, build_dataframe

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/retrain.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("retrain")


def retrain():
    logger.info("=== Début du ré-entraînement hebdomadaire (%s) ===", datetime.now().isoformat())
    try:
        rows = db.fetch_all_tweets()
        if not rows:
            logger.warning("Aucune donnée disponible en base, ré-entraînement annulé.")
            return False

        df = build_dataframe(rows)
        logger.info("Ré-entraînement sur %d tweets (dont %d nouveaux cette semaine).",
                     len(df), len(db.fetch_recent_tweets(days=7)))

        model = SentimentModel()
        model.fit(df)
        model.save()

        logger.info("Ré-entraînement terminé avec succès. Nouveau modèle sauvegardé.")
        return True
    except Exception as exc:
        logger.exception("Échec du ré-entraînement : %s", exc)
        return False


if __name__ == "__main__":
    success = retrain()
    sys.exit(0 if success else 1)
