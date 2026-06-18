"""
Test de cohérence automatique pour les prédictions FIFA
Vérifie que 1X2, parité et score exact sont toujours alignés
"""

import sys
import os
import pandas as pd
import numpy as np
from train_random_forest import ModelLoader

def test_coherence():
    """Teste la cohérence des prédictions sur un échantillon de matchs"""
    
    print("=" * 80)
    print("TEST DE COHÉRENCE DES PRÉDICTIONS")
    print("=" * 80)
    
    # Charger les modèles
    models_dir = "./models"
    csv_path = "finished_matches.csv"
    
    if not os.path.exists(models_dir):
        print("❌ Erreur: Répertoire des modèles non trouvé")
        return False
    
    model_loader = ModelLoader(models_dir, csv_path=csv_path)
    model_loader.load_all()
    
    if not model_loader.loaded:
        print("❌ Erreur: Modèles non chargés")
        return False
    
    print(f"✅ Modèles chargés: {len(model_loader.models)} familles")
    
    # Charger les données de test
    if not os.path.exists(csv_path):
        print("❌ Erreur: Fichier CSV non trouvé")
        return False
    
    df = pd.read_csv(csv_path)
    df["finished_at"] = pd.to_datetime(df["finished_at"], utc=True, format='ISO8601')
    
    # Sélectionner un échantillon de matchs pour le test
    sample_size = 20
    sample_df = df.sample(min(sample_size, len(df)), random_state=42)
    
    print(f"📊 Échantillon de {len(sample_df)} matchs pour le test")
    
    # Tester les prédictions
    inconsistencies = []
    total_tests = 0
    
    for _, row in sample_df.iterrows():
        team_home = row["team_home"]
        team_away = row["team_away"]
        league = row["league"]
        
        try:
            prediction = model_loader.predict(team_home, team_away, league)
            
            # Extraire les données
            exact_score_str = prediction["predictions"]["exact_score"]["prediction"]
            exact_home, exact_away = map(int, exact_score_str.split("-"))
            
            # Dériver le 1X2 attendu du score exact
            if exact_home > exact_away:
                expected_1x2 = "1"
                expected_result = "home"
            elif exact_home == exact_away:
                expected_1x2 = "X"
                expected_result = "draw"
            else:
                expected_1x2 = "2"
                expected_result = "away"
            
            # Dériver la parité attendue du score exact
            exact_total = exact_home + exact_away
            expected_parity = "pair" if exact_total % 2 == 0 else "impair"
            
            # Vérifier les probabilités 1X2
            home_prob = prediction["predictions"]["1x2"]["home"]
            draw_prob = prediction["predictions"]["1x2"]["draw"]
            away_prob = prediction["predictions"]["1x2"]["away"]
            
            # Vérifier que les probabilités correspondent au résultat dérivé
            if expected_result == "home" and home_prob < 0.5:
                inconsistencies.append({
                    "match": f"{team_home} vs {team_away}",
                    "league": league,
                    "exact_score": exact_score_str,
                    "expected_1x2": expected_1x2,
                    "home_prob": home_prob,
                    "draw_prob": draw_prob,
                    "away_prob": away_prob,
                    "issue": "1X2 incohérent: home devrait être favori"
                })
            elif expected_result == "draw" and draw_prob < 0.4:
                inconsistencies.append({
                    "match": f"{team_home} vs {team_away}",
                    "league": league,
                    "exact_score": exact_score_str,
                    "expected_1x2": expected_1x2,
                    "home_prob": home_prob,
                    "draw_prob": draw_prob,
                    "away_prob": away_prob,
                    "issue": "1X2 incohérent: draw devrait être favori"
                })
            elif expected_result == "away" and away_prob < 0.5:
                inconsistencies.append({
                    "match": f"{team_home} vs {team_away}",
                    "league": league,
                    "exact_score": exact_score_str,
                    "expected_1x2": expected_1x2,
                    "home_prob": home_prob,
                    "draw_prob": draw_prob,
                    "away_prob": away_prob,
                    "issue": "1X2 incohérent: away devrait être favori"
                })
            
            # Vérifier les probabilités de parité
            pair_prob = prediction["predictions"]["parity"]["pair"]
            impair_prob = prediction["predictions"]["parity"]["impair"]
            
            if expected_parity == "pair" and pair_prob < 0.5:
                inconsistencies.append({
                    "match": f"{team_home} vs {team_away}",
                    "league": league,
                    "exact_score": exact_score_str,
                    "expected_parity": expected_parity,
                    "pair_prob": pair_prob,
                    "impair_prob": impair_prob,
                    "issue": "Parité incohérente: pair devrait être favori"
                })
            elif expected_parity == "impair" and impair_prob < 0.5:
                inconsistencies.append({
                    "match": f"{team_home} vs {team_away}",
                    "league": league,
                    "exact_score": exact_score_str,
                    "expected_parity": expected_parity,
                    "pair_prob": pair_prob,
                    "impair_prob": impair_prob,
                    "issue": "Parité incohérente: impair devrait être favori"
                })
            
            total_tests += 1
            
        except Exception as e:
            print(f"⚠️  Erreur pour {team_home} vs {team_away}: {e}")
            continue
    
    # Afficher les résultats
    print(f"\n📈 Résultats du test:")
    print(f"   Total des tests: {total_tests}")
    print(f"   Incohérences trouvées: {len(inconsistencies)}")
    
    if inconsistencies:
        print(f"\n❌ INCOHÉRENCES DÉTECTÉES:")
        for i, inc in enumerate(inconsistencies, 1):
            print(f"\n{i}. {inc['match']} ({inc['league']})")
            print(f"   Score exact: {inc['exact_score']}")
            print(f"   Problème: {inc['issue']}")
            if "home_prob" in inc:
                print(f"   1X2: home={inc['home_prob']:.3f}, draw={inc['draw_prob']:.3f}, away={inc['away_prob']:.3f}")
            if "pair_prob" in inc:
                print(f"   Parité: pair={inc['pair_prob']:.3f}, impair={inc['impair_prob']:.3f}")
        
        print(f"\n❌ TEST ÉCHOUÉ: {len(inconsistences)} incohérences détectées")
        return False
    else:
        print(f"\n✅ TEST RÉUSSI: Toutes les prédictions sont cohérentes")
        print(f"   1X2 et parité sont correctement dérivés du score exact")
        return True

if __name__ == "__main__":
    success = test_coherence()
    sys.exit(0 if success else 1)
