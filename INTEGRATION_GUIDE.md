# FIFA Virtual Prediction API - Guide d'Intégration Complet

## 📋 Vue d'ensemble

L'API FIFA Virtual Prediction permet de prédire les résultats de matchs FIFA virtuels en utilisant des modèles de machine learning entraînés sur des données historiques. L'API supporte plusieurs familles de championnats avec des caractéristiques différentes et fournit des prédictions cohérentes et adaptées aux options de paris réelles.

**Version:** 2.1.0  
**Base URL (Production):** `https://top-modele-train-api.onrender.com`  
**Base URL (Local):** `http://localhost:8000`  
**Statut:** ✅ Opérationnel en production  
**Données d'entraînement:** 13,262 matchs historiques  
**Familles supportées:** 4 (PENALTY, HIGHSCORE, RUSH, CLASSIC)  
**Ligues supportées:** 17 ligues FIFA virtuelles  
**Dernière mise à jour:** 15 Juin 2026 à 1h27 UTC

---

## 🚀 Démarrage Rapide

### 1. Test de l'API en production

```bash
# Vérification de la santé de l'API
curl https://top-modele-train-api.onrender.com/health
```

**Réponse attendue :**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "families": ["PENALTY", "HIGHSCORE", "RUSH", "CLASSIC"]
}
```

### 2. Première prédiction

```bash
curl -X POST https://top-modele-train-api.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "team_home": "Arsenal",
    "team_away": "Lille OSC",
    "league": "FC 25. Champions League"
  }'
```

---

## 📊 Ligues Supportées (17 ligues au total)

### PENALTY (5 ligues)
- **FC25. Penalty**: 1,838 matchs
- **FC24. Penalty**: 1,586 matchs
- **Penalty**: 2,419 matchs
- **FIFA23. Penalty**: 99 matchs
- **FC26. Penalty**: 335 matchs

### HIGHSCORE (2 ligues)
- **FC 24. 4x4. Championnat d'Angleterre**: 875 matchs
- **FC 25. 3x3. Ligue de conférence**: 992 matchs

### RUSH (1 ligue)
- **FC 26. 5x5 Rush. Superligue**: 810 matchs

### CLASSIC (9 ligues)
- **FC 25. Champions League**: 502 matchs
- **FC 26. Champions League**: 502 matchs
- **FC 25. Championnat d'Angleterre**: 526 matchs
- **FC 26. Championnat du monde**: 502 matchs
- **FC 25. Championnat d'Espagne**: 532 matchs
- **FC 25. Ligue européenne**: 521 matchs
- **FC 25. Italy Championship**: 519 matchs
- **FC 25. Championnat d'Allemagne**: 499 matchs
- **World Cup 2026. Simulation**: 220 matchs

---

## 🗺️ Mapping des Ligues (EN → FR)

L'API supporte le mapping automatique des noms de ligues anglais vers français pour la compatibilité avec les API externes.

### HIGHSCORE (3x3, 4x4)
- `FC 24. 4x4. England Championship` → `FC 24. 4x4. Championnat d'Angleterre`
- `FC 25. 3x3. Conference League` → `FC 25. 3x3. Ligue de conférence`

### RUSH (5x5)
- `FC 26. 5x5 Rush. Superleague` → `FC 26. 5x5 Rush. Superligue`

### CLASSIC (championnats classiques)
- `FC 25. Germany Championship` → `FC 25. Championnat d'Allemagne`
- `FC 25. England Championship` → `FC 25. Championnat d'Angleterre`
- `FC 25. Spain Championship` → `FC 25. Championnat d'Espagne`
- `FC 25. Champions League` → `FC 25. Champions League`
- `FC 25. Italy Championship` → `FC 25. Italy Championship`
- `FC 25. Europa League` → `FC 25. Ligue européenne`
- `FC 26. World Championship` → `FC 26. Championnat du monde`
- `FC 26. Champions League` → `FC 26. Champions League`
- `World Cup 2026. Simulation` → `World Cup 2026. Simulation`

