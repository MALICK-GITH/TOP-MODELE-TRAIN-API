"""
Test des modèles avec des données de matchs en temps réel
"""
import pickle
import pandas as pd
import numpy as np
import json
from scipy.stats import poisson

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

def get_family_from_league(league):
    """Détermine la famille à partir de la ligue"""
    FAMILIES = {
        "FC24. Penalty":                         "PENALTY",
        "FC25. Penalty":                         "PENALTY",
        "FC26. Penalty":                         "PENALTY",
        "FIFA23. Penalty":                       "PENALTY",
        "Penalty":                               "PENALTY",
        "FC 24. 4x4. Championnat d'Angleterre":  "HIGHSCORE",
        "FC 25. 3x3. Ligue de conférence":       "HIGHSCORE",
        "FC 26. 5x5 Rush. Superligue":           "RUSH",
        "FC 25. Championnat d'Allemagne":        "CLASSIC",
        "FC 25. Championnat d'Angleterre":       "CLASSIC",
        "FC 25. Championnat d'Espagne":          "CLASSIC",
        "FC 25. Champions League":               "CLASSIC",
        "FC 25. Italy Championship":             "CLASSIC",
        "FC 25. Ligue européenne":               "CLASSIC",
        "FC 26. Championnat du monde":           "CLASSIC",
        "FC 26. Champions League":               "CLASSIC",
        "World Cup 2026. Simulation":            "CLASSIC",
    }
    return FAMILIES.get(league, "CLASSIC")

def test_live_matches(models, live_data):
    """Teste les modèles avec des données de matchs en temps réel"""
    
    print("\n" + "="*80)
    print("TEST DES MODÈLES AVEC DONNÉES EN TEMPS RÉEL")
    print("="*80)
    
    matches = live_data["Value"]
    print(f"\n{len(matches)} matchs à tester")
    
    results = []
    
    for i, match in enumerate(matches, 1):
        team_home = match["O1"]
        team_away = match["O2"]
        league = match["L"]
        family = get_family_from_league(league)
        
        print(f"\n[{i}/{len(matches)}] {team_home} vs {team_away}")
        print(f"   Ligue: {league}")
        print(f"   Famille: {family}")
        
        # Vérifier si le modèle existe pour cette famille
        if family not in models:
            print(f"   ❌ Modèle non disponible pour {family}")
            continue
        
        model_data = models[family]
        
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
            
            # Score actuel si disponible
            current_score = "N/A"
            if "SC" in match and "FS" in match["SC"]:
                fs = match["SC"]["FS"]
                if "S1" in fs and "S2" in fs:
                    current_score = f"{fs['S1']}-{fs['S2']}"
            
            # Afficher les résultats
            print(f"   Score actuel: {current_score}")
            print(f"   ✅ Score exact prédit: {exact_score}")
            print(f"   1X2: H={prob_1x2[0]:.3f}, D={prob_1x2[1]:.3f}, A={prob_1x2[2]:.3f}")
            print(f"   O/U: U={prob_ou[0]:.3f}, O={prob_ou[1]:.3f}")
            print(f"   BTTS: Non={prob_btts[0]:.3f}, Oui={prob_btts[1]:.3f}")
            print(f"   Parité: Pair={prob_parity[0]:.3f}, Impair={prob_parity[1]:.3f}")
            
            results.append({
                "match_id": match["I"],
                "team_home": team_home,
                "team_away": team_away,
                "league": league,
                "family": family,
                "current_score": current_score,
                "predicted_score": exact_score,
                "1x2": {"home": round(prob_1x2[0], 3), "draw": round(prob_1x2[1], 3), "away": round(prob_1x2[2], 3)},
                "over_under": {"under": round(prob_ou[0], 3), "over": round(prob_ou[1], 3)},
                "btts": {"no": round(prob_btts[0], 3), "yes": round(prob_btts[1], 3)},
                "parity": {"pair": round(prob_parity[0], 3), "impair": round(prob_parity[1], 3)}
            })
        
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            results.append({
                "match_id": match["I"],
                "team_home": team_home,
                "team_away": team_away,
                "league": league,
                "family": family,
                "error": str(e)
            })
    
    # Sauvegarder les résultats
    print(f"\n{'='*80}")
    print("RÉSUMÉ")
    print(f"{'='*80}")
    
    with open("live_matches_predictions.json", "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Résultats sauvegardés dans live_matches_predictions.json")
    print(f"Total matchs testés: {len(results)}")
    
    successful = len([r for r in results if "error" not in r])
    print(f"Prédictions réussies: {successful}")
    print(f"Taux de succès: {successful/len(results)*100:.1f}%" if len(results) > 0 else "N/A")
    
    # Résumé par famille
    print(f"\n{'='*80}")
    print("RÉSUMÉ PAR FAMILLE")
    print(f"{'='*80}")
    
    family_counts = {}
    for result in results:
        if "error" not in result:
            family = result["family"]
            if family not in family_counts:
                family_counts[family] = {"total": 0, "scores": []}
            family_counts[family]["total"] += 1
            family_counts[family]["scores"].append(result["predicted_score"])
    
    for family, data in family_counts.items():
        print(f"\n{family}:")
        print(f"  Matchs testés: {data['total']}")
        print(f"  Scores prédits: {set(data['scores'])}")
    
    return results

if __name__ == "__main__":
    # Charger les modèles
    models = load_models()
    
    # Charger les données de test
    with open("live_data.json", "r", encoding='utf-8') as f:
        live_data = json.load(f)
    
    # Tester les matchs
    test_live_matches(models, live_data)
