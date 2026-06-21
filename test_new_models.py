"""
Test des nouveaux modèles entraînés avec trainBest.py
"""
import pickle
import pandas as pd
import numpy as np
from scipy.stats import poisson
from platform_options_mapping import map_prediction_to_platform

def load_models(model_dir="models"):
    """Charge tous les modèles entraînés"""
    models = {}
    for family in ["PENALTY", "HIGHSCORE", "RUSH", "CLASSIC"]:
        model_path = f"{model_dir}/{family}.pkl"
        with open(model_path, "rb") as f:
            models[family] = pickle.load(f)
        print(f"✅ {family} chargé")
    return models

def predict_score_exact(lambda_home, lambda_away, max_goals=15):
    """Prédit le score exact le plus probable avec Poisson"""
    best_score = (0, 0)
    best_prob = 0
    
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = poisson.pmf(h, lambda_home) * poisson.pmf(a, lambda_away)
            if prob > best_prob:
                best_prob = prob
                best_score = (h, a)
    
    return f"{best_score[0]}-{best_score[1]}"

def test_all_leagues(models):
    """Teste les prédictions sur toutes les ligues"""
    
    print("\n" + "="*80)
    print("TEST DE PRÉDICTION SUR CHAQUE LIGUE")
    print("="*80)
    
    all_predictions = {}
    
    for family_name, model_data in models.items():
        print(f"\n{'='*80}")
        print(f"FAMILLE: {family_name}")
        print(f"Description: {model_data['meta']['total_matches']} matchs")
        print(f"Has draw: {model_data['meta']['has_draw']}")
        print(f"Avg goals: {model_data['meta']['avg_goals']}")
        print(f"{'='*80}")
        
        leagues = model_data["leagues"]
        print(f"\n{len(leagues)} ligues trouvées")
        
        family_predictions = {}
        
        # Tester chaque ligue
        for i, league in enumerate(leagues, 1):
            print(f"\n[{i}/{len(leagues)}] Ligue: {league}")
            
            # Créer des équipes fictives pour le test
            team_home = f"Team_Home_{i}"
            team_away = f"Team_Away_{i}"
            
            try:
                # Créer des features fictifs variés pour simuler des équipes différentes
                import random
                random.seed(i)  # Seed pour reproductibilité
                
                features = {}
                for feat in model_data["features"]:
                    # Valeurs variées pour les features
                    if "n" in feat:  # nombre de matchs
                        features[feat] = random.randint(5, 20)
                    elif "wr" in feat or "pts" in feat or "form" in feat:  # taux
                        features[feat] = random.uniform(0.2, 0.8)
                    elif "gf" in feat or "ga" in feat or "tot" in feat:  # buts
                        features[feat] = random.uniform(0.5, 3.0)
                    elif "h2h" in feat:  # H2H
                        features[feat] = random.uniform(0.3, 0.7)
                    elif "diff" in feat:  # différentiels
                        features[feat] = random.uniform(-1.0, 1.0)
                    else:
                        features[feat] = random.uniform(0.3, 0.7)
                
                X = pd.DataFrame([features])
                
                # Prédire 1X2
                model_1x2 = model_data["models"]["1x2"]
                pred_1x2 = model_1x2.predict(X)[0]
                prob_1x2 = model_1x2.predict_proba(X)[0]
                
                # Prédire Over/Under
                model_ou = model_data["models"]["over_under"]
                pred_ou = model_ou.predict(X)[0]
                prob_ou = model_ou.predict_proba(X)[0]
                
                # Prédire BTTS
                model_btts = model_data["models"]["btts"]
                pred_btts = model_btts.predict(X)[0]
                prob_btts = model_btts.predict_proba(X)[0]
                
                # Prédire Parité
                model_parity = model_data["models"]["parity"]
                pred_parity = model_parity.predict(X)[0]
                prob_parity = model_parity.predict_proba(X)[0]
                
                # Score exact avec Poisson dynamique
                if "poisson_lambda_home" in model_data["models"] and "poisson_lambda_away" in model_data["models"]:
                    # Nouveau modèle dynamique
                    model_lambda_home = model_data["models"]["poisson_lambda_home"]
                    model_lambda_away = model_data["models"]["poisson_lambda_away"]
                    lambda_home = model_lambda_home.predict(X)[0]
                    lambda_away = model_lambda_away.predict(X)[0]
                    print(f"   λ_home={lambda_home:.2f}, λ_away={lambda_away:.2f}")
                else:
                    # Ancien modèle avec lambdas fixes
                    poisson_params = model_data["models"]["poisson"]
                    lambda_home = poisson_params["lambda_home"]
                    lambda_away = poisson_params["lambda_away"]
                    print(f"   λ_home={lambda_home:.2f} (fixe), λ_away={lambda_away:.2f} (fixe)")
                
                exact_score = predict_score_exact(lambda_home, lambda_away)
                
                # Calculer Total Goals et Handicap
                total_goals_pred = round(lambda_home + lambda_away, 1)
                handicap_pred = round(lambda_home - lambda_away, 1)
                
                # Mapper les prédictions aux options de la plateforme spécifiques à la famille
                handicap_opt_value, handicap_opt_name = map_prediction_to_platform("handicap", handicap_pred, family_name)
                total_goals_opt_value, total_goals_opt_name = map_prediction_to_platform("total_goals", total_goals_pred, family_name)
                
                # Afficher les résultats
                print(f"   ✅ Score exact: {exact_score}")
                print(f"   1X2: H={prob_1x2[0]:.3f}, D={prob_1x2[1]:.3f}, A={prob_1x2[2]:.3f}")
                print(f"   Total Goals: {total_goals_pred} -> Plateforme: {total_goals_opt_value} ({total_goals_opt_name})")
                print(f"   Handicap: {handicap_pred:+.1f} -> Plateforme: {handicap_opt_value:+.1f} ({handicap_opt_name})")
                print(f"   O/U: U={prob_ou[0]:.3f}, O={prob_ou[1]:.3f}")
                print(f"   BTTS: Non={prob_btts[0]:.3f}, Oui={prob_btts[1]:.3f}")
                print(f"   Parité: Pair={prob_parity[0]:.3f}, Impair={prob_parity[1]:.3f}")
                
                family_predictions[league] = {
                    "exact_score": exact_score,
                    "lambda_home": round(lambda_home, 2),
                    "lambda_away": round(lambda_away, 2),
                    "total_goals": total_goals_pred,
                    "total_goals_platform": {
                        "value": total_goals_opt_value,
                        "name": total_goals_opt_name
                    },
                    "handicap": handicap_pred,
                    "handicap_platform": {
                        "value": handicap_opt_value,
                        "name": handicap_opt_name
                    },
                    "1x2": {"home": round(prob_1x2[0], 3), "draw": round(prob_1x2[1], 3), "away": round(prob_1x2[2], 3)},
                    "over_under": {"under": round(prob_ou[0], 3), "over": round(prob_ou[1], 3)},
                    "btts": {"no": round(prob_btts[0], 3), "yes": round(prob_btts[1], 3)},
                    "parity": {"pair": round(prob_parity[0], 3), "impair": round(prob_parity[1], 3)}
                }
            
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                family_predictions[league] = {"error": str(e)}
        
        all_predictions[family_name] = family_predictions
    
    # Sauvegarder les résultats
    print(f"\n{'='*80}")
    print("RÉSUMÉ")
    print(f"{'='*80}")
    
    import json
    with open("new_models_predictions.json", "w", encoding='utf-8') as f:
        json.dump(all_predictions, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Résultats sauvegardés dans new_models_predictions.json")
    print(f"Total familles testées: {len(all_predictions)}")
    
    # Compter les prédictions réussies
    total_leagues = 0
    successful_predictions = 0
    
    for family_name, leagues in all_predictions.items():
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
        successful = len([l for l in leagues.values() if "error" not in l])
        print(f"\n{family_name}:")
        print(f"  Ligues testées: {len(leagues)}")
        print(f"  Réussies: {successful}")
        
        # Afficher quelques exemples
        count = 0
        for league, pred in leagues.items():
            if "error" not in pred and count < 2:
                print(f"  Exemple: {league} -> {pred['exact_score']}")
                count += 1
    
    return all_predictions

if __name__ == "__main__":
    models = load_models()
    test_all_leagues(models)
