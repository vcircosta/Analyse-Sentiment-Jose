"""
Gestion de la connexion et des requêtes vers la base de données MySQL
contenant la table `tweets` (dataset annoté).
"""
import mysql.connector
from mysql.connector import Error
from app.config import Config


def get_connection():
    """Ouvre et retourne une nouvelle connexion MySQL."""
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
    )


def fetch_all_tweets():
    """Récupère tous les tweets annotés de la table `tweets`."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, text, positive, negative, created_at FROM tweets")
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def fetch_recent_tweets(days=7):
    """Récupère les tweets ajoutés dans les `days` derniers jours (pour le ré-entraînement)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, text, positive, negative, created_at FROM tweets "
            "WHERE created_at >= NOW() - INTERVAL %s DAY",
            (days,),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def insert_tweet(text: str, positive: int, negative: int):
    """Insère un tweet annoté dans la table `tweets`."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tweets (text, positive, negative) VALUES (%s, %s, %s)",
            (text, positive, negative),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def insert_tweets_bulk(rows):
    """
    Insère plusieurs tweets annotés en une seule transaction.
    `rows` est une liste de tuples (text, positive, negative).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO tweets (text, positive, negative) VALUES (%s, %s, %s)",
            rows,
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def check_connection() -> bool:
    """Vérifie que la connexion à MySQL fonctionne (utilisé par /health)."""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Error:
        return False