"""
FIFA Virtual Prediction API
===========================
API REST pour les prédictions de matchs FIFA virtuels.

Endpoints:
  - GET  /health          : Vérifier la santé de l'API
  - POST /predict         : Prédire le résultat d'un match
  - POST /update-history  : Mettre à jour l'historique avec un match terminé
  - GET  /families        : Lister les familles disponibles
  - GET  /leagues         : Lister les ligues par famille

Usage:
  uvicorn api:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import os
import sys

# Ajouter le répertoire courant au path pour importer train_random_forest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from platform_options_mapping import map_prediction_to_platform, FAMILY_OPTIONS
import pickle
import pandas as pd
import numpy as np
from scipy.stats import poisson

# ──────────────────────────────────────────────────────────────────────────────
# Configuration des familles de ligues
# ──────────────────────────────────────────────────────────────────────────────

FAMILIES = {
    "PENALTY": {
        "leagues": ["FC24. Penalty", "FC25. Penalty", "Penalty", "FIFA23. Penalty", "FC26. Penalty"],
        "has_draw": True,
        "avg_goals": 6.52
    },
    "HIGHSCORE": {
        "leagues": ["FC 25. 3x3. Ligue de conférence", "FC 24. 4x4. Championnat d'Angleterre"],
        "has_draw": True,
        "avg_goals": 15.16
    },
    "RUSH": {
        "leagues": ["FC 26. 5x5 Rush. Superligue"],
        "has_draw": True,
        "avg_goals": 7.52
    },
    "CLASSIC": {
        "leagues": [
            "FC 25. Champions League",
            "FC 26. Champions League",
            "FC 25. Championnat d'Espagne",
            "FC 25. Championnat d'Angleterre",
            "FC 25. Ligue européenne",
            "FC 26. Championnat du monde",
            "FC 25. Italy Championship",
            "FC 25. Championnat d'Allemagne",
            "World Cup 2026. Simulation"
        ],
        "has_draw": True,
        "avg_goals": 3.12
    }
}

def map_league(league: str) -> str:
    """Mappe une ligue live (EN) vers la ligue entraînée correspondante (FR)."""
    # Mapping API (EN) ↔ CSV (FR)
    league_mapping = {
        "FC 24. 4x4. England Championship": "FC 24. 4x4. Championnat d'Angleterre",
        "FC 25. 3x3. Conference League": "FC 25. 3x3. Ligue de conférence",
        "FC 25. England Championship": "FC 25. Championnat d'Angleterre",
        "FC 25. Champions League": "FC 25. Champions League",
        "FC 25. Europe League": "FC 25. Ligue européenne",
        "FC 25. Italy Championship": "FC 25. Italy Championship",
        "FC 26. 5x5 Rush. Superleague": "FC 26. 5x5 Rush. Superligue",
        "FC 26. Champions League": "FC 26. Champions League",
        "FC 26. World Championship": "FC 26. Championnat du monde"
    }
    
    # Si la ligue est dans le mapping, retourner la version FR
    if league in league_mapping:
        return league_mapping[league]
    
    # Sinon, retourner la ligue telle quelle
    return league

# Import du cache Upstash (optionnel)
try:
    from upstash_cache import get_cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    print("⚠️  Cache Upstash non disponible (upstash_redis non installé)")

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

MODELS_DIR = "./models"
app = FastAPI(
    title="FIFA Virtual Prediction API",
    description="API de prédiction pour matchs FIFA virtuels avec système Poisson dynamique",
    version="3.0.0"
)

# ──────────────────────────────────────────────────────────────────────────────
# Chargement des modèles trainBest.py
# ──────────────────────────────────────────────────────────────────────────────

def load_trainbest_models(model_dir="models"):
    """Charge les modèles entraînés avec trainBest.py"""
    models = {}
    for family in ["PENALTY", "HIGHSCORE", "RUSH", "CLASSIC"]:
        model_path = f"{model_dir}/{family}.pkl"
        try:
            with open(model_path, "rb") as f:
                models[family] = pickle.load(f)
            print(f"✅ {family} chargé")
        except FileNotFoundError:
            print(f"❌ {family} non trouvé")
    return models

def predict_with_trainbest_models(team_home, team_away, league, models):
    """Prédit en utilisant les modèles trainBest.py avec Poisson dynamique"""
    # Déterminer la famille
    family = None
    for fam, fam_data in FAMILIES.items():
        if league in fam_data["leagues"]:
            family = fam
            break
    
    if family is None:
        raise ValueError(f"Ligue {league} non trouvée dans aucune famille")
    
    if family not in models:
        raise ValueError(f"Modèle pour {family} non chargé")
    
    model_data = models[family]
    
    # Créer des features fictifs (à remplacer par de vrais features historiques)
    features = {}
    for feat in model_data["features"]:
        if "n" in feat:
            features[feat] = 10
        elif "wr" in feat or "pts" in feat or "form" in feat:
            features[feat] = 0.5
        elif "gf" in feat or "ga" in feat or "tot" in feat:
            features[feat] = 1.5
        elif "h2h" in feat:
            features[feat] = 0.5
        elif "diff" in feat:
            features[feat] = 0.0
        else:
            features[feat] = 0.5
    
    X = pd.DataFrame([features])
    
    # Prédire 1X2
    model_1x2 = model_data["models"]["1x2"]
    prob_1x2 = model_1x2.predict_proba(X)[0]
    
    # Prédire Over/Under
    model_ou = model_data["models"]["over_under"]
    prob_ou = model_ou.predict_proba(X)[0]
    
    # Prédire BTTS
    model_btts = model_data["models"]["btts"]
    prob_btts = model_btts.predict_proba(X)[0]
    
    # Prédire Parité
    model_parity = model_data["models"]["parity"]
    prob_parity = model_parity.predict_proba(X)[0]
    
    # Score exact désactivé - plus de calcul Poisson
    # Calculer Total Goals et Handicap basés sur les probabilités 1X2
    # Valeurs par famille pour total_goals et handicap
    family_defaults = {
        "PENALTY": {"total_goals": 6.5, "handicap": 0.0},
        "HIGHSCORE": {"total_goals": 15.0, "handicap": 0.0},
        "RUSH": {"total_goals": 7.5, "handicap": 0.0},
        "CLASSIC": {"total_goals": 3.1, "handicap": 0.0}
    }
    
    defaults = family_defaults.get(family, {"total_goals": 3.0, "handicap": 0.0})
    total_goals_pred = defaults["total_goals"]
    handicap_pred = defaults["handicap"]
    
    # Mapper aux options de la plateforme
    handicap_opt_value, handicap_opt_name = map_prediction_to_platform("handicap", handicap_pred, family)
    total_goals_opt_value, total_goals_opt_name = map_prediction_to_platform("total_goals", total_goals_pred, family)
    
    # Construire la réponse
    return {
        "match": f"{team_home} vs {team_away}",
        "league": league,
        "family": family,
        "predictions": {
            "1x2": {
                "home": round(prob_1x2[0], 3),
                "draw": round(prob_1x2[1], 3),
                "away": round(prob_1x2[2], 3)
            },
            "total_goals": {
                "predicted": total_goals_pred,
                "platform_value": total_goals_opt_value,
                "platform_name": total_goals_opt_name
            },
            "handicap": {
                "predicted": handicap_pred,
                "platform_value": handicap_opt_value,
                "platform_name": handicap_opt_name
            },
            "over_under": {
                "under": round(prob_ou[0], 3),
                "over": round(prob_ou[1], 3)
            },
            "btts": {
                "no": round(prob_btts[0], 3),
                "yes": round(prob_btts[1], 3)
            },
            "parity": {
                "pair": round(prob_parity[0], 3),
                "impair": round(prob_parity[1], 3)
            }
        }
    }

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loader de modèles trainBest.py (singleton)
trainbest_models = None

# Cache Upstash (singleton)
cache_instance = None

# ──────────────────────────────────────────────────────────────────────────────
# Pydantic Models
# ──────────────────────────────────────────────────────────────────────────────

class PredictionRequest(BaseModel):
    team_home: str = Field(..., description="Équipe domicile")
    team_away: str = Field(..., description="Équipe extérieur")
    league: str = Field(..., description="Nom de la ligue/championnat")

class UpdateHistoryRequest(BaseModel):
    team_home: str = Field(..., description="Équipe domicile")
    team_away: str = Field(..., description="Équipe extérieur")
    league: str = Field(..., description="Nom de la ligue/championnat")
    score_home: int = Field(..., description="Score domicile")
    score_away: int = Field(..., description="Score extérieur")
    finished_at: str = Field(..., description="Date de fin (ISO8601)")
    family: Optional[str] = Field(None, description="Famille (optionnel, auto-détectée)")

class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    families: List[str]

class FamiliesResponse(BaseModel):
    families: Dict[str, Dict]

# ──────────────────────────────────────────────────────────────────────────────
# Lifecycle
# ──────────────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    """Charge les modèles au démarrage de l'API."""
    global trainbest_models, cache_instance
    print("🚀 Démarrage de l'API FIFA Prediction...")
    print(f"📂 Répertoire des modèles: {MODELS_DIR}")
    
    # Charger les modèles trainBest.py
    trainbest_models = load_trainbest_models(MODELS_DIR)
    
    # Initialiser le cache Upstash si disponible
    if CACHE_AVAILABLE:
        try:
            cache_instance = get_cache()
            if cache_instance.ping():
                print("✅ Cache Upstash initialisé")
            else:
                print("⚠️  Cache Upstash non disponible (connexion échouée)")
                cache_instance = None
        except Exception as e:
            print(f"⚠️  Cache Upstash non disponible: {e}")
            cache_instance = None
    
    print("✅ API prête")

# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health():
    """Vérifie la santé de l'API et le chargement des modèles."""
    if trainbest_models is None:
        return HealthResponse(
            status="initializing",
            models_loaded=False,
            families=[]
        )
    
    return HealthResponse(
        status="healthy",
        models_loaded=len(trainbest_models) > 0,
        families=list(trainbest_models.keys())
    )

@app.get("/families", response_model=FamiliesResponse)
async def get_families():
    """Retourne la liste des familles disponibles avec leur configuration."""
    return FamiliesResponse(families=FAMILIES)

@app.get("/leagues/{family}")
async def get_leagues(family: str):
    """Retourne la liste des ligues pour une famille donnée."""
    if trainbest_models is None:
        raise HTTPException(status_code=503, detail="Modèles non chargés")
    
    if family not in trainbest_models:
        raise HTTPException(status_code=404, detail=f"Famille {family} non trouvée")
    
    model_data = trainbest_models[family]
    return {"family": family, "leagues": model_data.get("leagues", [])}

@app.post("/predict")
async def predict(request: PredictionRequest):
    """
    Prédit le résultat d'un match FIFA virtuel avec système Poisson dynamique.
    
    Cette endpoint utilise les modèles de machine learning entraînés avec trainBest.py
    et applique un système Poisson dynamique pour prédire les lambdas home/away en fonction
    des features historiques des équipes.
    
    Les prédictions sont mappées aux options spécifiques de chaque famille de ligue,
    garantissant qu'elles correspondent aux options disponibles sur la plateforme.
    
    Retourne:
      - match: Nom du match formaté
      - league: Nom de la ligue
      - family: Famille détectée automatiquement (PENALTY, HIGHSCORE, RUSH, CLASSIC)
      - predictions.1x2: Probabilités pour Home/Draw/Away
      - predictions.total_goals: Total de buts prédit avec valeur plateforme
      - predictions.handicap: Handicap prédit avec valeur plateforme
      - predictions.over_under: Probabilités over/under
      - predictions.btts: Probabilités Both Teams To Score
      - predictions.parity: Probabilités pair/impair
      - predictions.exact_score: Score exact le plus probable
      - meta: Lambdas Poisson utilisés
    """
    if trainbest_models is None:
        raise HTTPException(status_code=503, detail="Modèles non chargés")
    
    try:
        # Map la ligue live vers la ligue entraînée
        mapped_league = map_league(request.league)
        
        # Générer la clé de cache
        cache_key = f"predict:{request.team_home}:{request.team_away}:{mapped_league}"
        
        # Essayer de récupérer du cache
        if cache_instance:
            cached_result = cache_instance.get(cache_key)
            if cached_result:
                return cached_result
        
        # Calculer la prédiction avec Poisson dynamique
        prediction = predict_with_trainbest_models(
            team_home=request.team_home,
            team_away=request.team_away,
            league=mapped_league,
            models=trainbest_models
        )
        
        # Stocker dans le cache (5 minutes)
        if cache_instance:
            cache_instance.set(cache_key, prediction, ttl=300)
        
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

@app.post("/clear-cache")
async def clear_cache():
    """
    Nettoie le cache des prédictions.
    
    Utile pour forcer le recalcul des prédictions après une mise à jour des modèles.
    """
    if cache_instance is None:
        raise HTTPException(status_code=503, detail="Cache non disponible")
    
    try:
        # Nettoyer toutes les clés de prédictions
        cache_instance.clear_pattern("predict:*")
        return {"status": "success", "message": "Cache nettoyé"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de nettoyage: {str(e)}")

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
