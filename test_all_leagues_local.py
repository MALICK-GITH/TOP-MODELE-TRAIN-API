"""
Test de prédiction sur chaque ligue disponible (local)
"""
import sys
sys.path.insert(0, r"c:\Users\HP\Downloads\TRAIN CSV MODELE FIFA")

from train_random_forest import ModelLoader, FAMILIES

def test_all_leagues_local():
    """Teste les prédictions sur chaque ligue disponible en local"""
    
    print("=" * 80)
    print("TEST DE PRÉDICTION SUR CHAQUE LIGUE (LOCAL)")
    print("=" * 80)
    
    # Charger les modèles
    csv_path = r"c:\Users\HP\Downloads\TRAIN CSV MODELE FIFA\finished_matches.csv"
    model_loader = ModelLoader("./models", csv_path=csv_path)
    model_loader.load_all()
    
    print(f"\n✅ {len(model_loader.models)} familles chargées")
    
    # Pour chaque famille, récupérer les ligues et tester
    all_predictions = {}
    
    for family_name in model_loader.models.keys():
        family_config = FAMILIES[family_name]
        
        print(f"\n{'='*80}")
        print(f"FAMILLE: {family_name}")
        print(f"Description: {family_config['description']}")
        print(f"has_draw: {family_config['has_draw']}")
        print(f"{'='*80}")
        
        try:
            # Récupérer les ligues de cette famille
            meta = model_loader.models[family_name]["meta"]
            leagues = meta.get("leagues", [])
            print(f"\n{len(leagues)} ligues trouvées")
            
            family_predictions = {}
            
            # Tester chaque ligue
            for i, league in enumerate(leagues, 1):
                print(f"\n[{i}/{len(leagues)}] Ligue: {league}")
                
                # Créer des équipes fictives pour le test
                team_home = f"Team_Home_{i}"
                team_away = f"Team_Away_{i}"
                
                try:
                    # Faire la prédiction
                    prediction = model_loader.predict(team_home, team_away, league)
                    
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
                        "1x2": {"home": round(home_prob, 3), "draw": round(draw_prob, 3), "away": round(away_prob, 3)},
                        "total_goals": round(total_goals, 1)
                    }
                
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
    
    import json
    with open("all_leagues_predictions_local.json", "w", encoding='utf-8') as f:
        json.dump(all_predictions, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Résultats sauvegardés dans all_leagues_predictions_local.json")
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
    
    # Afficher un résumé par famille
    print(f"\n{'='*80}")
    print("RÉSUMÉ PAR FAMILLE")
    print(f"{'='*80}")
    
    for family_name, leagues in all_predictions.items():
        if isinstance(leagues, dict) and "error" not in leagues:
            print(f"\n{family_name}:")
            print(f"  Ligues testées: {len(leagues)}")
            successful = len([l for l in leagues.values() if "error" not in l])
            print(f"  Réussies: {successful}")
            
            # Afficher quelques exemples
            count = 0
            for league, pred in leagues.items():
                if "error" not in pred and count < 2:
                    print(f"  Exemple: {league} -> {pred['exact_score']}")
                    count += 1
    
    return all_predictions

if __name__ == "__main__":
    test_all_leagues_local()