### PENALTY (tirs au but)
- `FC24. Penalty` → `FC24. Penalty`
- `FC25. Penalty` → `FC25. Penalty`
- `FC26. Penalty` → `FC26. Penalty`
- `FIFA23. Penalty` → `FIFA23. Penalty`
- `Penalty` → `Penalty`

---

## 📊 Familles de Championnats

L'API supporte 4 familles de championnats avec des caractéristiques différentes :

| Famille | Pattern | Description | Nul autorisé | Fourchette buts typique | Ligues |
|---------|---------|-------------|--------------|------------------------|--------|
| **PENALTY** | `Penalty\|penalty` | Séances de tirs au but | ❌ Non | 3-15 | 5 |
| **HIGHSCORE** | `3x3\|4x4` | Formats 3x3 / 4x4 | ✅ Oui | 8-22 | 2 |
| **RUSH** | `Rush` | FC 26. 5x5 Rush | ✅ Oui | 3-14 | 1 |
| **CLASSIC** | (tous) | Championnats classiques | ✅ Oui | 0-8 | 9 |

---

## 🔌 Endpoints

### 1. GET `/health`

Vérifie la santé de l'API et le chargement des modèles.

**URL :** `https://top-modele-train-api.onrender.com/health`

**Méthode :** GET

**Réponse :**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "families": ["PENALTY", "HIGHSCORE", "RUSH", "CLASSIC"]
}
```

**Codes de réponse :**
- `200 OK` : API opérationnelle
- `503 Service Unavailable` : Modèles non chargés

---

### 2. GET `/families`

Retourne la configuration de toutes les familles disponibles.

**URL :** `https://top-modele-train-api.onrender.com/families`

**Méthode :** GET

**Réponse :**
```json
{
  "families": {
    "PENALTY": {
      "pattern": "Penalty|penalty",
      "has_draw": false,
      "typical_goals": [3, 15],
      "description": "Séances de tirs au but — 2 issues possibles, scores élevés"
    },
    "HIGHSCORE": {
      "pattern": "3x3|4x4",
      "has_draw": true,
      "typical_goals": [8, 22],
      "description": "Formats 3x3 / 4x4 — scores très élevés (~15 buts/match)"
    },
    "RUSH": {
      "pattern": "Rush",
      "has_draw": true,
      "typical_goals": [3, 14],
      "description": "FC 26. 5x5 Rush — profil intermédiaire, grande variance"
    },
    "CLASSIC": {
      "pattern": null,
      "has_draw": true,
      "typical_goals": [0, 8],
      "description": "Championnats classiques simulés — proche du football réel"
    }
  }
}
```

**Codes de réponse :**
- `200 OK` : Configuration retournée avec succès

---

### 3. GET `/leagues/{family}`

Retourne la liste des ligues pour une famille donnée.

**URL :** `https://top-modele-train-api.onrender.com/leagues/{family}`

**Méthode :** GET

**Paramètres :**
- `family` (path) : Nom de la famille (PENALTY, HIGHSCORE, RUSH, CLASSIC)

**Exemple :**
```bash
curl https://top-modele-train-api.onrender.com/leagues/CLASSIC
```

**Réponse :**
```json
{
  "family": "CLASSIC",
  "leagues": [
    "FC 25. Champions League",
    "FC 26. Champions League",
    "FC 25. Championnat d'Angleterre",
    "FC 26. Championnat du monde",
    "FC 25. Championnat d'Espagne",
    "FC 25. Ligue européenne",
    "FC 25. Italy Championship",
    "FC 25. Championnat d'Allemagne",
    "World Cup 2026. Simulation"
  ]
}
```

**Codes de réponse :**
- `200 OK` : Ligues retournées avec succès
- `404 Not Found` : Famille non trouvée
- `503 Service Unavailable` : Modèles non chargés

