"""
Test de l'API avec adaptation dynamique du score_range
Teste l'endpoint /predict avec market_data pour vérifier l'adaptation
"""

import requests
import json

API_URL = "http://localhost:8001"

def test_predict_with_market_data():
    """Test l'endpoint /predict avec market_data"""
    
    print("🧪 Test de l'API avec adaptation dynamique du score_range")
    print("=" * 60)
    
    # Test 1: RUSH avec market_data
    print("\n📊 Test 1: RUSH avec market_data")
    request_rush = {
        "team_home": "Liverpool",
        "team_away": "Borussia Dortmund",
        "league": "FC 26. 5x5 Rush. Superligue",
        "market_data": {
            "O1": "Liverpool",
            "O2": "Borussia Dortmund",
            "L": "FC 26. 5x5 Rush. Superligue",
            "E": [
                {"T": 9, "P": 7.5, "C": 2.0, "G": 17},
                {"T": 10, "P": 7.5, "C": 1.81, "G": 17},
            ],
            "AE": [
                {
                    "G": 17,
                    "ME": [
                        {"T": 9, "P": 4.5, "C": 2.1, "G": 17},
                        {"T": 10, "P": 4.5, "C": 1.9, "G": 17},
                        {"T": 9, "P": 15.5, "C": 3.5, "G": 17},
                        {"T": 10, "P": 15.5, "C": 1.4, "G": 17},
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(f"{API_URL}/predict", json=request_rush)
        if response.status_code == 200:
            data = response.json()
            score_range = data["predictions"]["score_range"]
            print(f"✅ Score Range RUSH: {score_range}")
            print(f"   Plages dynamiques: {list(score_range.keys())[:-1]}")
        else:
            print(f"❌ Erreur API: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 2: CLASSIC avec market_data
    print("\n📊 Test 2: CLASSIC avec market_data")
    request_classic = {
        "team_home": "Real Madrid",
        "team_away": "Barcelona",
        "league": "FC 25. Champions League",
        "market_data": {
            "O1": "Real Madrid",
            "O2": "Barcelona",
            "L": "FC 25. Champions League",
            "E": [
                {"T": 9, "P": 2.5, "C": 2.0, "G": 17},
                {"T": 10, "P": 2.5, "C": 1.81, "G": 17},
            ],
            "AE": [
                {
                    "G": 17,
                    "ME": [
                        {"T": 9, "P": 0.5, "C": 3.5, "G": 17},
                        {"T": 10, "P": 0.5, "C": 1.3, "G": 17},
                        {"T": 9, "P": 8.5, "C": 4.0, "G": 17},
                        {"T": 10, "P": 8.5, "C": 1.2, "G": 17},
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(f"{API_URL}/predict", json=request_classic)
        if response.status_code == 200:
            data = response.json()
            score_range = data["predictions"]["score_range"]
            print(f"✅ Score Range CLASSIC: {score_range}")
            print(f"   Plages dynamiques: {list(score_range.keys())[:-1]}")
        else:
            print(f"❌ Erreur API: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 3: Sans market_data (fallback)
    print("\n📊 Test 3: Sans market_data (fallback)")
    request_no_market = {
        "team_home": "Chelsea",
        "team_away": "Arsenal",
        "league": "FC 25. Champions League"
    }
    
    try:
        response = requests.post(f"{API_URL}/predict", json=request_no_market)
        if response.status_code == 200:
            data = response.json()
            score_range = data["predictions"]["score_range"]
            print(f"✅ Score Range Fallback: {score_range}")
            print(f"   Plages par défaut: {list(score_range.keys())[:-1]}")
        else:
            print(f"❌ Erreur API: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    print("\n✅ Tests API terminés")

if __name__ == "__main__":
    test_predict_with_market_data()
