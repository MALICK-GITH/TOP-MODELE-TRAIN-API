# API INTEGRATION GUIDE - FIFA Virtual Prediction System

**Production URL:** `https://top-modele-train-api-vmp.onrender.com`

**Version:** 5.0.0  
**Last Updated:** 2026-06-21

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
Get prediction for a FIFA match with platform-specific option mapping and confidence scores.

```http
POST /predict
Content-Type: application/json
```

**Request Body:**
```json
{
  "team_home": "Chelsea",
  "team_away": "Club Atlético de Madrid",
  "league": "FC 26. 5x5 Rush. Superligue"
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
      "away": 0.547,
      "confidence": 0.533
    },
    "total_goals": {
      "predicted": 7.5,
      "platform_value": 7.5,
      "platform_name": "Total Goals"
    },
    "handicap": {
      "predicted": -4.2,
      "platform_value": -4.0,
      "platform_name": "Handicap"
    },
    "over_under": {
      "under": 0.336,
      "over": 0.664,
      "confidence": 0.615
    },
    "btts": {
      "no": 0.069,
      "yes": 0.931,
      "confidence": 0.801
    },
    "parity": {
      "pair": 0.481,
      "impair": 0.519,
      "confidence": 0.513
    },
    "score_range": {
      "0-2": 0.048,
      "3-5": 0.306,
      "6-8": 0.322,
      "9+": 0.324,
      "confidence": 0.377
    },
    "double_chance": {
      "1x": 0.371,
      "x2": 0.481,
      "12": 0.149,
      "confidence": 0.486
    },
    "clean_sheet": {
      "home_no": 0.941,
      "home_yes": 0.059,
      "away_no": 0.829,
      "away_yes": 0.171,
      "confidence": 0.769
    },
    "draw_no_bet": {
      "home": 0.018,
      "away": 0.982,
      "draw": 0.0,
      "confidence": 0.838
    },
    "win_both_halves": {
      "no": 0.322,
      "yes": 0.678,
      "confidence": 0.624
    }
  }
}
```

**Key Changes from v4.0.0:**
- ✅ Added `score_range` prediction (0-2, 3-5, 6-8, 9+)
- ✅ Added `double_chance` prediction (1X, X2, 12)
- ✅ Added `clean_sheet` prediction (Home/Away)
- ✅ Added `draw_no_bet` prediction (Home/Away/Draw)
- ✅ Added `win_both_halves` prediction (Yes/No)
- ✅ Added `confidence` scores for all predictions (0.0-1.0)
- ✅ Total Goals and Handicap now use regression models instead of default values

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

### 3. Batch Predict
Get predictions for multiple matches in a single request.

```http
POST /batch-predict
Content-Type: application/json
```

**Request Body:**
```json
{
  "matches": [
    {
      "team_home": "Chelsea",
      "team_away": "Club Atlético de Madrid",
      "league": "FC 26. 5x5 Rush. Superligue"
    },
    {
      "team_home": "Real Madrid",
      "team_away": "Barcelona",
      "league": "FC 25. Champions League"
    }
  ]
}
```

**Response:**
```json
{
  "total": 2,
  "successful": 2,
  "predictions": [
    {
      "match": "Chelsea vs Club Atlético de Madrid",
      "league": "FC 26. 5x5 Rush. Superligue",
      "family": "RUSH",
      "predictions": { ... }
    },
    {
      "match": "Real Madrid vs Barcelona",
      "league": "FC 25. Champions League",
      "family": "CLASSIC",
      "predictions": { ... }
    }
  ]
}
```

---

### 4. Model Info
Get metadata about the loaded models.

```http
GET /model-info
```

**Response:**
```json
{
  "version": "5.0.0",
  "families": ["PENALTY", "HIGHSCORE", "RUSH", "CLASSIC"],
  "models": {
    "PENALTY": {
      "models": ["1x2", "over_under", "btts", "parity", "score_range", "double_chance", "clean_sheet_home", "clean_sheet_away", "total_goals_regressor", "handicap_regressor"],
      "leagues_count": 5,
      "leagues_sample": ["FC24. Penalty", "FC25. Penalty", "Penalty", "FIFA23. Penalty", "FC26. Penalty"],
      "has_regression": true
    },
    "HIGHSCORE": {
      "models": ["1x2", "over_under", "btts", "parity", "score_range", "double_chance", "clean_sheet_home", "clean_sheet_away", "total_goals_regressor", "handicap_regressor"],
      "leagues_count": 2,
      "leagues_sample": ["FC 25. 3x3. Ligue de conférence", "FC 24. 4x4. Championnat d'Angleterre"],
      "has_regression": true
    },
    "RUSH": {
      "models": ["1x2", "over_under", "btts", "parity", "score_range", "double_chance", "clean_sheet_home", "clean_sheet_away", "total_goals_regressor", "handicap_regressor"],
      "leagues_count": 1,
      "leagues_sample": ["FC 26. 5x5 Rush. Superligue"],
      "has_regression": true
    },
    "CLASSIC": {
      "models": ["1x2", "over_under", "btts", "parity", "score_range", "double_chance", "clean_sheet_home", "clean_sheet_away", "total_goals_regressor", "handicap_regressor"],
      "leagues_count": 9,
      "leagues_sample": ["FC 25. Champions League", "FC 26. Champions League", "FC 25. Championnat d'Espagne", "FC 25. Championnat d'Angleterre", "FC 25. Ligue européenne"],
      "has_regression": true
    }
  },
  "cache_enabled": true
}
```