---

### 4. POST `/predict`

Prédit le résultat d'un match FIFA virtuel avec des prédictions cohérentes et adaptées aux options de paris.

**URL :** `https://top-modele-train-api.onrender.com/predict`

**Méthode :** POST

**Content-Type :** application/json

**Corps de la requête :**
```json
{
  "team_home": "Arsenal",
  "team_away": "Lille OSC",
  "league": "FC 25. Champions League"
}
```

**Champs requis :**
- `team_home` (string) : Nom de l'équipe domicile
- `team_away` (string) : Nom de l'équipe extérieur
- `league` (string) : Nom de la ligue/championnat (supporte mapping EN → FR)

**Réponse complète :**
```json
{
  "match": "Arsenal vs Lille OSC",
  "league": "FC 25. Champions League",
  "family": "CLASSIC",
  "predictions": {
    "1x2": {
      "home": 0.481,
      "draw": 0.228,
      "away": 0.291
    },
    "total_goals": {
      "predicted": 4.7,
      "over_under": {
        "3.0": {"over": 0.589, "under": 0.411},
        "3.5": {"over": 0.564, "under": 0.436},
        "4.0": {"over": 0.346, "under": 0.654},
        "4.5": {"over": 0.321, "under": 0.679},
        "5.0": {"over": 0.153, "under": 0.847},
        "5.5": {"over": 0.128, "under": 0.872},
        "6.0": {"over": 0.05, "under": 0.95}
      }
    },
    "handicap": {
      "1": {"home": 0.9, "draw": 0.069, "away": 0.031},
      "2": {"home": 0.969, "draw": 0.024, "away": 0.008},
      "3": {"home": 0.992, "draw": 0.006, "away": 0.002},
      "4": {"home": 0.998, "draw": 0.001, "away": 0.0}
    },
    "parity": {
      "pair": 0.455,
      "impair": 0.545
    },
    "exact_score": {
      "prediction": "2-0"
    }
  }
}
```

**Champs de réponse :**
- `match` : Nom du match formaté
- `league` : Nom de la ligue
- `family` : Famille détectée automatiquement
- `predictions.1x2` : Probabilités pour Home/Draw/Away
- `predictions.total_goals.predicted` : Total de buts prédit
- `predictions.total_goals.over_under` : Probabilités over/under pour seuils dynamiques (adaptés au total prédit)
- `predictions.handicap` : Probabilités handicap pour seuils dynamiques (adaptés à la différence prédite)
- `predictions.parity` : Probabilités pair/impair
- `predictions.exact_score.prediction` : Score exact le plus probable

**Codes de réponse :**
- `200 OK` : Prédiction générée avec succès
- `400 Bad Request` : Paramètres invalides
- `503 Service Unavailable` : Modèles non chargés

---

### 5. POST `/update-history`

Met à jour l'historique des équipes avec un match terminé (optionnel, pour améliorer les prédictions futures).

**URL :** `https://top-modele-train-api.onrender.com/update-history`

**Méthode :** POST

**Content-Type :** application/json

**Corps de la requête :**
```json
{
  "team_home": "Arsenal",
  "team_away": "Lille OSC",
  "league": "FC 25. Champions League",
  "score_home": 2,
  "score_away": 2,
  "finished_at": "2026-06-12T18:00:00Z",
  "family": "CLASSIC"
}
```

**Champs requis :**
- `team_home` (string) : Nom de l'équipe domicile
- `team_away` (string) : Nom de l'équipe extérieur
- `league` (string) : Nom de la ligue/championnat
- `score_home` (integer) : Score domicile
- `score_away` (integer) : Score extérieur
- `finished_at` (string) : Date de fin (ISO8601)

**Champs optionnels :**
- `family` (string) : Famille (auto-détectée si non spécifiée)

