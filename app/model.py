import os
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from app.config import Config

CLASSES = ["negative", "neutral", "positive"]


def _rows_to_label(row) -> str:
    if row["positive"] == 1:
        return "positive"
    if row["negative"] == 1:
        return "negative"
    return "neutral"


def build_dataframe(rows) -> pd.DataFrame:
    """Convertit une liste de dicts/tuples (issue de MySQL ou d'un CSV) en DataFrame prêt à l'entraînement."""
    df = pd.DataFrame(rows)
    df["label"] = df.apply(_rows_to_label, axis=1)
    return df


class SentimentModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        self.clf = LogisticRegression(max_iter=1000, class_weight="balanced")
        self.is_fitted = False

    def fit(self, df: pd.DataFrame):
        X = self.vectorizer.fit_transform(df["text"])
        y = df["label"]
        self.clf.fit(X, y)
        self.is_fitted = True
        return self

    def predict_proba_df(self, texts):
        X = self.vectorizer.transform(texts)
        proba = self.clf.predict_proba(X)
        return pd.DataFrame(proba, columns=self.clf.classes_)

    def predict_scores(self, texts):
        """Retourne un score continu entre -1 (très négatif) et 1 (très positif) par texte."""
        proba_df = self.predict_proba_df(texts)
        pos = proba_df.get("positive", pd.Series(np.zeros(len(texts))))
        neg = proba_df.get("negative", pd.Series(np.zeros(len(texts))))
        score = (pos - neg).clip(-1, 1)
        return score.tolist()

    def predict_labels(self, texts):
        X = self.vectorizer.transform(texts)
        return self.clf.predict(X).tolist()

    def save(self, model_path=None, vectorizer_path=None):
        model_path = model_path or Config.MODEL_PATH
        vectorizer_path = vectorizer_path or Config.VECTORIZER_PATH
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(self.clf, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)

    @classmethod
    def load(cls, model_path=None, vectorizer_path=None):
        model_path = model_path or Config.MODEL_PATH
        vectorizer_path = vectorizer_path or Config.VECTORIZER_PATH
        instance = cls()
        instance.clf = joblib.load(model_path)
        instance.vectorizer = joblib.load(vectorizer_path)
        instance.is_fitted = True
        return instance


def train_test_split_df(df: pd.DataFrame, test_size=0.2, random_state=42):
    return train_test_split(
        df, test_size=test_size, random_state=random_state, stratify=df["label"]
    )