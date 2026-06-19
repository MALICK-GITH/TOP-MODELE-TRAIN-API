# API INTEGRATION GUIDE - FIFA Virtual Prediction System

**Production URL:** `https://top-modele-train-api-vmp.onrender.com`

**Version:** 3.0.0  
**Last Updated:** 2026-06-19

---

## 🚀 Quick Start

### Base URL
```
https://top-modele-train-api-vmp.onrender.com
```

### Authentication
No authentication required for public endpoints.

### Rate Limiting
- Cache: 5 minutes per prediction
- Recommended: Max 60 requests/minute per IP

---

## 📡 API Endpoints

### 1. Health Check
Check API status and loaded models.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "families": ["PENALTY", "HIGHSCORE", "RUSH", "CLASSIC"]
}
```

---

### 2. Predict Match
Get prediction for a FIFA match with dynamic Poisson system and platform-specific option mapping.

```http
POST /predict
Content-Type: application/json
```

**Request Body:**
```json
{
  "team_home": "Chelsea",
  "team_away": "Club Atlético de Madrid",
  "league": "FC 26. 5x5 Rush. Superleague"
}
```

**Response:**
```json
{
  "match": "Chelsea vs Club Atlético de Madrid",
  "league": "FC 26. 5x5 Rush. Superligue",
  "family": "RUSH",
  "predictions": {
    "1x2": {
      "home": 0.334,
      "draw": 0.120,
      "away": 0.547
    },
    "total_goals": {
      "predicted": 8.6,
      "platform_value": 8.5,
      "platform_name": "Total Goals"
    },
    "handicap": {
      "predicted": -2.0,
      "platform_value": -2.0,
      "platform_name": "Handicap"
    },
    "over_under": {
      "under": 0.336,
      "over": 0.664
    },
    "btts": {
      "no": 0.069,
      "yes": 0.931
    },
    "parity": {
      "pair": 0.481,
      "impair": 0.519
    },
    "exact_score": {
      "prediction": "3-5"
    }
  },
  "meta": {
    "lambda_home": 3.32,
    "lambda_away": 5.29
  }
}
```

**Key Changes from v2.2.0:**
- ❌ Removed `history` section (team historical data)
- ✅ Added `platform_value` and `platform_name` for total_goals and handicap
- ✅ Added `meta` section with Poisson lambda values
- ✅ Simplified `over_under` (single under/over instead of multiple thresholds)
- ✅ Simplified `handicap` (single predicted value instead of multiple thresholds)
- ✅ Dynamic Poisson system for varied exact score predictions

---

### 3. Clear Cache
Clear prediction cache to force recomputation.

```http
POST /clear-cache
```

**Response:**
```json
{
  "status": "success",
  "message": "Cache nettoyé"
}
```

---

### 6. Get Families
List all available families with configurations.

```http
GET /families
```

**Response:**
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

---

### 7. Get Leagues by Family
List all leagues for a specific family.

```http
GET /leagues/CLASSIC
```

**Response:**
```json
{
  "family": "CLASSIC",
  "leagues": [
    "FC 25. Championnat d'Angleterre",
    "FC 25. Champions League",
    "FC 25. Championnat d'Espagne",
    "FC 25. Championnat d'Allemagne",
    "FC 25. Italy Championship",
    "FC 25. Ligue européenne",
    "FC 26. Championnat du monde",
    "FC 26. Champions League",
    "World Cup 2026. Simulation"
  ]
}
```

---

## 📊 League Mapping

The API automatically maps live league names to trained league names:

| Live Name (EN) | Trained Name (FR) |
|----------------|-------------------|
| FC 24. 4x4. England Championship | FC 24. 4x4. Championnat d'Angleterre |
| FC 25. 3x3. Conference League | FC 25. 3x3. Ligue de conférence |
| FC 26. 5x5 Rush. Superleague | FC 26. 5x5 Rush. Superligue |
| FC 25. Germany Championship | FC 25. Championnat d'Allemagne |
| FC 25. England Championship | FC 25. Championnat d'Angleterre |
| FC 25. Spain Championship | FC 25. Championnat d'Espagne |
| FC 25. Champions League | FC 25. Champions League |
| FC 25. Italy Championship | FC 25. Italy Championship |
| FC 25. Europa League | FC 25. Ligue européenne |
| FC 26. World Championship | FC 26. Championnat du monde |
| FC 26. Champions League | FC 26. Champions League |
| World Cup 2026. Simulation | World Cup 2026. Simulation |
| FC24. Penalty | FC24. Penalty |
| FC25. Penalty | FC25. Penalty |
| FC26. Penalty | FC26. Penalty |
| FIFA23. Penalty | FIFA23. Penalty |
| Penalty | Penalty |

---

## 🏆 League Families

### PENALTY
- **Pattern:** `Penalty|penalty`
- **Draws:** No (has_draw: false)
- **Typical Goals:** 3-15
- **Characteristics:** Penalty shootouts, 2 outcomes only, high scores

**Leagues:**
- FC24. Penalty
- FC25. Penalty
- FC26. Penalty
- FIFA23. Penalty
- Penalty

### HIGHSCORE
- **Pattern:** `3x3|4x4`
- **Draws:** Yes (has_draw: true)
- **Typical Goals:** 8-22
- **Characteristics:** 3x3/4x4 formats, very high scores (~15 goals/match)

**Leagues:**
- FC 24. 4x4. Championnat d'Angleterre
- FC 25. 3x3. Ligue de conférence

### RUSH
- **Pattern:** `Rush`
- **Draws:** Yes (has_draw: true)
- **Typical Goals:** 3-14
- **Characteristics:** 5x5 Rush format, intermediate profile, high variance

**Leagues:**
- FC 26. 5x5 Rush. Superligue

### CLASSIC
- **Pattern:** `None` (everything else)
- **Draws:** Yes (has_draw: true)
- **Typical Goals:** 0-8
- **Characteristics:** Classic championships, close to real football

**Leagues:**
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

## 🎯 Platform-Specific Option Mapping

### Overview
The API maps continuous model predictions to discrete platform-specific options for each league family.

### How It Works
1. **Continuous Prediction**: The model predicts a continuous value (e.g., total_goals = 8.6)
2. **Platform Mapping**: The API finds the closest available option on the platform for that family
3. **Family-Specific Options**: Each family has its own set of available options

### Platform Options by Family

#### PENALTY
- **Total Goals**: 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5
- **Handicap**: -4.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0
- **Over/Under**: 5.5, 6.5, 7.5, 8.5, 9.5

#### HIGHSCORE
- **Total Goals**: 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5, 21.5, 22.5, 23.5, 24.5, 25.5
- **Handicap**: -8.0, -7.5, -7.0, -6.5, -6.0, -5.5, -5.0, -4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0
- **Over/Under**: 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5

#### RUSH
- **Total Goals**: 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5
- **Handicap**: -5.0, -4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0
- **Over/Under**: 6.5, 7.5, 8.5, 9.5, 10.5, 11.5

#### CLASSIC
- **Total Goals**: 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5
- **Handicap**: -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0
- **Over/Under**: 2.5, 3.5, 4.5, 5.5, 6.5

### Example
```json
{
  "total_goals": {
    "predicted": 8.6,
    "platform_value": 8.5,
    "platform_name": "Total Goals"
  }
}
```

---

## 🔒 Dynamic Poisson System

### Overview
The API uses a dynamic Poisson system for exact score prediction, replacing the fixed lambda system from v2.2.0.

### How It Works
1. **Regression Models**: Uses GradientBoostingRegressor models to predict lambda_home and lambda_away based on historical team features
2. **Varied Predictions**: Produces varied exact scores instead of uniform predictions (e.g., no more systematic 1-1 for all matches)
3. **Team Strength**: Preserves relative team strength through dynamic lambda calculation

### Lambda Values
- **lambda_home**: Expected goals for home team (predicted by regression model)
- **lambda_away**: Expected goals for away team (predicted by regression model)
- **Available in**: Response under `meta.lambda_home` and `meta.lambda_away`

### Exact Score Calculation
The exact score is calculated using the Poisson distribution with the predicted lambda values:
```python
from scipy.stats import poisson

