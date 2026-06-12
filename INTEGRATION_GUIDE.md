# FIFA Virtual Prediction API - Guide d'Intégration

## 📋 Vue d'ensemble

L'API FIFA Virtual Prediction permet de prédire les résultats de matchs FIFA virtuels en utilisant des modèles de machine learning entraînés sur des données historiques. L'API supporte plusieurs familles de championnats avec des caractéristiques différentes.

**Version:** 1.0.0  
**Base URL (Production):** `https://top-modele-train-api.onrender.com`  
**Statut:** ✅ Opérationnel en production  
**Données d'entraînement:** 10,464 matchs historiques

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

Prédit le résultat d'un match FIFA virtuel.

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
- `league` (string) : Nom de la ligue/championnat

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
- `match` : Nom du match formaté
- `league` : Nom de la ligue
- `family` : Famille détectée automatiquement
- `result.prediction` : Résultat prédit (H=Home, D=Draw, A=Away)
- `result.probabilities` : Probabilités pour chaque issue (H, D, A)
- `total_goals.prediction` : Total de buts prédit
- `total_goals.lambda_home/away` : Paramètres λ du modèle de Poisson
- `parity.prediction` : Pair ou impair
- `parity.prob_pair/impair` : Probabilités pour pair/impair
- `exact_score.prediction` : Score exact le plus probable

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
print(f"Résultat prédit: {prediction['result']['prediction']}")
print(f"Score exact: {prediction['exact_score']['prediction']}")
print(f"Total buts: {prediction['total_goals']['prediction']}")
print(f"Probabilités: H={prediction['result']['probabilities']['H']:.2%}, "
      f"D={prediction['result']['probabilities']['D']:.2%}, "
      f"A={prediction['result']['probabilities']['A']:.2%}")
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
console.log(`Résultat prédit: ${prediction.result.prediction}`);
console.log(`Score exact: ${prediction.exact_score.prediction}`);
console.log(`Total buts: ${prediction.total_goals.prediction}`);
console.log(`Probabilités: H=${(prediction.result.probabilities.H * 100).toFixed(1)}%, ` +
            `D=${(prediction.result.probabilities.D * 100).toFixed(1)}%, ` +
            `A=${(prediction.result.probabilities.A * 100).toFixed(1)}%`);
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

## ⚠️ Notes Importantes

1. **Détection automatique de la famille** : L'API détecte automatiquement la famille du championnat basée sur le nom de la ligue. Vous n'avez pas besoin de spécifier la famille manuellement.

2. **Données historiques** : Les modèles utilisent l'historique des équipes pour calculer les features. Pour les équipes nouvelles ou avec peu d'historique, les prédictions seront basées sur des valeurs par défaut.

3. **Mise à jour de l'historique** : L'endpoint `/update-history` est optionnel. Il permet d'améliorer les prédictions futures en ajoutant les résultats réels des matchs.

4. **Performance** : Les modèles sont chargés en mémoire au démarrage de l'API pour des prédictions rapides (< 100ms par requête).

5. **Limites de taux** : L'API n'a pas de limites de taux explicites, mais il est recommandé d'implémenter un backoff exponentiel en cas d'erreurs.

---

## 🏢 Intégration pour Plateformes

### Architecture recommandée

Pour une intégration optimale dans votre plateforme :

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
        
        Args:
            team_home: Nom de l'équipe domicile
            team_away: Nom de l'équipe extérieur
            league: Nom de la ligue
            max_retries: Nombre maximum de tentatives
            
        Returns:
            Dictionnaire contenant la prédiction
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
                # Backoff exponentiel
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

# Vérification de la santé
if client.health_check():
    print("API opérationnelle")
    
    # Prédiction
    prediction = client.predict_match(
        team_home="Arsenal",
        team_away="Lille OSC",
        league="FC 25. Champions League"
    )
    
    print(f"Résultat: {prediction['result']['prediction']}")
    print(f"Score exact: {prediction['exact_score']['prediction']}")
```

### Gestion des erreurs

```python
import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def safe_predict(team_home: str, team_away: str, league: str):
    """Prédiction avec gestion complète des erreurs"""
    try:
        response = requests.post(
            "https://top-modele-train-api.onrender.com/predict",
            json={
                "team_home": team_home,
                "team_away": team_away,
                "league": league
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
        
    except Timeout:
        print("Erreur: Timeout de l'API")
        return None
        
    except HTTPError as e:
        if e.response.status_code == 400:
            print("Erreur: Paramètres invalides")
        elif e.response.status_code == 503:
            print("Erreur: Modèles non chargés")
        else:
            print(f"Erreur HTTP: {e.response.status_code}")
        return None
        
    except RequestException as e:
        print(f"Erreur de connexion: {e}")
        return None
```

### Intégration React/JavaScript

```javascript
class FIFAPredictionAPI {
  constructor(baseUrl = 'https://top-modele-train-api.onrender.com') {
    this.baseUrl = baseUrl;
    this.timeout = 10000; // 10 secondes
  }

  async healthCheck() {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        signal: AbortSignal.timeout(this.timeout)
      });
      const data = await response.json();
      return data.status === 'healthy';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  async predictMatch(teamHome, teamAway, league) {
    try {
      const response = await fetch(`${this.baseUrl}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          team_home: teamHome,
          team_away: teamAway,
          league: league
        }),
        signal: AbortSignal.timeout(this.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Prediction failed:', error);
      throw error;
    }
  }

  async getLeagues(family) {
    try {
      const response = await fetch(`${this.baseUrl}/leagues/${family}`, {
        signal: AbortSignal.timeout(this.timeout)
      });
      const data = await response.json();
      return data.leagues || [];
    } catch (error) {
      console.error('Failed to get leagues:', error);
      return [];
    }
  }
}

// Exemple d'utilisation dans un composant React
const api = new FIFAPredictionAPI();

function MatchPrediction({ teamHome, teamAway, league }) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.predictMatch(teamHome, teamAway, league);
      setPrediction(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={handlePredict} disabled={loading}>
        {loading ? 'Prediction en cours...' : 'Prédire'}
      </button>
      
      {error && <div className="error">Erreur: {error}</div>}
      
      {prediction && (
        <div className="prediction">
          <h3>Résultat: {prediction.result.prediction}</h3>
          <p>Score exact: {prediction.exact_score.prediction}</p>
          <p>Total buts: {prediction.total_goals.prediction}</p>
        </div>
      )}
    </div>
  );
}
```

### Meilleures pratiques pour les plateformes

1. **Cache des résultats** : Cachez les prédictions pour les mêmes matchs pendant 5-10 minutes
2. **Monitoring** : Surveillez les temps de réponse et les taux d'erreur
3. **Fallback** : Prévoyez un système de fallback en cas d'indisponibilité
4. **Logging** : Loguez toutes les requêtes et réponses pour le debugging
5. **Rate limiting** : Implémentez un rate limiting côté client pour éviter les abus

---

## 🔧 Configuration

### Variables d'environnement (pour déploiement local)

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

**Performance des modèles :**
- Entraînés sur 10,464 matchs historiques
- 4 familles de championnats supportées
- Temps de réponse < 100ms par requête

---

## 🆘 Support

Pour toute question ou problème, contactez l'équipe de développement.

**Repository GitHub :** https://github.com/MALICK-GITH/TOP-MODELE-TRAIN-API

---

**Document généré par SOLITAIRE HACK**  
*Dernière mise à jour : 12 Juin 2026*  
*Version : 1.0.0 - Production*
