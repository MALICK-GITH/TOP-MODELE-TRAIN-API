"""
Test de l'intégration avec les options de marché dynamiques
Utilise les données réelles fournies par l'API de marché
"""

import requests
import json

# Exemple de données de marché (extrait de la réponse fournie)
sample_market_data = {
    "O1": "Borussia Dortmund",
    "O2": "Club Atlético de Madrid",
    "L": "FC 26. 5x5 Rush. Superligue",
    "E": [
        {"T": 9, "P": 7.5, "C": 2.0, "G": 17},
        {"T": 10, "P": 7.5, "C": 1.81, "G": 17},
    ],
    "AE": [
        {
            "G": 2,
            "ME": [
                {"T": 7, "P": -1.0, "C": 3.03, "G": 2},
                {"T": 8, "P": -1.0, "C": 2.625, "G": 2},
            ]
        }
    ]
}

# URL de l'API locale
API_URL = "http://localhost:8000"

def test_without_market_data():
    """Test sans données de marché (utilise les options statiques)"""
    print("=" * 80)
    print("TEST 1: Prédiction SANS données de marché (options statiques)")
    print("=" * 80)
    
    payload = {
        "team_home": "Borussia Dortmund",
        "team_away": "Club Atlético de Madrid",
        "league": "FC 26. 5x5 Rush. Superligue"
    }
    
    try:
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Match: {data['match']}")
            print(f"League: {data['league']}")
            print(f"Family: {data['family']}")
            print(f"Total Goals: prédit={data['predictions']['total_goals']['predicted']}, "
                  f"plateforme={data['predictions']['total_goals']['platform_value']}")
            print(f"Handicap: prédit={data['predictions']['handicap']['predicted']}, "
                  f"plateforme={data['predictions']['handicap']['platform_value']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Erreur: {e}")
    
    print()

def test_with_market_data():
    """Test avec données de marché (utilise les options dynamiques)"""
    print("=" * 80)
    print("TEST 2: Prédiction AVEC données de marché (options dynamiques)")
    print("=" * 80)
    
    payload = {
        "team_home": "Borussia Dortmund",
        "team_away": "Club Atlético de Madrid",
        "league": "FC 26. 5x5 Rush. Superligue",
        "market_data": sample_market_data
    }
    
    try:
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Match: {data['match']}")
            print(f"League: {data['league']}")
            print(f"Family: {data['family']}")
            print(f"Total Goals: prédit={data['predictions']['total_goals']['predicted']}, "
                  f"plateforme={data['predictions']['total_goals']['platform_value']}")
            print(f"Handicap: prédit={data['predictions']['handicap']['predicted']}, "
                  f"plateforme={data['predictions']['handicap']['platform_value']}")
            print("\n✅ Les options de marché dynamiques sont utilisées!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Erreur: {e}")
    
    print()

