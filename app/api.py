"""
API Flask - SocialMetrics AI
Endpoint principal : POST /analyze

Reçoit une liste de tweets (string[]) et retourne un score de sentiment
(entre -1 et 1) pour chacun, au format :
    { "tweet1": score1, "tweet2": score2, ... }
"""
import logging
from flask import Flask, request, jsonify

from app.config import Config
from app.model import SentimentModel
from app import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentiment-api")

app = Flask(__name__)

try:
    model = SentimentModel.load()
    logger.info("Modèle chargé depuis le disque (%s).", Config.MODEL_PATH)
except FileNotFoundError:
    model = None
    logger.warning(
        "Aucun modèle entraîné trouvé. Lance 'python scripts/train_model.py' "
        "avant de démarrer l'API, sinon /analyze renverra une erreur 503."
    )


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Endpoint introuvable."}), 404


@app.errorhandler(405)
def method_not_allowed(_):
    return jsonify({"error": "Méthode HTTP non autorisée pour cet endpoint."}), 405


@app.errorhandler(500)
def internal_error(_):
    return jsonify({"error": "Erreur interne du serveur."}), 500


@app.route("/health", methods=["GET"])
def health():
    """Vérifie que l'API, le modèle et la base de données sont opérationnels."""
    return jsonify(
        {
            "status": "ok",
            "model_loaded": model is not None,
            "database_connected": db.check_connection(),
        }
    )


@app.route("/analyze", methods=["POST"])
def analyze():
    if model is None:
        return jsonify(
            {"error": "Le modèle n'est pas encore entraîné. Contactez l'administrateur."}
        ), 503

    if not request.is_json:
        return jsonify({"error": "Le corps de la requête doit être au format JSON."}), 400

    payload = request.get_json(silent=True)

    tweets = None
    if isinstance(payload, list):
        tweets = payload
    elif isinstance(payload, dict) and "tweets" in payload:
        tweets = payload["tweets"]

    if tweets is None:
        return jsonify(
            {"error": "Format invalide. Attendu : { \"tweets\": [\"...\", \"...\"] } ou [\"...\", \"...\"]."}
        ), 400

    if not isinstance(tweets, list):
        return jsonify({"error": "'tweets' doit être une liste de chaînes de caractères."}), 400

    if len(tweets) == 0:
        return jsonify({"error": "La liste de tweets est vide."}), 400

    if not all(isinstance(t, str) for t in tweets):
        return jsonify({"error": "Chaque élément de la liste doit être une chaîne de caractères."}), 400

    if any(len(t.strip()) == 0 for t in tweets):
        return jsonify({"error": "Un ou plusieurs tweets sont vides ou ne contiennent que des espaces."}), 400

    try:
        scores = model.predict_scores(tweets)
    except Exception as exc:
        logger.exception("Erreur lors de la prédiction : %s", exc)
        return jsonify({"error": "Erreur lors du calcul du score de sentiment."}), 500

    result = {tweet: round(float(score), 4) for tweet, score in zip(tweets, scores)}
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)