---

### 5. Team Stats
Get statistics for a specific team.

```http
GET /team-stats/{team_name}
```

**Response:**
```json
{
  "team": "Chelsea",
  "total_matches": 170,
  "leagues": [
    {"league": "FC24. Penalty", "family": "PENALTY"},
    {"league": "FC 25. Champions League", "family": "CLASSIC"}
  ],
  "performance": {
    "avg_goals_scored": 3.26,
    "avg_goals_conceded": 3.26,
    "win_rate": 0.45,
    "draw_rate": 0.25,
    "loss_rate": 0.30
  },
  "form": ["W", "D", "W", "L", "W"],
  "note": "Statistiques simulées - nécessite une base de données pour des données réelles"
}
```

---

### 6. League Stats
Get statistics for a specific league.

```http
GET /league-stats/{league_name}
```

**Response:**
```json
{
  "league": "FC 26. 5x5 Rush. Superligue",
  "family": "RUSH",
  "configuration": {
    "has_draw": true,
    "avg_goals": 7.52
  },
  "teams_count": 20,
  "total_matches": 100,
  "goals_per_match": 7.52,
  "draw_rate": 0.25,
  "note": "Statistiques basées sur la configuration de la famille"
}
```

---

### 7. Clear Cache
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

### 8. Get Families
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

### 9. Get Leagues by Family
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

## 🔒 Prediction Models

### Overview
The API uses machine learning models for prediction with confidence scores.

### Available Models
1. **1X2 (Result)**: GradientBoostingClassifier - predicts Home/Draw/Away
2. **Over/Under**: GradientBoostingClassifier - predicts Over/Under based on family-specific thresholds
3. **BTTS (Both Teams To Score)**: RandomForestClassifier - predicts Yes/No
4. **Parity (Odd/Even)**: RandomForestClassifier - predicts Pair/Impair
5. **Score Range**: GradientBoostingClassifier - predicts 0-2, 3-5, 6-8, 9+
6. **Double Chance**: GradientBoostingClassifier - predicts 1X, X2, 12
7. **Clean Sheet Home**: RandomForestClassifier - predicts Home No/Yes
8. **Clean Sheet Away**: RandomForestClassifier - predicts Away No/Yes
9. **Draw No Bet**: GradientBoostingClassifier - predicts Home/Away/Draw
10. **Win Both Halves**: RandomForestClassifier - predicts Yes/No
11. **Total Goals (Regression)**: GradientBoostingRegressor - predicts continuous total goals
12. **Handicap (Regression)**: GradientBoostingRegressor - predicts continuous handicap

### Confidence Scores
All predictions include a confidence score (0.0-1.0) calculated based on:
- Prediction certainty (maximum probability)
- Model accuracy from training
- Higher confidence = more reliable prediction

### Total Goals and Handicap
Total Goals and Handicap now use regression models for more accurate predictions:
- **PENALTY**: Trained on penalty shootout data
- **HIGHSCORE**: Trained on 3x3/4x4 format data
- **RUSH**: Trained on 5x5 Rush format data
- **CLASSIC**: Trained on classic championship data

These predictions are then mapped to platform-specific options using the platform options mapping.

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
    "league": "FC 26. 5x5 Rush. Superligue"
})
prediction = response.json()

# Access prediction data
print(f"Match: {prediction['match']}")
print(f"Family: {prediction['family']}")
print(f"Total Goals: {prediction['predictions']['total_goals']['predicted']}")
print(f"Platform Value: {prediction['predictions']['total_goals']['platform_value']}")
print(f"Handicap: {prediction['predictions']['handicap']['predicted']}")
print(f"1X2: Home={prediction['predictions']['1x2']['home']}, Draw={prediction['predictions']['1x2']['draw']}, Away={prediction['predictions']['1x2']['away']}")
print(f"1X2 Confidence: {prediction['predictions']['1x2']['confidence']}")
print(f"Score Range: 0-2={prediction['predictions']['score_range']['0-2']}, 3-5={prediction['predictions']['score_range']['3-5']}")
print(f"Double Chance: 1X={prediction['predictions']['double_chance']['1x']}, X2={prediction['predictions']['double_chance']['x2']}")
print(f"Clean Sheet: Home No={prediction['predictions']['clean_sheet']['home_no']}, Away No={prediction['predictions']['clean_sheet']['away_no']}")
print(f"Draw No Bet: Home={prediction['predictions']['draw_no_bet']['home']}, Away={prediction['predictions']['draw_no_bet']['away']}")
print(f"Win Both Halves: Yes={prediction['predictions']['win_both_halves']['yes']}")
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
  "FC 26. 5x5 Rush. Superligue"
);

