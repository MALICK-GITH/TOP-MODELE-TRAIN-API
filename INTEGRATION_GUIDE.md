# FIFA Virtual Prediction API - Guide d'Intégration

## 📋 Vue d'ensemble

L'API FIFA Virtual Prediction permet de prédire les résultats de matchs FIFA virtuels en utilisant des modèles de machine learning entraînés sur des données historiques. L'API supporte plusieurs familles de championnats avec des caractéristiques différentes.

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000`  
**Statut:** ✅ Opérationnel

---

## 🚀 Démarrage Rapide

### 1. Lancement de l'API

```bash
# Depuis le répertoire du projet
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Vérification de la santé

```bash
curl http://localhost:8000/health
```

**Réponse attendue :**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "families": ["PENALTY", "HIGHSCORE", "RUSH", "CLASSIC"]
}
```

---

## 📊 Familles de Championnats

L'API supporte 4 familles de championnats avec des caractéristiques différentes :

| Famille | Pattern | Description | Nul autorisé | Fourchette buts typique |
|---------|---------|-------------|--------------|------------------------|
| **PENALTY** | `Penalty\|penalty` | Séances de tirs au but | ❌ Non | 3-15 |
| **HIGHSCORE** | `3x3\|4x4` | Formats 3x3 / 4x4 | ✅ Oui | 8-22 |
| **RUSH** | `Rush` | FC 26. 5x5 Rush | ✅ Oui | 3-14 |
| **CLASSIC** | (tous) | Championnats classiques | ✅ Oui | 0-8 |

---

## 🔌 Endpoints

### 1. GET `/health`

Vérifie la santé de l'API et le chargement des modèles.

**Réponse :**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "families": ["PENALTY", "HIGHSCORE", "RUSH", "CLASSIC"]
}
```

---

### 2. GET `/families`

Retourne la configuration de toutes les familles disponibles.

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
    ...
  }
}
```

---

### 3. GET `/leagues/{family}`

Retourne la liste des ligues pour une famille donnée.

**Exemple :**
```bash
curl http://localhost:8000/leagues/CLASSIC
```

**Réponse :**
```json
{
  "family": "CLASSIC",
  "leagues": [
    "FC 25. Champions League",
    "FC 26. Champions League",
    "FC 25. Championnat d'Angleterre",
    ...
  ]
}
```

---

### 4. POST `/predict`

Prédit le résultat d'un match FIFA virtuel.

**Corps de la requête :**
```json
{
  "team_home": "Arsenal",
  "team_away": "Lille OSC",
  "league": "FC 25. Champions League"
}
```

**Réponse :**
```json
{
  "match": "Arsenal vs Lille OSC",
  "league": "FC 25. Champions League",
  "family": "CLASSIC",
  "result": {
    "prediction": "D",
    "probabilities": {
      "A": 0.273,
      "D": 0.454,
      "H": 0.273
    }
  },
  "total_goals": {
    "prediction": 3.2,
    "lambda_home": 1.76,
    "lambda_away": 1.31
  },
  "parity": {
    "prediction": "impair",
    "prob_pair": 0.244,
    "prob_impair": 0.756
  },
  "exact_score": {
    "prediction": "1-1"
  }
}
```

**Champs de réponse :**
- `result.prediction` : Résultat prédit (H=Home, D=Draw, A=Away)
- `result.probabilities` : Probabilités pour chaque issue
- `total_goals.prediction` : Total de buts prédit
- `total_goals.lambda_home/away` : Paramètres λ du modèle de Poisson
- `parity.prediction` : Pair ou impair
- `exact_score.prediction` : Score exact le plus probable

---

### 5. POST `/update-history`

Met à jour l'historique des équipes avec un match terminé (optionnel, pour améliorer les prédictions futures).

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

**Réponse :**
```json
{
  "status": "success",
  "message": "Historique mis à jour"
}
```

---

### 6. POST `/save-history`

Sauvegarde l'historique mis à jour sur disque.

**Paramètres :**
- `family` (optionnel) : Si spécifié, sauvegarde seulement cette famille

**Exemple :**
```bash
curl -X POST http://localhost:8000/save-history?family=CLASSIC
```

**Réponse :**
```json
{
  "status": "success",
  "message": "Historique sauvegardé"
}
```

---

## 💡 Exemples d'Utilisation

### Python

```python
import requests

# Prédiction d'un match
response = requests.post('http://localhost:8000/predict', json={
    'team_home': 'Arsenal',
    'team_away': 'Lille OSC',
    'league': 'FC 25. Champions League'
})

prediction = response.json()
print(f"Résultat prédit: {prediction['result']['prediction']}")
print(f"Score exact: {prediction['exact_score']['prediction']}")
print(f"Total buts: {prediction['total_goals']['prediction']}")
```

### JavaScript/Node.js

```javascript
const response = await fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    team_home: 'Arsenal',
    team_away: 'Lille OSC',
    league: 'FC 25. Champions League'
  })
});

const prediction = await response.json();
console.log(`Résultat prédit: ${prediction.result.prediction}`);
console.log(`Score exact: ${prediction.exact_score.prediction}`);
```

### cURL

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "team_home": "Arsenal",
    "team_away": "Lille OSC",
    "league": "FC 25. Champions League"
  }'
```

---

## ⚠️ Notes Importantes

1. **Détection automatique de la famille** : L'API détecte automatiquement la famille du championnat basée sur le nom de la ligue. Vous n'avez pas besoin de spécifier la famille manuellement.

2. **Données historiques** : Les modèles utilisent l'historique des équipes pour calculer les features. Pour les équipes nouvelles ou avec peu d'historique, les prédictions seront basées sur des valeurs par défaut.

3. **Mise à jour de l'historique** : L'endpoint `/update-history` est optionnel. Il permet d'améliorer les prédictions futures en ajoutant les résultats réels des matchs.

4. **Performance** : Les modèles sont chargés en mémoire au démarrage de l'API pour des prédictions rapides (< 100ms par requête).

---

## 🔧 Configuration

### Variables d'environnement

- `MODELS_DIR` : Répertoire contenant les modèles (défaut: `./models`)
- `HOST` : Hôte de l'API (défaut: `0.0.0.0`)
- `PORT` : Port de l'API (défaut: `8000`)

### Réentraînement des modèles

Pour réentraîner les modèles avec de nouvelles données :

```bash
python train_random_forest.py --csv finished_matches_dataset.csv --out ./models
```

---

## 📈 Modèles Utilisés

- **Résultat** : GradientBoostingClassifier (ou RandomForestClassifier pour petits datasets)
- **Total buts** : GradientBoostingRegressor (ou Ridge pour petits datasets)
- **Pair/Impair** : LogisticRegression
- **Score exact** : Modèle de Poisson indépendant pour chaque équipe

---

## 🆘 Support

Pour toute question ou problème, contactez l'équipe de développement.

---

**Document généré par SOLITAIRE HACK**  
*Dernière mise à jour : 12 Juin 2026*
