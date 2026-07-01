"""
Test de l'API avec des données de marché réelles
Teste l'adaptation dynamique du score_range avec des données réelles de la plateforme
"""

import requests
import json

API_URL = "http://localhost:8001"

# Données de marché réelles extraites du JSON (match RUSH)
real_market_data = {
    "O1": "Barcelone",
    "O2": "Liverpool",
    "L": "FC 26. 5x5 Rush. Superligue",
    "E": [
        {"T": 9, "P": 7.5, "C": 2.0, "G": 17},
        {"T": 10, "P": 7.5, "C": 1.81, "G": 17}
    ],
    "AE": [
        {
            "G": 17,
            "ME": [
                {"T": 9, "P": 4.5, "C": 2.1, "G": 17},
                {"T": 10, "P": 4.5, "C": 1.9, "G": 17},
                {"T": 9, "P": 15.5, "C": 3.5, "G": 17},
                {"T": 10, "P": 15.5, "C": 1.4, "G": 17}
            ]
        }
    ]
}

def test_real_market_data():
    """Test l'API avec des données de marché réelles"""
    
    print("🧪 Test de l'API avec données de marché réelles")
    print("=" * 60)
    
    # Test 1: RUSH
    print("\n📊 Test 1: Match RUSH (FC 26. 5x5 Rush. Superligue)")
    request_rush = {
        "team_home": "Barcelone",
        "team_away": "Liverpool",
        "league": "FC 26. 5x5 Rush. Superligue",
        "market_data": real_market_data
    }
    
    print(f"   Équipe domicile: {request_rush['team_home']}")
    print(f"   Équipe extérieur: {request_rush['team_away']}")
    print(f"   Ligue: {request_rush['league']}")
    print(f"   Options Total Goals disponibles: {[opt['P'] for opt in real_market_data['AE'][0]['ME'] if opt['T'] in [9, 10]]}")
    
    try:
        response = requests.post(f"{API_URL}/predict", json=request_rush)
        if response.status_code == 200:
            data = response.json()
            score_range = data["predictions"]["score_range"]
            print(f"\n✅ Score Range obtenu:")
            print(f"   {score_range}")
            
            # Vérifier l'adaptation dynamique
            range_keys = list(score_range.keys())[:-1]  # Exclure 'confidence'
            print(f"\n📋 Plages de score dynamiques: {range_keys}")
            
            # Attendu pour RUSH avec options 4.5-15.5: 0-4, 5-7, 8-15, 16+
            expected_ranges = ["0-4", "5-7", "8-15", "16+"]
            if range_keys == expected_ranges:
                print("✅ Adaptation dynamique CORRECTE - Les plages correspondent aux options du marché")
            else:
                print(f"⚠️ Plages attendues: {expected_ranges}")
                print(f"⚠️ Plages obtenues: {range_keys}")
                
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 2: CLASSIC (sans market_data pour tester fallback)
    print("\n📊 Test 2: Match CLASSIC sans market_data (fallback)")
    request_classic = {
        "team_home": "Real Madrid",
        "team_away": "Barcelona",
        "league": "FC 25. Champions League"
    }
    
    print(f"   Équipe domicile: {request_classic['team_home']}")
    print(f"   Équipe extérieur: {request_classic['team_away']}")
    print(f"   Ligue: {request_classic['league']}")
    print(f"   market_data: Non fourni (test fallback)")
    
    try:
        response = requests.post(f"{API_URL}/predict", json=request_classic)
        if response.status_code == 200:
            data = response.json()
            score_range = data["predictions"]["score_range"]
            print(f"\n✅ Score Range obtenu:")
            print(f"   {score_range}")
            
            # Vérifier le fallback
            range_keys = list(score_range.keys())[:-1]  # Exclure 'confidence'
            print(f"\n📋 Plages de score (fallback): {range_keys}")
            
            # Attendu pour fallback: 0-2, 3-5, 6-8, 9+
            expected_fallback = ["0-2", "3-5", "6-8", "9+"]
            if range_keys == expected_fallback:
                print("✅ Fallback CORRECT - Les plages par défaut sont utilisées")
            else:
                print(f"⚠️ Plages attendues: {expected_fallback}")
                print(f"⚠️ Plages obtenues: {range_keys}")
                
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_real_market_data()