console.log(`Match: ${prediction.match}`);
console.log(`Family: ${prediction.family}`);
console.log(`Total Goals: ${prediction.predictions.total_goals.predicted}`);
console.log(`Platform Value: ${prediction.predictions.total_goals.platform_value}`);
console.log(`Handicap: ${prediction.predictions.handicap.predicted}`);
console.log(`1X2: Home=${prediction.predictions['1x2'].home}, Draw=${prediction.predictions['1x2'].draw}, Away=${prediction.predictions['1x2'].away}`);
console.log(`1X2 Confidence: ${prediction.predictions['1x2'].confidence}`);
console.log(`Score Range: 0-2=${prediction.predictions.score_range['0-2']}, 3-5=${prediction.predictions.score_range['3-5']}`);
console.log(`Double Chance: 1X=${prediction.predictions.double_chance['1x']}, X2=${prediction.predictions.double_chance['x2']}`);
console.log(`Clean Sheet: Home No=${prediction.predictions.clean_sheet.home_no}, Away No=${prediction.predictions.clean_sheet.away_no}`);
console.log(`Draw No Bet: Home=${prediction.predictions.draw_no_bet.home}, Away=${prediction.predictions.draw_no_bet.away}`);
console.log(`Win Both Halves: Yes=${prediction.predictions.win_both_halves.yes}`);
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
- **Version:** 5.0.0

---

## 📄 License

This API is developed by SOLITAIRE HACK.

---

## 🔄 Migration Guide (v4.0.0 → v5.0.0)

### Breaking Changes

#### 1. Response Structure Changes
**New Fields:**
- `score_range` prediction (0-2, 3-5, 6-8, 9+)
- `double_chance` prediction (1X, X2, 12)
- `clean_sheet` prediction (Home/Away)
- `draw_no_bet` prediction (Home/Away/Draw)
- `win_both_halves` prediction (Yes/No)
- `confidence` scores for all predictions (0.0-1.0)

**Modified Fields:**
- All prediction fields now include a `confidence` score
- `total_goals.predicted` now uses regression models instead of default values
- `handicap.predicted` now uses regression models instead of default values

**Unchanged Fields:**
- `1x2` (still predicted by GradientBoostingClassifier)
- `over_under` (still predicted by GradientBoostingClassifier)
- `btts` (still predicted by RandomForestClassifier)
- `parity` (still predicted by RandomForestClassifier)
- `platform_value` and `platform_name` (still mapped to platform-specific options)

#### 2. Model Changes
**New Models:**
- `score_range` (GradientBoostingClassifier)
- `double_chance` (GradientBoostingClassifier)
- `clean_sheet_home` (RandomForestClassifier)
- `clean_sheet_away` (RandomForestClassifier)
- `draw_no_bet` (GradientBoostingClassifier)
- `win_both_halves` (RandomForestClassifier)
- `total_goals_regressor` (GradientBoostingRegressor)
- `handicap_regressor` (GradientBoostingRegressor)

**Existing Models:**
- `1x2` (GradientBoostingClassifier)
- `over_under` (GradientBoostingClassifier)
- `btts` (RandomForestClassifier)
- `parity` (RandomForestClassifier)

#### 3. New Behavior
- Total Goals and Handicap now use regression models for more accurate predictions
- All predictions include confidence scores (0.0-1.0)
- New endpoints available: `/batch-predict`, `/model-info`, `/team-stats`, `/league-stats`

### Migration Steps

1. **Update response parsing:**
```python
# Old (v4.0.0)
total_goals = prediction['predictions']['total_goals']['predicted']

# New (v5.0.0)
total_goals = prediction['predictions']['total_goals']['predicted']
confidence = prediction['predictions']['total_goals']['confidence']  # Note: regression models don't have confidence
score_range = prediction['predictions']['score_range']
double_chance = prediction['predictions']['double_chance']
clean_sheet = prediction['predictions']['clean_sheet']
draw_no_bet = prediction['predictions']['draw_no_bet']
win_both_halves = prediction['predictions']['win_both_halves']
```

2. **Update prediction logic:**
```python
# Old (v4.0.0)
# Used family-specific default values for Total Goals and Handicap

# New (v5.0.0)
# Uses regression models for more accurate Total Goals and Handicap predictions
# All predictions include confidence scores
```

3. **Update UI:**
```python
# Add new prediction displays to your UI:
# - Score Range (0-2, 3-5, 6-8, 9+)
# - Double Chance (1X, X2, 12)
# - Clean Sheet (Home/Away)
# - Draw No Bet (Home/Away/Draw)
# - Win Both Halves (Yes/No)
# - Confidence scores for all predictions
```

---

**Last Updated:** 2026-06-21  
**API Version:** 5.0.0  
**Status:** Production ✅