**Réponse :**
```json
{
  "status": "success",
  "message": "Historique mis à jour"
}
```

**Codes de réponse :**
- `200 OK` : Historique mis à jour avec succès
- `500 Internal Server Error` : Erreur lors de la mise à jour

---

### 6. POST `/save-history`

Sauvegarde l'historique mis à jour sur disque.

**URL :** `https://top-modele-train-api.onrender.com/save-history`

**Méthode :** POST

**Paramètres de requête :**
- `family` (optionnel) : Si spécifié, sauvegarde seulement cette famille

**Exemple :**
```bash
curl -X POST "https://top-modele-train-api.onrender.com/save-history?family=CLASSIC"
```

**Réponse :**
```json
{
  "status": "success",
  "message": "Historique sauvegardé"
}
```

**Codes de réponse :**
- `200 OK` : Historique sauvegardé avec succès
- `500 Internal Server Error` : Erreur lors de la sauvegarde

---

## 🧠 Cohérence des Prédictions

L'API assure la cohérence entre toutes les prédictions pour éviter des résultats contradictoires.

### Cohérence 1x2 ↔ Handicap
- Si home est favori dans 1x2 (ex: 76%), les handicaps positifs pour home sont plus probables
- Si away est favori dans 1x2, les handicaps négatifs pour home sont plus probables
- Les handicaps sont ajustés progressivement (20% par unité) pour éviter les changements brusques
- Forçage de la cohérence: si le favori n'est pas correct, les probabilités sont ajustées (0.6/0.2/0.2)

### Cohérence Total Goals ↔ Over/Under
- Si le total prédit est supérieur au seuil, over est favorisé
- Si le total prédit est inférieur au seuil, under est favorisé
- Les seuils sont sélectionnés dynamiquement autour du total prédit (±3 seuils)
- Ajustement renforcé (40% max) pour garantir la cohérence
- Forçage de la cohérence: si total > seuil, over > under (0.6/0.4)

### Seuils Dynamiques
- **Over/Under**: Sélectionnés autour du total prédit (ex: total 8.5 → seuils 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0)
- **Handicap**: Sélectionnés autour de la différence prédite (ex: diff ~1 → handicaps -2, -1, 1, 2)
- Maximum 7 seuils over/under et 5 handicaps pour éviter la surcharge d'informations

### Validation de Cohérence
- Tous les seuils over/under sont validés pour garantir la cohérence avec le total prédit
- Tous les handicaps sont validés pour garantir la cohérence avec les prédictions 1x2
- Tests automatiques sur toutes les familles (CLASSIC, HIGHSCORE, RUSH, PENALTY)

---

## 🔧 Installation Locale

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)

### Dépendances

```txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
joblib==1.3.2
scipy==1.11.4
```

### Installation

```bash
# Cloner le repository
git clone https://github.com/MALICK-GITH/TOP-MODELE-TRAIN-API.git
cd TOP-MODELE-TRAIN-API

# Installer les dépendances
pip install -r requirements.txt

# Télécharger les modèles pré-entraînés (si non inclus)
# Les modèles doivent être dans le répertoire ./models
```

### Démarrage Local

```bash
# Démarrer l'API
python api.py

# L'API sera accessible sur http://localhost:8000
```

### Variables d'Environnement

- `MODELS_DIR` : Répertoire contenant les modèles (défaut: `./models`)
- `HOST` : Hôte de l'API (défaut: `0.0.0.0`)
- `PORT` : Port de l'API (défaut: `8000`)

---

## 🚀 Déploiement

### Déploiement sur Render

1. **Créer un compte Render** : https://render.com
2. **Créer un nouveau Web Service**
3. **Connecter le repository GitHub**
4. **Configurer le build et le démarrage** :
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python api.py`
5. **Déployer**

### Déploiement sur Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "api.py"]
```

```bash
# Construire l'image
docker build -t fifa-prediction-api .

# Lancer le conteneur
docker run -p 8000:8000 fifa-prediction-api
```