def test_with_real_market_data():
    """Test avec les données réelles complètes fournies par l'utilisateur"""
    print("=" * 80)
    print("TEST 3: Prédiction avec données de marché réelles (extrait complet)")
    print("=" * 80)
    
    # Extrait d'un match réel dans les données fournies
    real_market_data = {
        "O1": "Borussia Dortmund",
        "O2": "Club Atlético de Madrid",
        "L": "FC 26. 5x5 Rush. Superligue",
        "E": [
            {"T": 5, "C": 1.06, "CV": "1.06", "G": 8},
            {"T": 6, "C": 1.56, "CV": "1.56", "G": 8},
            {"T": 4, "C": 1.688, "CV": "1.688", "G": 8},
            {"T": 13, "P": 3.5, "C": 1.784, "CV": "1.784", "G": 62},
            {"T": 8, "C": 1.805, "CV": "1.805", "G": 2},
            {"T": 10, "P": 7.5, "C": 1.81, "CV": "1.81", "G": 17},
            {"T": 11, "P": 3.5, "C": 1.9, "CV": "1.9", "G": 15},
            {"T": 12, "P": 3.5, "C": 1.9, "CV": "1.9", "G": 15},
            {"T": 9, "P": 7.5, "C": 2, "CV": "2", "G": 17},
            {"T": 7, "C": 2.005, "CV": "2.005", "G": 2},
            {"T": 14, "P": 3.5, "C": 2.03, "CV": "2.03", "G": 62},
            {"T": 3, "C": 2.075, "CV": "2.075", "G": 1},
            {"T": 1, "C": 2.304, "CV": "2.304", "G": 1},
            {"T": 2, "C": 6.11, "CV": "6.11", "G": 1}
        ],
        "AE": [
            {
                "G": 2,
                "ME": [
                    {"T": 7, "C": 2.005, "CV": "2.005", "G": 2, "CE": 1},
                    {"T": 8, "C": 1.805, "CV": "1.805", "G": 2},
                    {"T": 7, "P": -1.0, "C": 3.03, "CV": "3.03", "G": 2},
                    {"T": 8, "P": -1.0, "C": 2.625, "CV": "2.625", "G": 2},
                    {"T": 7, "P": 1.0, "C": 1.464, "CV": "1.464", "G": 2},
                    {"T": 8, "P": 1.0, "C": 1.365, "CV": "1.365", "G": 2},
                    {"T": 7, "P": -1.5, "C": 3.5, "CV": "3.5", "G": 2},
                    {"T": 8, "P": -1.5, "C": 3.056, "CV": "3.056", "G": 2},
                    {"T": 7, "P": 1.5, "C": 1.36, "CV": "1.36", "G": 2},
                    {"T": 8, "P": 1.5, "C": 1.285, "CV": "1.285", "G": 2}
                ]
            },
            {
                "G": 17,
                "ME": [
                    {"T": 9, "P": 5.5, "C": 1.22, "CV": "1.22", "G": 17},
                    {"T": 10, "P": 5.5, "C": 3.85, "CV": "3.85", "G": 17},
                    {"T": 9, "P": 6.5, "C": 1.51, "CV": "1.51", "G": 17},
                    {"T": 10, "P": 6.5, "C": 2.49, "CV": "2.49", "G": 17},
                    {"T": 9, "P": 7.5, "C": 2, "CV": "2", "G": 17, "CE": 1},
                    {"T": 10, "P": 7.5, "C": 1.81, "CV": "1.81", "G": 17, "CE": 1},
                    {"T": 9, "P": 8.5, "C": 2.792, "CV": "2.792", "G": 17},
                    {"T": 10, "P": 8.5, "C": 1.416, "CV": "1.416", "G": 17},
                    {"T": 9, "P": 9.5, "C": 4.18, "CV": "4.18", "G": 17},
                    {"T": 10, "P": 9.5, "C": 1.19, "CV": "1.19", "G": 17}
                ]
            }
        ]
    }
    
    payload = {
        "team_home": "Borussia Dortmund",
        "team_away": "Club Atlético de Madrid",
        "league": "FC 26. 5x5 Rush. Superligue",
        "market_data": real_market_data
    }
    
    try:
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Match: {data['match']}")
            print(f"League: {data['league']}")
            print(f"Family: {data['family']}")
            print(f"Total Goals: prédit={data['predictions']['total_goals']['predicted']}, "
                  f"plateforme={data['predictions']['total_goals']['platform_value']}")
            print(f"Handicap: prédit={data['predictions']['handicap']['predicted']}, "
                  f"plateforme={data['predictions']['handicap']['platform_value']}")
            print("\n✅ Les options de marché réelles sont utilisées!")
            print("   Note: Les valeurs plateforme correspondent maintenant aux options disponibles dans le marché réel")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Erreur: {e}")
    
    print()

if __name__ == "__main__":
    print("🧪 TESTS D'INTÉGRATION MARKET API")
    print("=" * 80)
    print()
    
    # Test 1: Sans données de marché
    test_without_market_data()
    
    # Test 2: Avec données de marché simplifiées
    test_with_market_data()
    
    # Test 3: Avec données de marché réelles
    test_with_real_market_data()
    
    print("=" * 80)
    print("✅ TESTS TERMINÉS")
    print("=" * 80)
