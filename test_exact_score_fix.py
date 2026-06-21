"""
Test pour vérifier que les scores exacts ne sont plus tous 3-3
"""
import sys
sys.path.insert(0, r"c:\Users\HP\Downloads\TRAIN CSV MODELE FIFA")

from train_random_forest import ModelLoader

def test_exact_scores():
    """Teste que les scores exacts varient et ne sont pas tous 3-3"""
    
    print("=" * 80)
    print("TEST DES SCORES EXACTS - VÉRIFICATION DU BUG 3-3")
    print("=" * 80)
    
    # Charger les modèles
    csv_path = r"c:\Users\HP\Downloads\TRAIN CSV MODELE FIFA\finished_matches.csv"
    model_loader = ModelLoader("./models", csv_path=csv_path)
    model_loader.load_all()
    
    # Tester différents matchs
    test_matches = [
        ("Real Madrid", "Barcelona", "FC 25. Champions League"),
        ("Manchester City", "Liverpool", "FC 24. 4x4. Championnat d'Angleterre"),
        ("Arsenal", "Napoli", "FC 26. 5x5 Rush. Superligue"),
        ("PSG", "Bayern Munich", "FC25. Penalty"),
        ("Real Madrid", "Atletico Madrid", "FC 25. Champions League"),
        ("Manchester United", "Chelsea", "FC 25. Championnat d'Angleterre"),
        ("Inter Milan", "AC Milan", "FC 25. Italy Championship"),
        ("Bayern Munich", "Dortmund", "FC 25. Championnat d'Allemagne"),
    ]
    
    exact_scores = []
    three_three_count = 0
    
    for team_home, team_away, league in test_matches:
        try:
            prediction = model_loader.predict(team_home, team_away, league)
            exact_score = prediction["predictions"]["exact_score"]["prediction"]
            exact_scores.append(exact_score)
            
            if exact_score == "3-3":
                three_three_count += 1
            
            print(f"{team_home} vs {team_away} ({league[:30]}...): {exact_score}")
        except Exception as e:
            print(f"Erreur pour {team_home} vs {team_away}: {e}")
    
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print(f"Total des scores exacts testés: {len(exact_scores)}")
    print(f"Nombre de scores 3-3: {three_three_count}")
    print(f"Pourcentage de 3-3: {three_three_count / len(exact_scores) * 100:.1f}%")
    print(f"\nScores exacts uniques: {set(exact_scores)}")
    
    if three_three_count > len(exact_scores) * 0.5:
        print("\n⚠️  PROBLÈME: Trop de scores 3-3 détectés!")
        return False
    else:
        print("\n✅ SUCCÈS: Les scores exacts varient correctement!")
        return True

if __name__ == "__main__":
    success = test_exact_scores()
    sys.exit(0 if success else 1)
