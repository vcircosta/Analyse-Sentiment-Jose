-- ============================================================
-- Script de création de la base de données et de la table tweets
-- SocialMetrics AI - Analyse de sentiments
-- ============================================================

CREATE DATABASE IF NOT EXISTS sentiment_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sentiment_db;

-- Table principale : tweets annotés servant de dataset d'entraînement
CREATE TABLE IF NOT EXISTS tweets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL,
    positive TINYINT(1) NOT NULL DEFAULT 0,
    negative TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Un tweet ne peut pas être à la fois positif ET négatif
    CONSTRAINT chk_sentiment_exclusive CHECK (
        (positive = 1 AND negative = 0) OR
        (positive = 0 AND negative = 1) OR
        (positive = 0 AND negative = 0)  -- tweet neutre
    )
) ENGINE=InnoDB;

-- Index utile pour les requêtes de ré-entraînement (les plus récents)
CREATE INDEX idx_tweets_created_at ON tweets (created_at);

-- (Optionnel) Utilisateur applicatif dédié avec droits restreints
-- CREATE USER IF NOT EXISTS 'sentiment_user'@'%' IDENTIFIED BY 'change_me';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON sentiment_db.tweets TO 'sentiment_user'@'%';
-- FLUSH PRIVILEGES;
