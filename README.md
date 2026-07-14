# SocialMetrics AI — API d'Analyse de Sentiments

## Équipe **WEVL** : 
- Luciano FERREIRA 
- Elise LABARRERE 
- Valentin CIRCOSTA 
- William LE GAVRIAN

## Lancer le projet

Prérequis : Docker et Docker Compose.

```bash
docker compose up --build
```

Cette seule commande crée la base MySQL, entraîne le modèle et démarre
l'API sur `http://localhost:5000`.

## Utilisation

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"tweets": ["Super produit !", "Vraiment déçu du service"]}'
```