# Calculate probability for each possible score
prob = poisson.pmf(home_goals, lambda_home) * poisson.pmf(away_goals, lambda_away)

# Return the score with highest probability
```

---

## 💻 Code Examples

### Python

```python
import requests

BASE_URL = "https://top-modele-train-api-vmp.onrender.com"

# Get prediction
response = requests.post(f"{BASE_URL}/predict", json={
    "team_home": "Chelsea",
    "team_away": "Club Atlético de Madrid",
    "league": "FC 26. 5x5 Rush. Superleague"
})
prediction = response.json()

# Access prediction data
print(f"Match: {prediction['match']}")
print(f"Family: {prediction['family']}")
print(f"Exact Score: {prediction['predictions']['exact_score']['prediction']}")
print(f"Total Goals: {prediction['predictions']['total_goals']['predicted']}")
print(f"Platform Value: {prediction['predictions']['total_goals']['platform_value']}")
print(f"Lambda Home: {prediction['meta']['lambda_home']}")
print(f"Lambda Away: {prediction['meta']['lambda_away']}")
```

### JavaScript/Node.js

```javascript
const BASE_URL = "https://top-modele-train-api-vmp.onrender.com";

// Get prediction
async function getPrediction(teamHome, teamAway, league) {
  const response = await fetch(`${BASE_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      team_home: teamHome,
      team_away: teamAway,
      league: league
    })
  });
  return await response.json();
}

// Usage
const prediction = await getPrediction(
  "Chelsea",
  "Club Atlético de Madrid",
  "FC 26. 5x5 Rush. Superleague"
);

console.log(`Match: ${prediction.match}`);
console.log(`Family: ${prediction.family}`);
console.log(`Exact Score: ${prediction.predictions.exact_score.prediction}`);
console.log(`Total Goals: ${prediction.predictions.total_goals.predicted}`);
console.log(`Platform Value: ${prediction.predictions.total_goals.platform_value}`);
console.log(`Lambda Home: ${prediction.meta.lambda_home}`);
console.log(`Lambda Away: ${prediction.meta.lambda_away}`);
```

### cURL

```bash
# Get prediction
curl -X POST https://top-modele-train-api-vmp.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "team_home": "Chelsea",
    "team_away": "Club Atlético de Madrid",
    "league": "FC 26. 5x5 Rush. Superleague"
  }'
```

---

## 🧪 Testing

### Health Check
```bash
curl https://top-modele-train-api-vmp.onrender.com/health
```

### Test Prediction
```bash
curl -X POST https://top-modele-train-api-vmp.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "team_home": "Chelsea",
    "team_away": "Club Atlético de Madrid",
    "league": "FC 26. 5x5 Rush. Superleague"
  }'
```

---

## 📝 Error Handling

### Error Response Format
```json
{
  "detail": "Error message"
}
```

### Common Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Family or league not found |
| 503 | Service Unavailable | Models not loaded |
| 500 | Internal Server Error | Prediction error |

---

## 🔄 Cache System

### Overview
The API uses Upstash Redis cache for performance optimization.

### Cache Behavior
- **Duration:** 5 minutes per prediction
- **Key Format:** `predict:{team_home}:{team_away}:{league}`
- **Auto-clear:** Use `/clear-cache` endpoint to force recomputation

### Cache Configuration (Optional)
Set these environment variables to enable cache:

```env
UPSTASH_REDIS_REST_URL=https://your-rest-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-token
```

If not configured, the API works without cache.

---

## 📞 Support

For integration support or questions:
- **Production URL:** https://top-modele-train-api-vmp.onrender.com
- **Documentation:** This file
- **Version:** 3.0.0

---

## 📄 License

This API is developed by SOLITAIRE HACK.

---

## 🔄 Migration Guide (v2.2.0 → v3.0.0)

### Breaking Changes

#### 1. Response Structure Changes
**Removed Fields:**
- `history` section (all historical team data)
- `total_goals.over_under` (multiple thresholds)
- `handicap` (multiple thresholds)

**Added Fields:**
- `total_goals.platform_value` (closest platform option)
- `total_goals.platform_name` (option type)
- `handicap.platform_value` (closest platform option)
- `handicap.platform_name` (option type)
- `meta.lambda_home` (Poisson lambda for home team)
- `meta.lambda_away` (Poisson lambda for away team)
- `btts` (Both Teams To Score probabilities)

**Simplified Fields:**
- `over_under` (now single under/over instead of multiple thresholds)
- `handicap` (now single predicted value instead of multiple thresholds)

#### 2. Removed Endpoints
- ❌ `POST /update-history` (no longer supported)
- ❌ `POST /save-history` (no longer supported)

#### 3. New Features
- ✅ Dynamic Poisson system for varied exact score predictions
- ✅ Platform-specific option mapping for each league family
- ✅ League name mapping (EN ↔ FR)

### Migration Steps

1. **Update response parsing:**
```python
# Old (v2.2.0)
total_goals = prediction['predictions']['total_goals']['predicted']
over_under = prediction['predictions']['total_goals']['over_under']['2.5']

# New (v3.0.0)
total_goals = prediction['predictions']['total_goals']['predicted']
platform_value = prediction['predictions']['total_goals']['platform_value']
over_under = prediction['predictions']['over_under']
lambda_home = prediction['meta']['lambda_home']
```

2. **Remove history-related code:**
```python
# Remove these
history = prediction['history']
home_matches = prediction['history']['home_last_matches']

# No longer available in v3.0.0
```

3. **Remove history endpoint calls:**
```python
# Remove these
requests.post(f"{BASE_URL}/update-history", json={...})
requests.post(f"{BASE_URL}/save-history?family=CLASSIC")
```

4. **Update league names:**
The API now automatically maps league names (EN ↔ FR). You can use either format:
- `"FC 26. 5x5 Rush. Superleague"` (EN)
- `"FC 26. 5x5 Rush. Superligue"` (FR)

Both will work correctly.

---

**Last Updated:** 2026-06-19  
**API Version:** 3.0.0  
**Status:** Production ✅
