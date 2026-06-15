# Guide Redis - Cache pour l'API FIFA Prediction

## 📋 Qu'est-ce que Redis?

**Redis** (Remote Dictionary Server) est un système de cache en mémoire open-source, utilisé comme base de données, cache et broker de messages.

### Caractéristiques principales:
- **Ultra-rapide**: Stockage en mémoire (RAM), temps de réponse < 1ms
- **Clé-valeur**: Structure simple mais puissante
- **Persistance**: Option de sauvegarde sur disque
- **Scalable**: Supporte le clustering et la réplication
- **Multi-usage**: Cache, sessions, pub/sub, etc.

### Pourquoi l'utiliser dans notre API?
- **Réduction de la charge CPU**: Évite de recalculer les mêmes prédictions
- **Temps de réponse**: < 10ms au lieu de < 100ms
- **Économie de ressources**: Moins de calculs de machine learning
- **Scalabilité**: Supporte plus de requêtes avec moins de ressources

---

## 🚀 Comment obtenir Redis?

### Option 1: Installation Locale (Développement)

#### Windows
```bash
# Via Chocolatey
choco install redis-64

# Via Docker (recommandé)
docker run -d -p 6379:6379 redis:latest
```

#### macOS
```bash
# Via Homebrew
brew install redis
brew services start redis
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### Option 2: Docker (Recommandé pour développement)
```bash
# Démarrer Redis en container
docker run -d -p 6379:6379 --name redis redis:latest

# Vérifier que Redis fonctionne
docker exec -it redis redis-cli ping
# Réponse: PONG
```

### Option 3: Cloud (Production)

#### Redis Cloud (Officiel)
- **URL**: https://redis.com/try-free/
- **Gratuit**: 30MB de stockage
- **Avantages**: Géré, scalable, monitoring inclus

#### AWS ElastiCache
- **Service**: AWS ElastiCache for Redis
- **Coût**: ~$15-50/mois selon la taille
- **Avantages**: Intégration AWS, haute disponibilité

#### Azure Cache for Redis
- **Service**: Azure Cache for Redis
- **Coût**: ~$15-50/mois selon la taille
- **Avantages**: Intégration Azure, haute disponibilité

#### Render (Déploiement actuel)
- **Service**: Render Redis
- **Coût**: ~$7/mois pour le plan de base
- **Avantages**: Intégration facile avec l'API existante

---

## 🔧 Installation pour notre API

### Étape 1: Installer les dépendances Python
```bash
pip install redis
```

### Étape 2: Ajouter au requirements.txt
```txt
redis==5.0.1
```

### Étape 3: Configuration des variables d'environnement
```bash
# Local
REDIS_URL=redis://localhost:6379/0

# Production (Redis Cloud)
REDIS_URL=redis://default:password@host:port

# Render
REDIS_URL=redis://default:password@redis-render-url:6379
```

---

## 💻 Implémentation dans l'API

### Code de base pour le cache Redis

```python
import redis
import json
import hashlib
from typing import Optional, Any
from functools import wraps