### Déploiement sur AWS EC2

```bash
# Lancer une instance EC2 avec Ubuntu
# SSH dans l'instance
ssh ubuntu@your-ec2-ip

# Installer Python et pip
sudo apt update
sudo apt install python3 python3-pip -y

# Cloner le repository
git clone https://github.com/MALICK-GITH/TOP-MODELE-TRAIN-API.git
cd TOP-MODELE-TRAIN-API

# Installer les dépendances
pip3 install -r requirements.txt

# Installer et configurer systemd
sudo nano /etc/systemd/system/fifa-api.service
```

Contenu du service systemd :
```ini
[Unit]
Description=FIFA Prediction API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/TOP-MODELE-TRAIN-API
ExecStart=/usr/bin/python3 api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer le service
sudo systemctl enable fifa-api
sudo systemctl start fifa-api
sudo systemctl status fifa-api
```

---

## 🧪 Tests Locaux

### Test de santé

```bash
curl http://localhost:8000/health
```

### Test de prédiction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "team_home": "Arsenal",
    "team_away": "Napoli",
    "league": "FC 26. 5x5 Rush. Superligue"
  }'
```

### Test avec différentes familles

```bash
# CLASSIC
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"team_home":"Real Madrid","team_away":"Barcelona","league":"FC 25. Champions League"}'

# HIGHSCORE
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"team_home":"Manchester City","team_away":"Liverpool","league":"FC 24. 4x4. Championnat d'Angleterre"}'

# RUSH
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"team_home":"Arsenal","team_away":"Napoli","league":"FC 26. 5x5 Rush. Superligue"}'

# PENALTY
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"team_home":"PSG","team_away":"Bayern Munich","league":"FC25. Penalty"}'
```

---

## 📈 Performance

### Benchmarks

- **Temps de réponse moyen**: < 100ms par requête
- **Temps de réponse P95**: < 200ms par requête
- **Temps de réponse P99**: < 500ms par requête
- **Débit maximum**: ~1000 requêtes/secondes (dépend du serveur)

### Limites

- **Pas de limites de taux explicites** sur l'API de production
- **Recommandation**: Implémenter un rate limiting côté client
- **Backoff exponentiel**: En cas d'erreurs, utiliser un backoff exponentiel

---

## 🔒 Sécurité

### Best Practices

1. **HTTPS**: Toujours utiliser HTTPS en production
2. **Validation des entrées**: L'API valide toutes les entrées
3. **Rate Limiting**: Implémenter un rate limiting côté client
4. **Logging**: Loguez toutes les requêtes pour le debugging
5. **Monitoring**: Surveillez les temps de réponse et les taux d'erreur

### Codes d'Erreur

| Code | Signification | Action recommandée |
|------|--------------|-------------------|
| 200 | Success | Aucune action requise |
| 400 | Bad Request | Vérifiez les paramètres de la requête |
| 404 | Not Found | Vérifiez l'URL et les paramètres |
| 503 | Service Unavailable | Modèles non chargés, réessayez plus tard |
| 500 | Internal Server Error | Erreur serveur, contactez le support |

---

## 🔄 Mise à jour des Modèles

### Réentraînement avec de nouvelles données

```bash
python train_random_forest.py \
  --csv finished_matches_dataset.csv \
  --out ./models
