import requests
import time
import json

# Configuration
API_BASE_URL = "https://top-modele-train-api.onrender.com"

def test_production_cache():
    """Teste le cache Upstash en production"""
    print("="*70)
    print("TEST DU CACHE UPSTASH EN PRODUCTION")
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
    
    # Test 2: Première prédiction (cache miss attendu)
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
            print("⚠️  Les prédictions sont différentes (cache peut ne pas fonctionner)")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # Test 4: Nettoyage du cache
    print("\n📊 Test 4: Nettoyage du cache")
    try:
        response = requests.post(f"{API_BASE_URL}/clear-cache", timeout=10)
        result = response.json()
        print(f"Statut: {result['status']}")
        print(f"Message: {result['message']}")
        print("✅ Cache nettoyé")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # Test 5: Prédiction après nettoyage (cache miss attendu)
    print("\n📊 Test 5: Prédiction après nettoyage (cache miss attendu)")
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
        prediction3 = response.json()
        print(f"Match: {prediction3['match']}")
        print(f"Famille: {prediction3['family']}")
        print(f"Temps de réponse: {elapsed:.3f}s")
        print("✅ Prédiction après nettoyage réussie")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    print("\n" + "="*70)
    print("TEST TERMINÉ")
    print("="*70)
    print("\n📝 INSTRUCTIONS POUR VÉRIFIER LES LOGS RENDER:")
    print("1. Aller sur https://dashboard.render.com")
    print("2. Sélectionner votre service API")
    print("3. Cliquer sur 'Logs'")
    print("4. Chercher le message: '✅ Cache Upstash initialisé'")

if __name__ == "__main__":
    test_production_cache()
