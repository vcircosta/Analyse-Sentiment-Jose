"""
Évalue le modèle : split train/validation, calcule les matrices de
confusion (positive et negative) ainsi que précision/rappel/F1, et
sauvegarde les figures dans reports/.

Usage:
    python scripts/evaluate.py
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, classification_report

from app.model import SentimentModel, build_dataframe, train_test_split_df
from app import db

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
FALLBACK_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "tweets_dataset.csv")
os.makedirs(REPORTS_DIR, exist_ok=True)


def load_data():
    try:
        rows = db.fetch_all_tweets()
        if not rows:
            raise ValueError("table vide")
        return build_dataframe(rows)
    except Exception:
        df = pd.read_csv(FALLBACK_CSV)
        return build_dataframe(df.to_dict(orient="records"))


def plot_confusion(cm, labels, title, filename):
    plt.figure(figsize=(4.5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels, cbar=False)
    plt.title(title)
    plt.xlabel("Prédiction")
    plt.ylabel("Réalité")
    plt.tight_layout()
    path = os.path.join(REPORTS_DIR, filename)
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def main():
    df = load_data()
    train_df, val_df = train_test_split_df(df, test_size=0.25)

    model = SentimentModel()
    model.fit(train_df)

    y_true = val_df["label"].tolist()
    y_pred = model.predict_labels(val_df["text"].tolist())

    # --- Matrice de confusion binaire : "positive" vs "reste"
    y_true_pos = ["positive" if l == "positive" else "autre" for l in y_true]
    y_pred_pos = ["positive" if l == "positive" else "autre" for l in y_pred]
    cm_pos = confusion_matrix(y_true_pos, y_pred_pos, labels=["positive", "autre"])
    plot_confusion(cm_pos, ["positive", "autre"], "Matrice de confusion - Positive", "confusion_matrix_positive.png")

    # --- Matrice de confusion binaire : "negative" vs "reste"
    y_true_neg = ["negative" if l == "negative" else "autre" for l in y_true]
    y_pred_neg = ["negative" if l == "negative" else "autre" for l in y_pred]
    cm_neg = confusion_matrix(y_true_neg, y_pred_neg, labels=["negative", "autre"])
    plot_confusion(cm_neg, ["negative", "autre"], "Matrice de confusion - Negative", "confusion_matrix_negative.png")

    # --- Métriques par classe (positive / negative / neutral)
    labels_order = ["positive", "negative", "neutral"]
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels_order, zero_division=0
    )

    metrics = {
        lbl: {
            "precision": round(float(p), 3),
            "recall": round(float(r), 3),
            "f1_score": round(float(f), 3),
            "support": int(s),
        }
        for lbl, p, r, f, s in zip(labels_order, precision, recall, f1, support)
    }

    report_text = classification_report(y_true, y_pred, labels=labels_order, zero_division=0)
    print(report_text)

    with open(os.path.join(REPORTS_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    with open(os.path.join(REPORTS_DIR, "classification_report.txt"), "w", encoding="utf-8") as f:
        f.write(report_text)

    print("\nMatrices de confusion et métriques sauvegardées dans reports/.")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