class RedisCache:
    """Gestionnaire de cache Redis pour l'API"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 300  # 5 minutes par défaut
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Génère une clé de cache unique"""
        # Créer une chaîne à partir des paramètres
        params_str = json.dumps(kwargs, sort_keys=True)
        # Hasher pour avoir une clé courte
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{params_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Stocke une valeur dans le cache"""
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            return self.redis_client.setex(key, ttl, serialized)
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Supprime une valeur du cache"""
        try:
            return self.redis_client.delete(key) > 0
        except Exception:
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Supprime toutes les clés correspondant à un pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception:
            return 0

def cache_result(prefix: str, ttl: int = 300):
    """Décorateur pour mettre en cache les résultats de fonctions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer la clé de cache
            cache_key = f"{prefix}:{hashlib.md5(json.dumps(kwargs, sort_keys=True).encode()).hexdigest()}"
            
            # Essayer de récupérer du cache
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Calculer le résultat
            result = func(*args, **kwargs)
            
            # Stocker dans le cache
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Instance globale du cache
cache = None

def get_cache():
    """Retourne l'instance du cache (singleton)"""
    global cache
    if cache is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        cache = RedisCache(redis_url)
    return cache
```

### Intégration dans api.py

```python
from redis_cache import get_cache

# Initialiser le cache au démarrage
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'API"""
    global cache
    cache = get_cache()
    print("✅ Cache Redis initialisé")

@app.post("/predict")
async def predict_match(request: PredictionRequest):
    """Prédit le résultat d'un match avec cache"""
    # Générer la clé de cache
    cache_key = f"predict:{request.team_home}:{request.team_away}:{request.league}"
    
    # Essayer de récupérer du cache
    cached_result = cache.get(cache_key)
    if cached_result:
        print(f"📦 Résultat récupéré du cache pour {request.team_home} vs {request.team_away}")
        return cached_result
    
    # Calculer la prédiction
    result = compute_prediction(request)
    
    # Stocker dans le cache (5 minutes)
    cache.set(cache_key, result, ttl=300)
    
    return result
```

---

## 🧪 Test du cache Redis

### Script de test
```python
import redis
import json
import time

# Connexion à Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Test basique
print("🧪 Test Redis")
print(f"Ping: {r.ping()}")

# Écrire une valeur
r.set("test_key", "test_value")
print(f"Set test_key: test_value")

# Lire la valeur
value = r.get("test_key")
print(f"Get test_key: {value}")

# Écrire avec TTL (5 secondes)
r.setex("test_ttl", 5, "test_value_with_ttl")
print(f"Set test_ttl with 5s TTL")

# Lire immédiatement
print(f"Get test_ttl (immédiat): {r.get('test_ttl')}")

# Attendre 6 secondes
time.sleep(6)
print(f"Get test_ttl (après 6s): {r.get('test_ttl')}")

# Nettoyer
r.delete("test_key", "test_ttl")
print("✅ Test terminé")
```

---

## 📊 Monitoring du cache Redis

### Commandes utiles
```bash
# Statistiques Redis
redis-cli INFO

# Nombre de clés
redis-cli DBSIZE

# Mémoire utilisée
redis-cli INFO memory

# Clés avec un pattern
redis-cli KEYS "predict:*"

# Supprimer toutes les clés
redis-cli FLUSHDB
```

### Métriques à monitorer
- **Nombre de clés**: Taille du cache
- **Hit ratio**: Pourcentage de cache hits vs misses
- **Mémoire utilisée**: RAM consommée
- **TTL moyen**: Durée de vie moyenne des clés

---

## 🚀 Déploiement sur Render

### 1. Ajouter Redis dans Render
- Aller sur dashboard.render.com
- Créer un nouveau "Redis"
- Note: Coût ~$7/mois

### 2. Connecter l'API à Redis
```bash
# Ajouter la variable d'environnement
# Dans Render Dashboard → Environment Variables
REDIS_URL=redis://default:password@redis-render-url:6379
```

### 3. Redéployer l'API
- Render va automatiquement utiliser la nouvelle variable d'environnement
- L'API se connectera automatiquement à Redis

---

## 💡 Bonnes pratiques

### 1. TTL approprié
- **Prédictions**: 5-15 minutes (données volatiles)
- **Ligues**: 1 heure (données stables)
- **Statistiques**: 24 heures (données très stables)

### 2. Clés descriptives
- ✅ `predict:real_madrid:barcelona:champions_league`
- ❌ `abc123def456`

### 3. Gestion des erreurs
- Toujours utiliser try/except
- Fallback sur le calcul si Redis échoue
- Logging des erreurs de cache

### 4. Nettoyage régulier
- Utiliser des TTL pour éviter l'accumulation
- Nettoyage manuel si nécessaire
- Monitoring de la taille du cache

---

## 🎯 Exemple complet d'implémentation

```python
# api.py avec cache Redis
import os
from fastapi import FastAPI
from redis_cache import get_cache

app = FastAPI()

@app.on_event("startup")
async def startup():
    """Initialisation au démarrage"""
    global cache
    cache = get_cache()
    print("✅ Cache Redis initialisé")

@app.post("/predict")
async def predict_match(request: PredictionRequest):
    """Prédiction avec cache"""
    # Clé de cache
    cache_key = f"predict:{request.team_home}:{request.team_away}:{request.league}"
    
    # Essayer le cache
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Calculer
    result = compute_prediction(request)
    
    # Mettre en cache (5 min)
    cache.set(cache_key, result, ttl=300)
    
    return result

@app.post("/clear-cache")
async def clear_cache():
    """Nettoyer le cache (admin)"""
    cache.clear_pattern("predict:*")
    return {"status": "success", "message": "Cache nettoyé"}
```

---

## 📈 Résultats attendus

### Avant Redis
- Temps de réponse: ~100ms
- Charge CPU: Élevée
- Scalabilité: Limitée

### Après Redis
- Temps de réponse: ~10ms (cache hit)
- Charge CPU: Réduite de 70%
- Scalabilité: 10x plus de requêtes possibles

---

## 🔗 Ressources

- **Documentation officielle**: https://redis.io/docs/
- **Python Redis**: https://redis-py.readthedocs.io/
- **Redis Cloud**: https://redis.com/try-free/
- **Render Redis**: https://render.com/docs/redis

---

**Document généré par SOLITAIRE HACK**  
*Date: 15 Juin 2026 à 2h03 UTC*  
*Version: 1.0*  
*Tous droits réservés*
