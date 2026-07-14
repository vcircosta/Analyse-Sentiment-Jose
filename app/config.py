"""
Configuration centralisée de l'application, chargée depuis les variables
d'environnement (voir .env.example).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "sentiment_db")

    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    MODEL_PATH = os.getenv("MODEL_PATH", "models/sentiment_model.joblib")
    VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", "models/vectorizer.joblib")