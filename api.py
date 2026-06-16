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

from train_random_forest import ModelLoader, FAMILIES, map_league

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
    description="API de prédiction pour matchs FIFA virtuels avec règles de cohérence globale",
    version="2.2.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loader de modèles (singleton)
model_loader = None

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
    global model_loader, cache_instance
    print("🚀 Démarrage de l'API FIFA Prediction...")
    model_loader = ModelLoader(MODELS_DIR)
    model_loader.load_all()
    
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
    if model_loader is None:
        return HealthResponse(
            status="initializing",
            models_loaded=False,
            families=[]
        )
    
    return HealthResponse(
        status="healthy",
        models_loaded=model_loader.loaded,
        families=list(model_loader.models.keys())
    )

@app.get("/families", response_model=FamiliesResponse)
async def get_families():
    """Retourne la liste des familles disponibles avec leur configuration."""
    return FamiliesResponse(families=FAMILIES)

@app.get("/leagues/{family}")
async def get_leagues(family: str):
    """Retourne la liste des ligues pour une famille donnée."""
    if model_loader is None or not model_loader.loaded:
        raise HTTPException(status_code=503, detail="Modèles non chargés")
    
    if family not in model_loader.models:
        raise HTTPException(status_code=404, detail=f"Famille {family} non trouvée")
    
    meta = model_loader.models[family]["meta"]
    return {"family": family, "leagues": meta.get("leagues", [])}

@app.post("/predict")
async def predict(request: PredictionRequest):
    """
    Prédit le résultat d'un match FIFA virtuel avec règles de cohérence globale.
    
    Cette endpoint utilise les modèles de machine learning entraînés et applique
    automatiquement 5 règles de cohérence pour éviter les contradictions entre
    les différentes prédictions (1x2, handicap, over/under, score exact, parity).
    
    Règles de cohérence appliquées:
      1. Cohérence Over/Under (Monotonie): Si over est favori pour un seuil, 
         il doit l'être pour tous les seuils inférieurs
      2. Cohérence Handicap (Monotonie): Si home est favori pour +1, 
         il doit être encore plus favori pour +2
      3. Cohérence Score Exact ↔ Total Goals: Le score exact doit correspondre 
         au total de buts prédit (écart max 2 buts)
      4. Cohérence Score Exact ↔ 1x2: Le score exact doit refléter le résultat 
         (home favori → home > away si probabilité > 60%)
      5. Cohérence Score Exact ↔ Parity: Le score exact doit respecter la 
         prédiction pair/impair (si probabilité > 60%)
    
    Retourne:
      - match: Nom du match formaté
      - league: Nom de la ligue
      - family: Famille détectée automatiquement (PENALTY, HIGHSCORE, RUSH, CLASSIC)
      - predictions.1x2: Probabilités pour Home/Draw/Away
      - predictions.total_goals.predicted: Total de buts prédit
      - predictions.total_goals.over_under: Probabilités over/under pour seuils dynamiques
      - predictions.handicap: Probabilités handicap pour seuils dynamiques
      - predictions.parity: Probabilités pair/impair
      - predictions.exact_score.prediction: Score exact le plus probable
    """
    if model_loader is None or not model_loader.loaded:
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
        
        # Calculer la prédiction avec règles de cohérence globales
        prediction = model_loader.predict(
            team_home=request.team_home,
            team_away=request.team_away,
            league=mapped_league
        )
        
        # Stocker dans le cache (5 minutes)
        if cache_instance:
            cache_instance.set(cache_key, prediction, ttl=300)
        
        return prediction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")

@app.post("/update-history")
async def update_history(request: UpdateHistoryRequest):
    """
    Met à jour l'historique des équipes avec un match terminé.
    
    Utile pour améliorer les prédictions futures avec les résultats réels.
    """
    if model_loader is None or not model_loader.loaded:
        raise HTTPException(status_code=503, detail="Modèles non chargés")
    
    try:
        model_loader.update_history({
            "team_home": request.team_home,
            "team_away": request.team_away,
            "league": request.league,
            "score_home": request.score_home,
            "score_away": request.score_away,
            "finished_at": request.finished_at,
            "family": request.family
        })
        
        return {"status": "success", "message": "Historique mis à jour"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de mise à jour: {str(e)}")

@app.post("/save-history")
async def save_history(family: Optional[str] = None):
    """
    Sauvegarde l'historique mis à jour sur disque.
    
    Args:
      family: si spécifié, sauvegarde seulement cette famille
    """
    if model_loader is None or not model_loader.loaded:
        raise HTTPException(status_code=503, detail="Modèles non chargés")
    
    try:
        model_loader.save_history(family)
        return {"status": "success", "message": "Historique sauvegardé"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de sauvegarde: {str(e)}")

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
