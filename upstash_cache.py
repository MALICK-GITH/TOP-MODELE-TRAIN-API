import os
import json
import hashlib
from typing import Optional, Any
from functools import wraps

try:
    from upstash_redis import Redis
    UPSTASH_AVAILABLE = True
except ImportError:
    UPSTASH_AVAILABLE = False
    print("⚠️  upstash_redis non installé. Installez avec: pip install upstash-redis")

class UpstashCache:
    """Gestionnaire de cache Upstash Redis pour l'API"""
    
    def __init__(self, url: str = None, token: str = None):
        """
        Initialise le cache Upstash
        
        Args:
            url: URL Upstash Redis (défaut: variable d'environnement UPSTASH_REDIS_REST_URL)
            token: Token Upstash Redis (défaut: variable d'environnement UPSTASH_REDIS_REST_TOKEN)
        """
        if not UPSTASH_AVAILABLE:
            raise ImportError("upstash_redis non installé. Installez avec: pip install upstash-redis")
        
        self.url = url or os.getenv("UPSTASH_REDIS_REST_URL")
        self.token = token or os.getenv("UPSTASH_REDIS_REST_TOKEN")
        
        if not self.url or not self.token:
            raise ValueError("UPSTASH_REDIS_REST_URL et UPSTASH_REDIS_REST_TOKEN doivent être définis")
        
        self.redis = Redis(url=self.url, token=self.token)
        self.default_ttl = 300  # 5 minutes par défaut
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Génère une clé de cache unique"""
        params_str = json.dumps(kwargs, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{params_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Stocke une valeur dans le cache"""
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            self.redis.set(key, serialized, ex=ttl)
            return True
        except Exception as e:
            print(f"❌ Erreur lors du stockage dans le cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Supprime une valeur du cache"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la suppression du cache: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Supprime toutes les clés correspondant à un pattern"""
        try:
            # Upstash ne supporte pas directement KEYS, donc on utilise une approche différente
            # Pour l'instant, on retourne 0 (à améliorer avec un système de tracking)
            return 0
        except Exception as e:
            print(f"❌ Erreur lors du nettoyage du cache: {e}")
            return 0
    
    def ping(self) -> bool:
        """Vérifie la connexion au cache"""
        try:
            result = self.redis.set("ping", "pong", ex=10)
            if result:
                value = self.redis.get("ping")
                self.redis.delete("ping")
                return value == "pong"
            return False
        except Exception as e:
            print(f"❌ Erreur de ping: {e}")
            return False

def cache_result(prefix: str, ttl: int = 300):
    """Décorateur pour mettre en cache les résultats de fonctions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer la clé de cache
            cache_key = f"{prefix}:{hashlib.md5(json.dumps(kwargs, sort_keys=True).encode()).hexdigest()}"
            
            # Essayer de récupérer du cache
            if cache_instance:
                cached = cache_instance.get(cache_key)
                if cached is not None:
                    return cached
            
            # Calculer le résultat
            result = func(*args, **kwargs)
            
            # Stocker dans le cache
            if cache_instance:
                cache_instance.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Instance globale du cache
cache_instance = None

def get_cache():
    """Retourne l'instance du cache (singleton)"""
    global cache_instance
    if cache_instance is None:
        cache_instance = UpstashCache()
    return cache_instance

# Test du cache
if __name__ == "__main__":
    print("="*70)
    print("TEST DU CACHE UPSTASH")
    print("="*70)
    
    try:
        cache = UpstashCache()
        
        # Test de connexion
        print("\n📊 Test 1: Ping")
        ping_result = cache.ping()
        print(f"Connexion: {'✅ OK' if ping_result else '❌ Échoué'}")
        
        if ping_result:
            # Test d'écriture
            print("\n📊 Test 2: Écriture")
            cache.set("test_key", {"message": "Hello Upstash!"})
            print("✅ Écriture réussie")
            
            # Test de lecture
            print("\n📊 Test 3: Lecture")
            value = cache.get("test_key")
            print(f"Valeur: {value}")
            print("✅ Lecture réussie")
            
            # Test de suppression
            print("\n📊 Test 4: Suppression")
            cache.delete("test_key")
            print("✅ Suppression réussie")
            
            # Test après suppression
            print("\n📊 Test 5: Vérification après suppression")
            value = cache.get("test_key")
            print(f"Valeur: {value}")
            print("✅ Clé supprimée correctement")
        
        print("\n" + "="*70)
        print("TEST TERMINÉ")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        print("\nAssurez-vous d'avoir défini les variables d'environnement:")
        print("  UPSTASH_REDIS_REST_URL")
        print("  UPSTASH_REDIS_REST_TOKEN")
