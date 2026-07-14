"""
Alternative au cronjob système : planifie le ré-entraînement hebdomadaire
directement en Python grâce à la librairie `schedule`.

Utile sur les environnements où l'on ne peut pas configurer de crontab
(ex. certains PaaS). À lancer en tâche de fond (ex. via systemd, supervisor,
ou simplement `nohup python scripts/scheduler.py &`).

Usage:
    python scripts/scheduler.py
"""
import time
import schedule

from retrain import retrain  # noqa: E402

# Tous les lundis à 3h du matin
schedule.every().monday.at("03:00").do(retrain)

if __name__ == "__main__":
    print("Planificateur démarré : ré-entraînement chaque lundi à 03:00.")
    while True:
        schedule.run_pending()
        time.sleep(60)
