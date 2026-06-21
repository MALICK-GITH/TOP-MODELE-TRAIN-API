# FIFA Virtual Prediction API

API REST pour les prédictions de matchs FIFA virtuels avec règles de cohérence globale et système d'historique.

## 📋 Table des matières

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Endpoints API](#endpoints-api)
- [Système d'historique](#système-dhistorique)
- [Déploiement](#déploiement)
- [Familles de ligues](#familles-de-ligues)
- [Règles de cohérence](#règles-de-cohérence)

---

## Overview

Cette API fournit des prédictions pour les matchs FIFA virtuels en utilisant des modèles de machine learning entraînés sur des données historiques. Elle supporte plusieurs familles de ligues avec des caractéristiques différentes (Penalty, Highscore, Rush, Classic).

### Fonctionnalités principales

- **Prédictions multi-tâches** : Résultat (1X2), Total buts, Pair/Impair, Score exact
- **Règles de cohérence** : Garantit la cohérence entre les différentes prédictions
- **Système d'historique** : Met à jour les statistiques des équipes en temps réel
- **Cache Upstash** : Optimisation des performances avec cache Redis
- **Multi-familles** : Supporte 4 familles de ligues avec des profils différents

---

## Architecture

### Structure du projet

```
TRAIN CSV MODELE FIFA/
├── api.py                      # API FastAPI principale
├── train_random_forest.py      # Pipeline d'entraînement et ModelLoader
├── models.py                   # Classes de modèles ML (PoissonScoreModel)
├── upstash_cache.py            # Cache Upstash Redis
├── finished_matches.csv       # Données d'entraînement
├── models/                     # Modèles entraînés par famille
│   ├── PENALTY/
│   ├── HIGHSCORE/
│   ├── RUSH/
│   └── CLASSIC/
├── requirements.txt            # Dépendances Python
└── render.yaml                 # Configuration Render
```

### Composants principaux

1. **ModelLoader** : Charge et gère tous les modèles au démarrage
2. **PoissonScoreModel** : Modèle de Poisson pour les scores exacts
3. **Système d'historique** : Met à jour les statistiques des équipes
4. **Règles de cohérence** : Applique 5 règles de validation globale

---

## Installation

### Prérequis

- Python 3.9+
- pip

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Dépendances principales

```
fastapi==0.104.1
uvicorn==0.24.0
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
scipy==1.11.4
joblib==1.3.2
requests==2.31.0
upstash-redis==1.0.0
```

---

## Configuration

### Variables d'environnement

Créer un fichier `.env` :

```env
# Upstash Redis (optionnel)
UPSTASH_REDIS_REST_URL=https://your-rest-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-token
```

### Configuration Render

Le fichier `render.yaml` configure le déploiement sur Render :

```yaml
services:
  - type: web
    name: fifa-prediction-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api:app --host 0.0.0.0 --port 8000
```

---

## Endpoints API

### Base URL

```
https://your-api.onrender.com
```

### Health Check

```http
GET /health
```

**Response :**

```json
{
  "status": "healthy",
  "models_loaded": true,
  "families": ["PENALTY", "HIGHSCORE", "RUSH", "CLASSIC"]
}
```

### Prédiction de match

```http
POST /predict
Content-Type: application/json

{
  "team_home": "Real Madrid",
  "team_away": "Barcelona",
  "league": "FC 25. Champions League"
}
```

**Response :**

```json
{
  "match": "Real Madrid vs Barcelona",
  "league": "FC 25. Champions League",
  "family": "CLASSIC",
  "predictions": {
    "1x2": {
      "home": 0.450,
      "draw": 0.300,
      "away": 0.250
    },
    "total_goals": {
      "predicted": 2.5,
      "over_under": {
        "2.5": {"over": 0.600, "under": 0.400},
        "3.5": {"over": 0.350, "under": 0.650}
      }
    },
    "handicap": {
      "-1.0": {"home": 0.250, "draw": 0.200, "away": 0.550},
      "1.0": {"home": 0.650, "draw": 0.200, "away": 0.150}
    },
    "parity": {
      "pair": 0.550,
      "impair": 0.450
    },
    "exact_score": {
      "prediction": "1-1"
    }
  },
  "history": {
    "home_last_matches": [...],
    "home_stats": {...},
    "away_last_matches": [...],
    "away_stats": {...}
  }
}
```

### Mise à jour de l'historique

```http
POST /update-history
Content-Type: application/json

{
  "team_home": "Real Madrid",
  "team_away": "Barcelona",
  "league": "FC 25. Champions League",
  "score_home": 2,
  "score_away": 1,
  "finished_at": "2024-01-15T20:00:00Z"
}
```

**Response :**

```json
{
  "status": "success",
  "message": "Historique mis à jour"
}
```

### Sauvegarde de l'historique

```http
POST /save-history?family=CLASSIC
```

**Response :**

```json
{
  "status": "success",
  "message": "Historique sauvegardé"
}
```

### Nettoyage du cache

```http
POST /clear-cache
```

**Response :**

```json
{
  "status": "success",
  "message": "Cache nettoyé"
}
```

### Lister les familles

```http
GET /families
```

**Response :**

```json
{
  "families": {
    "PENALTY": {
      "pattern": "Penalty|penalty",
      "has_draw": false,
      "typical_goals": [3, 15],
      "description": "Séances de tirs au but — 2 issues possibles, scores élevés"
    },
    ...
  }
}
```

### Lister les ligues d'une famille

```http
GET /leagues/CLASSIC
```

**Response :**

```json
{
  "family": "CLASSIC",
  "leagues": [
    "FC 25. Championnat d'Angleterre",
    "FC 25. Champions League",
    ...
  ]
}
```

---

## Système d'historique

### Fonctionnement

Le système d'historique permet de mettre à jour les statistiques des équipes en temps réel avec les résultats des matchs terminés.

### Fonctions disponibles

#### `update_history(match_data)`

Met à jour l'historique avec un match terminé.

**Paramètres :**

```python
{
    "team_home": str,      # Équipe domicile
    "team_away": str,      # Équipe extérieur
    "league": str,         # Nom de la ligue
    "score_home": int,     # Score domicile
    "score_away": int,     # Score extérieur
    "finished_at": str,   # Date de fin (ISO8601)
    "family": str (optionnel)  # Famille (auto-détectée si non fournie)
}
```

#### `get_team_last_matches(team, league, limit=5)`

Récupère les derniers matchs d'une équipe avec statistiques.

**Retourne :**

```python
{
    "matches": [
        {
            "opponent": str,
            "score_home": int,
            "score_away": int,
            "result": str,  # "H", "D", "A"
            "finished_at": str
        },
        ...
    ],
    "stats": {
        "matches_played": int,
        "wins": int,
        "draws": int,
        "losses": int,
        "goals_for": float,
        "goals_against": float,
        "win_rate": float
    }
}
```

#### `get_head_to_head(team_home, team_away, league, limit=5)`

Récupère les confrontations directes entre deux équipes.

**Retourne :** Liste des matchs précédents entre les deux équipes.

#### `save_history(family=None)`

Sauvegarde l'historique mis à jour sur disque.

**Paramètres :**
- `family` : Si spécifié, sauvegarde seulement cette famille. Sinon, sauvegarde toutes les familles.

### Utilisation via API

```bash
# Mettre à jour l'historique après un match
curl -X POST https://your-api.onrender.com/update-history \
  -H "Content-Type: application/json" \
  -d '{
    "team_home": "Real Madrid",
    "team_away": "Barcelona",
    "league": "FC 25. Champions League",
    "score_home": 2,
    "score_away": 1,
    "finished_at": "2024-01-15T20:00:00Z"
  }'

# Sauvegarder l'historique
curl -X POST https://your-api.onrender.com/save-history?family=CLASSIC
```

---

## Déploiement

### Déploiement local

```bash
# Lancer l'API localement
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Déploiement sur Render

1. **Créer un compte Render** : https://render.com

2. **Créer un nouveau Web Service** :
   - Connecter votre repository GitHub
   - Sélectionner le dossier du projet
   - Render utilisera automatiquement `render.yaml`

3. **Configurer les variables d'environnement** :
   - `UPSTASH_REDIS_REST_URL` (optionnel)
   - `UPSTASH_REDIS_REST_TOKEN` (optionnel)

4. **Déployer** : Render déploiera automatiquement

### Redémarrage du service

Utiliser le script `control_render.py` :

```bash
python control_render.py
```

Options :
1. Lister les services
2. Redémarrer un service
3. Déployer un service
4. Quitter

---

## Familles de ligues

### PENALTY

**Pattern :** `Penalty|penalty`

**Caractéristiques :**
- Pas de match nul (has_draw: false)
- Scores élevés (typical_goals: 3-15)
- 2 issues possibles (victoire domicile ou extérieur)

**Ligues :**
- FC24. Penalty
- FC25. Penalty
- FC26. Penalty
- FIFA23. Penalty
- Penalty

### HIGHSCORE

**Pattern :** `3x3|4x4`

**Caractéristiques :**
- Matchs nuls possibles (has_draw: true)
- Scores très élevés (typical_goals: 8-22)
- Formats 3x3 / 4x4

**Ligues :**
- FC 24. 4x4. Championnat d'Angleterre
- FC 25. 3x3. Ligue de conférence

### RUSH

**Pattern :** `Rush`

**Caractéristiques :**
- Matchs nuls possibles (has_draw: true)
- Scores intermédiaires (typical_goals: 3-14)
- Grande variance
- Format 5x5

**Ligues :**
- FC 26. 5x5 Rush. Superligue

### CLASSIC

**Pattern :** `None` (tout le reste)

**Caractéristiques :**
- Matchs nuls possibles (has_draw: true)
- Scores classiques (typical_goals: 0-8)
- Proche du football réel

**Ligues :**
- FC 25. Championnat d'Angleterre
- FC 25. Champions League
- FC 25. Championnat d'Espagne
- FC 25. Championnat d'Allemagne
- FC 25. Italy Championship
- FC 25. Ligue européenne
- FC 26. Championnat du monde
- FC 26. Champions League
- World Cup 2026. Simulation

---

## Règles de cohérence

L'API applique 5 règles de cohérence globale pour éviter les contradictions entre les différentes prédictions.

### Règle 1 : Cohérence Over/Under (Monotonie)

Si over est favori pour un seuil, il doit l'être pour tous les seuils inférieurs.

**Exemple :**
- Si over est favori pour 3.5 buts, il doit aussi être favori pour 2.5 buts

### Règle 2 : Cohérence Handicap (Monotonie)

Si home est favori pour +1, il doit être encore plus favori pour +2.

**Exemple :**
- Si home est favori pour handicap +1.0, il doit être encore plus favori pour +2.0

### Règle 3 : Cohérence Score Exact ↔ Total Goals

Le score exact doit correspondre au total de buts prédit (écart max 2 buts).

**Implémentation :**
- Utilise les lambdas Poisson originaux (lambda_home, lambda_away)
- Préserve la force relative des équipes
- Évite les scores artificiels comme 3-3 systématiques

### Règle 4 : Cohérence Score Exact ↔ 1X2

Le score exact doit refléter le résultat prédit.

**Implémentation :**
- Le 1X2 est dérivé du score exact (pas l'inverse)
- home > away → "1"
- home == away → "X"
- home < away → "2"

### Règle 5 : Cohérence Score Exact ↔ Parity

Le score exact doit respecter la prédiction pair/impair.

**Implémentation :**
- La parité est dérivée du score exact (pas l'inverse)
- (home + away) % 2 == 0 → "pair"
- (home + away) % 2 == 1 → "impair"

---

## Entraînement des modèles

### Commande d'entraînement

```bash
python train_random_forest.py --csv finished_matches.csv --out ./models
```

### Options

- `--csv` : Chemin vers le fichier CSV d'entraînement
- `--out` : Répertoire de sortie pour les modèles
- `--eval` : Évaluer les modèles après entraînement

### Processus d'entraînement

1. Chargement des données
2. Séparation par famille
3. Calcul des features historiques
4. Entraînement des 4 tâches par famille :
   - Résultat (classification)
   - Total buts (régression)
   - Pair/Impair (classification)
   - Score exact (Poisson)
5. Sauvegarde des modèles

---

## Cache Upstash

### Configuration

Le cache Upstash est optionnel. S'il n'est pas configuré, l'API fonctionne sans cache.

### Activation

Créer un compte Upstash et configurer les variables d'environnement :

```env
UPSTASH_REDIS_REST_URL=https://your-rest-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-token
```

### Utilisation

- Les prédictions sont mises en cache pour 5 minutes
- Clé de cache : `predict:{team_home}:{team_away}:{league}`
- Nettoyage du cache via endpoint `/clear-cache`

---

## Tests

### Test de cohérence

```bash
python test_coherence.py
```

### Test de l'API

```bash
python test_client.py
```

### Test du cache

```bash
python test_cache_api.py
```

---

## License

Ce projet est développé par SOLITAIRE HACK.

---

## Support

Pour toute question ou problème, veuillez contacter l'équipe de développement.
