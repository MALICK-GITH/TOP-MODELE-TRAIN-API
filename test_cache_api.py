import requests
import time
import json

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_cache():
    """Teste le cache de l'API"""
    print("="*70)
    print("TEST DU CACHE UPSTASH DANS L'API")
    print("="*70)
    
    # Test 1: Health check
    print("\n📊 Test 1: Health Check")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        health = response.json()
        print(f"Statut: {health['status']}")
        print(f"Modèles chargés: {health['models_loaded']}")
        print(f"Familles: {health['families']}")
        print("✅ Health check réussi")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # Test 2: Première prédiction (cache miss)
    print("\n📊 Test 2: Première prédiction (cache miss attendu)")
    start_time = time.time()
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={
                "team_home": "Real Madrid",
                "team_away": "Barcelona",
                "league": "FC 25. Champions League"
            },
            timeout=10
        )
        elapsed = time.time() - start_time
        prediction1 = response.json()
        print(f"Match: {prediction1['match']}")
        print(f"Famille: {prediction1['family']}")
        print(f"Temps de réponse: {elapsed:.3f}s")
        print("✅ Première prédiction réussie")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # Test 3: Deuxième prédiction identique (cache hit attendu)
    print("\n📊 Test 3: Deuxième prédiction identique (cache hit attendu)")
    start_time = time.time()
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={
                "team_home": "Real Madrid",
                "team_away": "Barcelona",
                "league": "FC 25. Champions League"
            },
            timeout=10
        )
        elapsed = time.time() - start_time
        prediction2 = response.json()
        print(f"Match: {prediction2['match']}")
        print(f"Famille: {prediction2['family']}")
        print(f"Temps de réponse: {elapsed:.3f}s")
        print("✅ Deuxième prédiction réussie")
        
        # Vérifier que les prédictions sont identiques
        if prediction1 == prediction2:
            print("✅ Les prédictions sont identiques (cache fonctionne)")
        else:
            print("❌ Les prédictions sont différentes (problème de cache)")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # Test 4: Prédiction différente (cache miss attendu)
    print("\n📊 Test 4: Prédiction différente (cache miss attendu)")
    start_time = time.time()
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={
                "team_home": "Manchester City",
                "team_away": "Liverpool",
                "league": "FC 24. 4x4. Championnat d'Angleterre"
            },
            timeout=10
        )
        elapsed = time.time() - start_time
        prediction3 = response.json()
        print(f"Match: {prediction3['match']}")
        print(f"Famille: {prediction3['family']}")
        print(f"Temps de réponse: {elapsed:.3f}s")
        print("✅ Prédiction différente réussie")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # Test 5: Nettoyage du cache
    print("\n📊 Test 5: Nettoyage du cache")
    try:
        response = requests.post(f"{API_BASE_URL}/clear-cache", timeout=10)
        result = response.json()
        print(f"Statut: {result['status']}")
        print(f"Message: {result['message']}")
        print("✅ Cache nettoyé")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # Test 6: Prédiction après nettoyage (cache miss attendu)
    print("\n📊 Test 6: Prédiction après nettoyage (cache miss attendu)")
    start_time = time.time()
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={
                "team_home": "Real Madrid",
                "team_away": "Barcelona",
                "league": "FC 25. Champions League"
            },
            timeout=10
        )
        elapsed = time.time() - start_time
        prediction4 = response.json()
        print(f"Match: {prediction4['match']}")
        print(f"Famille: {prediction4['family']}")
        print(f"Temps de réponse: {elapsed:.3f}s")
        print("✅ Prédiction après nettoyage réussie")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    print("\n" + "="*70)
    print("TEST TERMINÉ")
    print("="*70)

if __name__ == "__main__":
    test_cache()
