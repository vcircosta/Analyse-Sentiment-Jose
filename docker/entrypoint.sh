#!/bin/sh
set -e

echo "[entrypoint] Attente de MySQL..."
python -c "
import time
from app import db

for i in range(30):
    if db.check_connection():
        print('[entrypoint] MySQL disponible.')
        break
    print('[entrypoint] MySQL indisponible, nouvelle tentative (%d/30)...' % (i + 1))
    time.sleep(2)
else:
    raise SystemExit('[entrypoint] MySQL injoignable apres 60s.')
"

if [ ! -f data/tweets_dataset.csv ]; then
  echo "[entrypoint] Generation du dataset de demonstration..."
  python scripts/generate_dataset.py
fi

echo "[entrypoint] Verification du contenu de la table tweets..."
if python -c "
from app import db
raise SystemExit(0 if db.fetch_all_tweets() else 1)
"; then
  echo "[entrypoint] Table tweets deja peuplee, seed ignore."
else
  echo "[entrypoint] Table tweets vide, chargement du dataset..."
  python scripts/seed_db.py
fi

if [ ! -f models/sentiment_model.joblib ] || [ ! -f models/vectorizer.joblib ]; then
  echo "[entrypoint] Entrainement initial du modele..."
  python scripts/train_model.py
else
  echo "[entrypoint] Modele deja present, entrainement ignore."
fi

echo "[entrypoint] Demarrage de l'API Flask..."
exec python -m app.api
