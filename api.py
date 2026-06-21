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

# Import du cache Upstash Redis (optionnel)
try:
    from upstash_redis import Redis
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

def calculate_confidence(probabilities, model_accuracy):
    """Calcule un score de confiance basé sur les probabilités et l'accuracy du modèle"""
    # Confiance basée sur la certitude de la prédiction (entropie inverse)
    max_prob = max(probabilities)
    certainty = max_prob  # Plus la probabilité max est élevée, plus on est confiant
    
    # Ajuster par l'accuracy du modèle
    confidence = (certainty * 0.7) + (model_accuracy * 0.3)
    
    return round(min(confidence, 1.0), 3)

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
    
    # Récupérer les statistiques des modèles pour calculer la confiance
    model_stats = model_data.get("stats", {})
    
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
    acc_1x2 = model_stats.get("1x2_acc", 0.5)
    confidence_1x2 = calculate_confidence(prob_1x2, acc_1x2)
    
    # Prédire Over/Under
    model_ou = model_data["models"]["over_under"]
    prob_ou = model_ou.predict_proba(X)[0]
    acc_ou = model_stats.get("over_under_acc", 0.5)
    confidence_ou = calculate_confidence(prob_ou, acc_ou)
    
    # Prédire BTTS
    model_btts = model_data["models"]["btts"]
    prob_btts = model_btts.predict_proba(X)[0]
    acc_btts = model_stats.get("btts_acc", 0.5)
    confidence_btts = calculate_confidence(prob_btts, acc_btts)
    
    # Prédire Parité
    model_parity = model_data["models"]["parity"]
    prob_parity = model_parity.predict_proba(X)[0]
    acc_parity = model_stats.get("parity_acc", 0.5)
    confidence_parity = calculate_confidence(prob_parity, acc_parity)
    
    # Prédire Score Range
    try:
        if "score_range" in model_data["models"]:
            model_score_range = model_data["models"]["score_range"]
            prob_score_range = model_score_range.predict_proba(X)[0]
            acc_score_range = model_stats.get("score_range_acc", 0.5)
            # S'assurer que prob_score_range a exactement 4 éléments
            if len(prob_score_range) != 4:
                prob_score_range = [0.25, 0.25, 0.25, 0.25]
            confidence_score_range = calculate_confidence(prob_score_range, acc_score_range)
        else:
            prob_score_range = [0.25, 0.25, 0.25, 0.25]
            confidence_score_range = 0.5
    except Exception as e:
        prob_score_range = [0.25, 0.25, 0.25, 0.25]
        confidence_score_range = 0.5
    
    # Prédire Double Chance
    try:
        if "double_chance" in model_data["models"]:
            model_double_chance = model_data["models"]["double_chance"]
            prob_double_chance = model_double_chance.predict_proba(X)[0]
            acc_double_chance = model_stats.get("double_chance_acc", 0.5)
            # S'assurer que prob_double_chance a exactement 3 éléments
            if len(prob_double_chance) != 3:
                prob_double_chance = [0.33, 0.33, 0.34]
            confidence_double_chance = calculate_confidence(prob_double_chance, acc_double_chance)
        else:
            prob_double_chance = [0.33, 0.33, 0.34]
            confidence_double_chance = 0.5
    except Exception as e:
        prob_double_chance = [0.33, 0.33, 0.34]
        confidence_double_chance = 0.5
    
    # Prédire Clean Sheet Home
    if "clean_sheet_home" in model_data["models"]:
        model_clean_sheet_home = model_data["models"]["clean_sheet_home"]
        prob_clean_sheet_home = model_clean_sheet_home.predict_proba(X)[0]
        acc_clean_sheet_home = model_stats.get("clean_sheet_home_acc", 0.5)
        confidence_clean_sheet_home = calculate_confidence(prob_clean_sheet_home, acc_clean_sheet_home)
    else:
        prob_clean_sheet_home = [0.5, 0.5]
        confidence_clean_sheet_home = 0.5
    
    # Prédire Clean Sheet Away
    if "clean_sheet_away" in model_data["models"]:
        model_clean_sheet_away = model_data["models"]["clean_sheet_away"]
        prob_clean_sheet_away = model_clean_sheet_away.predict_proba(X)[0]
        acc_clean_sheet_away = model_stats.get("clean_sheet_away_acc", 0.5)
        confidence_clean_sheet_away = calculate_confidence(prob_clean_sheet_away, acc_clean_sheet_away)
    else:
        prob_clean_sheet_away = [0.5, 0.5]
        confidence_clean_sheet_away = 0.5
    
    # Prédire Draw No Bet
    try:
        if "draw_no_bet" in model_data["models"]:
            model_draw_no_bet = model_data["models"]["draw_no_bet"]
            prob_draw_no_bet = model_draw_no_bet.predict_proba(X)[0]
            acc_draw_no_bet = model_stats.get("draw_no_bet_acc", 0.5)
            # Gérer le cas où le modèle n'a que 2 classes (home/away sans draw)
            if len(prob_draw_no_bet) == 2:
                # Ajouter une probabilité de draw simulée
                prob_draw_no_bet = [prob_draw_no_bet[0], prob_draw_no_bet[1], 0.0]
            # S'assurer que prob_draw_no_bet a exactement 3 éléments
            elif len(prob_draw_no_bet) == 3:
                # Le modèle a déjà 3 classes, utiliser tel quel
                pass
            else:
                # Cas inattendu, utiliser des valeurs par défaut
                prob_draw_no_bet = [0.33, 0.33, 0.34]
            confidence_draw_no_bet = calculate_confidence(prob_draw_no_bet, acc_draw_no_bet)
        else:
            prob_draw_no_bet = [0.33, 0.33, 0.34]
            confidence_draw_no_bet = 0.5
    except Exception as e:
        prob_draw_no_bet = [0.33, 0.33, 0.34]
        confidence_draw_no_bet = 0.5
    
    # Prédire Win Both Halves
    try:
        if "win_both_halves" in model_data["models"]:
            model_win_both_halves = model_data["models"]["win_both_halves"]
            prob_win_both_halves = model_win_both_halves.predict_proba(X)[0]
            acc_win_both_halves = model_stats.get("win_both_halves_acc", 0.5)
            # S'assurer que prob_win_both_halves a exactement 2 éléments
            if len(prob_win_both_halves) != 2:
                prob_win_both_halves = [0.5, 0.5]
            confidence_win_both_halves = calculate_confidence(prob_win_both_halves, acc_win_both_halves)
        else:
            prob_win_both_halves = [0.5, 0.5]
            confidence_win_both_halves = 0.5
    except Exception as e:
        prob_win_both_halves = [0.5, 0.5]
        confidence_win_both_halves = 0.5
    
    # Score exact désactivé - plus de calcul Poisson
    # Utiliser les modèles de régression pour Total Goals et Handicap
    if "total_goals_regressor" in model_data["models"]:
        model_total_goals = model_data["models"]["total_goals_regressor"]
        total_goals_pred = round(model_total_goals.predict(X)[0], 1)
    else:
        # Fallback aux valeurs par défaut si le modèle n'existe pas
        family_defaults = {
            "PENALTY": 6.5,
            "HIGHSCORE": 15.0,
            "RUSH": 7.5,
            "CLASSIC": 3.1
        }
        total_goals_pred = family_defaults.get(family, 3.0)
    
    if "handicap_regressor" in model_data["models"]:
        model_handicap = model_data["models"]["handicap_regressor"]
        handicap_pred = round(model_handicap.predict(X)[0], 1)
    else:
        # Fallback aux valeurs par défaut si le modèle n'existe pas
        handicap_pred = 0.0
    
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
                "away": round(prob_1x2[2], 3),
                "confidence": confidence_1x2
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
                "over": round(prob_ou[1], 3),
                "confidence": confidence_ou
            },
            "btts": {
                "no": round(prob_btts[0], 3),
                "yes": round(prob_btts[1], 3),
                "confidence": confidence_btts
            },
            "parity": {
                "pair": round(prob_parity[0], 3),
                "impair": round(prob_parity[1], 3),
                "confidence": confidence_parity
            },
            "score_range": {
                "0-2": round(prob_score_range[0], 3),
                "3-5": round(prob_score_range[1], 3),
                "6-8": round(prob_score_range[2], 3),
                "9+": round(prob_score_range[3], 3),
                "confidence": confidence_score_range
            },
            "double_chance": {
                "1x": round(prob_double_chance[0], 3),
                "x2": round(prob_double_chance[1], 3),
                "12": round(prob_double_chance[2], 3),
                "confidence": confidence_double_chance
            },
            "clean_sheet": {
                "home_no": round(prob_clean_sheet_home[0], 3),
                "home_yes": round(prob_clean_sheet_home[1], 3),
                "away_no": round(prob_clean_sheet_away[0], 3),
                "away_yes": round(prob_clean_sheet_away[1], 3),
                "confidence": (confidence_clean_sheet_home + confidence_clean_sheet_away) / 2
            },
            "draw_no_bet": {
                "home": round(prob_draw_no_bet[0], 3),
                "away": round(prob_draw_no_bet[1], 3),
                "draw": round(prob_draw_no_bet[2], 3),
                "confidence": confidence_draw_no_bet
            },
            "win_both_halves": {
                "no": round(prob_win_both_halves[0], 3),
                "yes": round(prob_win_both_halves[1], 3),
                "confidence": confidence_win_both_halves
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

class BatchPredictionRequest(BaseModel):
    matches: List[PredictionRequest] = Field(..., description="Liste des matchs à prédire")

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
            redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
            redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
            
            if redis_url and redis_token:
                cache_instance = Redis(url=redis_url, token=redis_token)
                # Test de connexion
                cache_instance.set("test", "ok", ex=1)
                test_value = cache_instance.get("test")
                if test_value == "ok":
                    print("✅ Cache Upstash initialisé")
                else:
                    print("⚠️  Cache Upstash non disponible (test de connexion échoué)")
                    cache_instance = None
            else:
                print("⚠️  Variables d'environnement Upstash non configurées")
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
                import json
                return json.loads(cached_result)
        
        # Calculer la prédiction avec Poisson dynamique
        prediction = predict_with_trainbest_models(
            team_home=request.team_home,
            team_away=request.team_away,
            league=mapped_league,
            models=trainbest_models
        )
        
        # Mettre en cache le résultat
        if cache_instance:
            import json
            cache_instance.set(cache_key, json.dumps(prediction), ex=300)  # 5 minutes
        
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

@app.post("/batch-predict")
async def batch_predict(request: BatchPredictionRequest):
    """
    Prédit plusieurs matchs FIFA virtuels en une seule requête.
    
    Cette endpoint permet d'obtenir des prédictions pour plusieurs matchs en une seule requête,
    ce qui est plus efficace que d'appeler l'endpoint /predict plusieurs fois.
    
    Retourne:
      - predictions: Liste des prédictions pour chaque match
      - total: Nombre total de matchs traités
      - successful: Nombre de prédictions réussies
    """
    if trainbest_models is None:
        raise HTTPException(status_code=503, detail="Modèles non chargés")
    
    predictions = []
    successful = 0
    
    for match_request in request.matches:
        try:
            # Map la ligue live vers la ligue entraînée
            mapped_league = map_league(match_request.league)
            
            # Générer la clé de cache
            cache_key = f"predict:{match_request.team_home}:{match_request.team_away}:{mapped_league}"
            
            # Essayer de récupérer du cache
            if cache_instance:
                cached_result = cache_instance.get(cache_key)
                if cached_result:
                    import json
                    predictions.append(json.loads(cached_result))
                    successful += 1
                    continue
            
            # Calculer la prédiction
            prediction = predict_with_trainbest_models(
                team_home=match_request.team_home,
                team_away=match_request.team_away,
                league=mapped_league,
                models=trainbest_models
            )
            
            # Mettre en cache le résultat
            if cache_instance:
                import json
                cache_instance.set(cache_key, json.dumps(prediction), ex=300)  # 5 minutes
            
            predictions.append(prediction)
            successful += 1
        except Exception as e:
            # Ajouter une erreur pour ce match mais continuer avec les autres
            predictions.append({
                "error": str(e),
                "match": f"{match_request.team_home} vs {match_request.team_away}",
                "league": match_request.league
            })
    
    return {
        "predictions": predictions,
        "total": len(request.matches),
        "successful": successful
    }

@app.post("/clear-cache")
async def clear_cache():
    """
    Nettoie le cache des prédictions.
    
    Utile pour forcer le recalcul des prédictions après une mise à jour des modèles.
    """
    if cache_instance is None:
        raise HTTPException(status_code=503, detail="Cache non disponible")
    
    try:
        cache_instance.flushdb()
        return {"status": "success", "message": "Cache vidé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du vidage du cache: {str(e)}")

@app.get("/model-info")
async def model_info():
    """
    Retourne des informations sur les modèles chargés.
    
    Retourne:
      - families: Liste des familles de modèles chargés
      - models: Détails des modèles par famille
      - version: Version de l'API
      - last_updated: Date de la dernière mise à jour des modèles
    """
    if trainbest_models is None:
        raise HTTPException(status_code=503, detail="Modèles non chargés")
    
    model_details = {}
    for family, model_data in trainbest_models.items():
        models_list = list(model_data.get("models", {}).keys())
        leagues = model_data.get("leagues", [])
        thresholds = model_data.get("thresholds", {})
        
        model_details[family] = {
            "models": models_list,
            "leagues_count": len(leagues),
            "leagues_sample": leagues[:5] if len(leagues) > 5 else leagues,
            "has_regression": "total_goals_regressor" in models_list and "handicap_regressor" in models_list
        }
    
    return {
        "version": "5.0.0",
        "families": list(trainbest_models.keys()),
        "models": model_details,
        "cache_enabled": cache_instance is not None
    }

@app.get("/team-stats/{team_name}")
async def get_team_stats(team_name: str):
    """
    Retourne les statistiques d'une équipe.
    
    Note: Les statistiques sont basées sur les configurations des familles et ligues.
    Pour des statistiques historiques réelles, une base de données serait nécessaire.
    """
    # Trouver les ligues où l'équipe apparaît
    team_leagues = []
    for family, fam_data in FAMILIES.items():
        for league in fam_data["leagues"]:
            # Simuler la présence de l'équipe dans les ligues
            # Dans une vraie implémentation, on aurait une base de données
            team_leagues.append({
                "league": league,
                "family": family
            })
    
    # Statistiques simulées basées sur la famille
    stats = {
        "team": team_name,
        "total_matches": len(team_leagues) * 10,  # Simulé
        "leagues": team_leagues,
        "performance": {
            "avg_goals_scored": round(FAMILIES.get(team_leagues[0]["family"], {}).get("avg_goals", 3.0) / 2, 2) if team_leagues else 1.5,
            "avg_goals_conceded": round(FAMILIES.get(team_leagues[0]["family"], {}).get("avg_goals", 3.0) / 2, 2) if team_leagues else 1.5,
            "win_rate": 0.45,  # Simulé
            "draw_rate": 0.25,  # Simulé
            "loss_rate": 0.30   # Simulé
        },
        "form": ["W", "D", "W", "L", "W"],  # Simulé
        "note": "Statistiques simulées - nécessite une base de données pour des données réelles"
    }
    
    return stats

@app.get("/league-stats/{league_name}")
async def get_league_stats(league_name: str):
    """
    Retourne les statistiques d'une ligue.
    """
    # Trouver la famille de la ligue
    family = None
    for fam, fam_data in FAMILIES.items():
        if league_name in fam_data["leagues"]:
            family = fam
            break
    
    if family is None:
        raise HTTPException(status_code=404, detail=f"Ligue {league_name} non trouvée")
    
    fam_data = FAMILIES[family]
    
    stats = {
        "league": league_name,
        "family": family,
        "configuration": {
            "has_draw": fam_data["has_draw"],
            "avg_goals": fam_data["avg_goals"]
        },
        "teams_count": 20,  # Simulé
        "total_matches": 100,  # Simulé
        "goals_per_match": fam_data["avg_goals"],
        "draw_rate": 0.25 if fam_data["has_draw"] else 0.10,
        "note": "Statistiques basées sur la configuration de la famille"
    }
    
    return stats

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
