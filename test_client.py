import requests
import time
from typing import Dict, Any

class FIFAPredictionClient:
    """Client pour l'API FIFA Prediction"""
    
    def __init__(self, base_url: str = "https://top-modele-train-api.onrender.com"):
        self.base_url = base_url
        self.timeout = 10  # secondes
        
    def health_check(self) -> bool:
        """Vérifie si l'API est opérationnelle"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return response.json().get("status") == "healthy"
        except Exception:
            return False
    
    def predict_match(
        self, 
        team_home: str, 
        team_away: str, 
        league: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Prédit le résultat d'un match avec retry automatique
        """
        payload = {
            "team_home": team_home,
            "team_away": team_away,
            "league": league
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/predict",
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Erreur après {max_retries} tentatives: {e}")
                time.sleep(2 ** attempt)
    
    def get_available_leagues(self, family: str) -> list:
        """Retourne la liste des ligues disponibles pour une famille"""
        response = requests.get(
            f"{self.base_url}/leagues/{family}",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json().get("leagues", [])

# Test du client
if __name__ == "__main__":
    print("="*70)
    print("TEST DU CLIENT FIFAPredictionClient")
    print("="*70)
    
    client = FIFAPredictionClient()
    
    # Test 1: Health check
    print("\n📊 Test 1: Health Check")
    health_status = client.health_check()
    print(f"Statut API: {'✅ Opérationnelle' if health_status else '❌ Non opérationnelle'}")
    
    if health_status:
        # Test 2: Prédiction d'un match
        print("\n📊 Test 2: Prédiction d'un match (CLASSIC)")
        try:
            prediction = client.predict_match(
                team_home="Real Madrid",
                team_away="Barcelona",
                league="FC 25. Champions League"
            )
            print(f"Match: {prediction['match']}")
            print(f"Famille: {prediction['family']}")
            print(f"1x2: Home={prediction['predictions']['1x2']['home']:.3f}, Draw={prediction['predictions']['1x2']['draw']:.3f}, Away={prediction['predictions']['1x2']['away']:.3f}")
            print(f"Total buts: {prediction['predictions']['total_goals']['predicted']}")
            print(f"Score exact: {prediction['predictions']['exact_score']['prediction']}")
            print("✅ Prédiction réussie")
        except Exception as e:
            print(f"❌ Erreur de prédiction: {e}")
        
        # Test 3: Liste des ligues
        print("\n📊 Test 3: Liste des ligues CLASSIC")
        try:
            leagues = client.get_available_leagues("CLASSIC")
            print(f"Nombre de ligues: {len(leagues)}")
            print(f"Ligues: {', '.join(leagues[:3])}...")
            print("✅ Récupération des ligues réussie")
        except Exception as e:
            print(f"❌ Erreur de récupération des ligues: {e}")
        
        # Test 4: Prédiction avec différentes familles
        print("\n📊 Test 4: Prédictions avec différentes familles")
        test_cases = [
            ("Manchester City", "Liverpool", "FC 24. 4x4. Championnat d'Angleterre", "HIGHSCORE"),
            ("Arsenal", "Napoli", "FC 26. 5x5 Rush. Superligue", "RUSH"),
            ("PSG", "Bayern Munich", "FC25. Penalty", "PENALTY")
        ]
        
        for team_home, team_away, league, expected_family in test_cases:
            try:
                prediction = client.predict_match(team_home, team_away, league)
                actual_family = prediction['family']
                status = "✅" if actual_family == expected_family else "❌"
                print(f"  {status} {league}: Famille détectée = {actual_family}")
            except Exception as e:
                print(f"  ❌ {league}: Erreur = {e}")
    
    print("\n" + "="*70)
    print("TEST TERMINÉ")
    print("="*70)