```

### Structure des modèles

```
models/
├── PENALTY/
│   ├── result.pkl
│   ├── total_goals.pkl
│   ├── parity.pkl
│   ├── poisson.pkl
│   ├── meta.json
│   └── team_history.pkl
├── HIGHSCORE/
│   ├── result.pkl
│   ├── total_goals.pkl
│   ├── parity.pkl
│   ├── poisson.pkl
│   ├── meta.json
│   └── team_history.pkl
├── RUSH/
│   ├── result.pkl
│   ├── total_goals.pkl
│   ├── parity.pkl
│   ├── poisson.pkl
│   ├── meta.json
│   └── team_history.pkl
├── CLASSIC/
│   ├── result.pkl
│   ├── total_goals.pkl
│   ├── parity.pkl
│   ├── poisson.pkl
│   ├── meta.json
│   └── team_history.pkl
└── summary.json
```

---

## 📊 Modèles Utilisés

### Algorithmes

- **Résultat** : GradientBoostingClassifier (ou RandomForestClassifier pour petits datasets)
- **Total buts** : GradientBoostingRegressor (ou Ridge pour petits datasets)
- **Pair/Impair** : LogisticRegression
- **Score exact** : Modèle de Poisson indépendant pour chaque équipe

### Features Calculés

L'API calcule automatiquement les features suivants à partir de l'historique des équipes :

- **Statistiques de base** (windows 5 et 10): played, wins, draws, losses, gf, ga, gd, win_rate, draw_rate
- **Statistiques avancées**: unbeaten_rate, form_points, form_ppg
- **Statistiques domicile/extérieur uniquement**: home_only_w5, away_only_w5, home_only_w10, away_only_w10
- **Statistiques tête-à-tête**: h2h_w5, h2h_w10
- **Features différentielles**: diff_w5_win_rate, diff_w10_win_rate, etc.

---

## 💡 Exemples d'Utilisation

### Python

```python
import requests

# Configuration de l'API
API_BASE_URL = "https://top-modele-train-api.onrender.com"

# Vérification de la santé
health_response = requests.get(f"{API_BASE_URL}/health")
print(f"Statut API: {health_response.json()['status']}")

# Prédiction d'un match
prediction_response = requests.post(f"{API_BASE_URL}/predict", json={
    'team_home': 'Arsenal',
    'team_away': 'Lille OSC',
    'league': 'FC 25. Champions League'
})

prediction = prediction_response.json()
print(f"Résultat prédit: {prediction['predictions']['1x2']}")
print(f"Score exact: {prediction['predictions']['exact_score']['prediction']}")
print(f"Total buts: {prediction['predictions']['total_goals']['predicted']}")
print(f"Over/Under: {prediction['predictions']['total_goals']['over_under']}")
print(f"Handicap: {prediction['predictions']['handicap']}")
```

### JavaScript/Node.js

```javascript
const API_BASE_URL = "https://top-modele-train-api.onrender.com";

// Vérification de la santé
const healthResponse = await fetch(`${API_BASE_URL}/health`);
const healthData = await healthResponse.json();
console.log(`Statut API: ${healthData.status}`);

// Prédiction d'un match
const predictionResponse = await fetch(`${API_BASE_URL}/predict`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    team_home: 'Arsenal',
    team_away: 'Lille OSC',
    league: 'FC 25. Champions League'
  })
});

const prediction = await predictionResponse.json();
console.log(`Résultat: ${JSON.stringify(prediction.predictions['1x2'])}`);
console.log(`Score exact: ${prediction.predictions.exact_score.prediction}`);
console.log(`Total buts: ${prediction.predictions.total_goals.predicted}`);
console.log(`Over/Under: ${JSON.stringify(prediction.predictions.total_goals.over_under)}`);
console.log(`Handicap: ${JSON.stringify(prediction.predictions.handicap)}`);
```

### cURL

```bash
# Vérification de la santé
curl https://top-modele-train-api.onrender.com/health

# Prédiction d'un match
curl -X POST https://top-modele-train-api.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "team_home": "Arsenal",
    "team_away": "Lille OSC",
    "league": "FC 25. Champions League"
  }'

# Liste des ligues CLASSIC
curl https://top-modele-train-api.onrender.com/leagues/CLASSIC
```

---

## 🏢 Intégration pour Plateformes

### Architecture recommandée

```python
import requests
import time
from typing import Dict, Any

