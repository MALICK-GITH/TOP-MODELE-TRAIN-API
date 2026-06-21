"""
Test de prédiction sur chaque ligue disponible
"""
import requests
import json

BASE_URL = "https://top-modele-train-api-vmp.onrender.com"

def test_all_leagues():
    """Teste les prédictions sur chaque ligue disponible"""
    
    print("=" * 80)
    print("TEST DE PRÉDICTION SUR CHAQUE LIGUE")
    print("=" * 80)
    
    # Récupérer les familles
    try:
        response = requests.get(f"{BASE_URL}/families")
        families = response.json()["families"]
        print(f"\n✅ {len(families)} familles disponibles")
    except Exception as e:
        print(f"❌ Erreur récupération familles: {e}")
        return
    
    # Pour chaque famille, récupérer les ligues et tester
    all_predictions = {}
    
    for family_name, family_config in families.items():
        print(f"\n{'='*80}")
        print(f"FAMILLE: {family_name}")
        print(f"Description: {family_config['description']}")
        print(f"{'='*80}")
        
        try:
            # Récupérer les ligues de cette famille
            response = requests.get(f"{BASE_URL}/leagues/{family_name}")
            leagues = response.json()["leagues"]
            print(f"\n{len(leagues)} ligues trouvées")
            
            family_predictions = {}
            
            # Tester chaque ligue
            for i, league in enumerate(leagues[:3], 1):  # Limiter à 3 ligues par famille pour le test
                print(f"\n[{i}/{min(3, len(leagues))}] Ligue: {league}")
                
                # Créer des équipes fictives pour le test
                team_home = f"Team_Home_{i}"
                team_away = f"Team_Away_{i}"
                
                try:
                    # Faire la prédiction
                    response = requests.post(f"{BASE_URL}/predict", json={
                        "team_home": team_home,
                        "team_away": team_away,
                        "league": league
                    })
                    
                    if response.status_code == 200:
                        prediction = response.json()
                        
                        # Extraire les informations clés
                        exact_score = prediction["predictions"]["exact_score"]["prediction"]
                        home_prob = prediction["predictions"]["1x2"]["home"]
                        draw_prob = prediction["predictions"]["1x2"]["draw"]
                        away_prob = prediction["predictions"]["1x2"]["away"]
                        total_goals = prediction["predictions"]["total_goals"]["predicted"]
                        
                        print(f"   ✅ Score exact: {exact_score}")
                        print(f"   1X2: H={home_prob:.3f}, D={draw_prob:.3f}, A={away_prob:.3f}")
                        print(f"   Total buts: {total_goals}")
                        
                        family_predictions[league] = {
                            "exact_score": exact_score,
                            "1x2": {"home": home_prob, "draw": draw_prob, "away": away_prob},
                            "total_goals": total_goals
                        }
                    else:
                        print(f"   ❌ Erreur prédiction: {response.status_code}")
                        family_predictions[league] = {"error": f"HTTP {response.status_code}"}
                
                except Exception as e:
                    print(f"   ❌ Erreur: {e}")
                    family_predictions[league] = {"error": str(e)}
            
            all_predictions[family_name] = family_predictions
            
        except Exception as e:
            print(f"❌ Erreur pour famille {family_name}: {e}")
            all_predictions[family_name] = {"error": str(e)}
    
    # Sauvegarder les résultats
    print(f"\n{'='*80}")
    print("RÉSUMÉ")
    print(f"{'='*80}")
    
    with open("all_leagues_predictions.json", "w") as f:
        json.dump(all_predictions, f, indent=2)
    
    print(f"\n✅ Résultats sauvegardés dans all_leagues_predictions.json")
    print(f"Total familles testées: {len(all_predictions)}")
    
    # Compter les prédictions réussies
    total_leagues = 0
    successful_predictions = 0
    
    for family_name, leagues in all_predictions.items():
        if isinstance(leagues, dict) and "error" not in leagues:
            total_leagues += len(leagues)
            successful_predictions += len([l for l in leagues.values() if "error" not in l])
    
    print(f"Total ligues testées: {total_leagues}")
    print(f"Prédictions réussies: {successful_predictions}")
    print(f"Taux de succès: {successful_predictions/total_leagues*100:.1f}%" if total_leagues > 0 else "N/A")
    
    return all_predictions

if __name__ == "__main__":
    test_all_leagues()