class FIFAPredictionClient:
    """Client pour l'API FIFA Prediction"""
    
    def __init__(self, base_url: str = "https://top-modele-train-api.onrender.com"):
        self.base_url = base_url
        self.timeout = 10  # secondes
        
    def health_check(self) -> bool:
        """Vérifie si l'API est opérationnelle"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return response.json().get("status") == "healthy"
        except Exception:
            return False
    
    def predict_match(
        self, 
        team_home: str, 
        team_away: str, 
        league: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Prédit le résultat d'un match avec retry automatique
        """
        payload = {
            "team_home": team_home,
            "team_away": team_away,
            "league": league
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/predict",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Erreur après {max_retries} tentatives: {e}")
                time.sleep(2 ** attempt)
    
    def get_available_leagues(self, family: str) -> list:
        """Retourne la liste des ligues disponibles pour une famille"""
        response = requests.get(
            f"{self.base_url}/leagues/{family}",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json().get("leagues", [])

# Exemple d'utilisation
client = FIFAPredictionClient()

if client.health_check():
    print("API opérationnelle")
    
    prediction = client.predict_match(
        team_home="Arsenal",
        team_away="Lille OSC",
        league="FC 25. Champions League"
    )
    
    print(f"Résultat: {prediction['predictions']['1x2']}")
    print(f"Score exact: {prediction['predictions']['exact_score']['prediction']}")
```

---

## ⚠️ Notes Importantes

1. **Détection automatique de la famille** : L'API détecte automatiquement la famille du championnat basée sur le nom de la ligue.
2. **Mapping automatique des ligues** : L'API mappe automatiquement les noms de ligues anglais vers français.
3. **Cohérence des prédictions** : L'API assure la cohérence entre toutes les prédictions (1x2, handicap, over/under).
4. **Seuils dynamiques** : Les seuils over/under et handicap sont sélectionnés dynamiquement en fonction des prédictions.
5. **Données historiques** : Les modèles utilisent l'historique des équipes pour calculer les features.
6. **Performance** : Les modèles sont chargés en mémoire au démarrage pour des prédictions rapides (< 100ms).

---

## 🆘 Support

Pour toute question ou problème, contactez l'équipe de développement.

**Repository GitHub :** https://github.com/MALICK-GITH/TOP-MODELE-TRAIN-API

---

## 📝 Changelog

### Version 2.1.0 (15 Juin 2026 à 1h27 UTC)
- **Correction critique**: Renforcement de la cohérence des prédictions (over/under et handicap)
- Ajustement plus fort pour over/under (40% au lieu de 15%)
- Forçage de la cohérence over/under: si total > seuil, over > under
- Ajustement plus fort pour handicap (20% au lieu de 10%)
- Forçage de la cohérence handicap: si home favori en 1x2, handicaps positifs favorisent home
- Réentraînement des modèles avec dataset actualisé (13,262 matchs)
- Période du dataset: 27 mai 2026 - 14 juin 2026
- Sources multiples: 888starz et cron-learning
- Tests validés: cohérence parfaite sur toutes les familles
- Résolution du problème d'incohérence des options de paris sur la plateforme

### Version 2.0.0 (14 Juin 2026)
- Ajout de la cohérence entre les prédictions (1x2 ↔ handicap, total_goals ↔ over/under)
- Sélection dynamique des seuils over/under et handicap
- Support de 17 ligues FIFA virtuelles
- Mapping automatique des ligues (EN → FR)
- Mise à jour du format de réponse avec over/under et handicap
- Amélioration de la documentation

### Version 1.0.0 (12 Juin 2026)
- Version initiale
- Support de 4 familles de championnats
- Prédictions basiques (1x2, total_goals, parity, exact_score)

---

**Document généré par SOLITAIRE HACK**  
*Dernière mise à jour : 15 Juin 2026 à 1h27 UTC*  
*Version : 2.1.0 - Production*  
*Tous droits réservés*
