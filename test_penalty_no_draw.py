"""
Test pour vérifier que PENALTY ne prédit plus de matchs nuls
"""
import sys
sys.path.insert(0, r"c:\Users\HP\Downloads\TRAIN CSV MODELE FIFA")

from train_random_forest import ModelLoader

def test_penalty_no_draw():
    """Teste que PENALTY ne prédit plus de matchs nuls"""
    
    print("=" * 80)
    print("TEST PENALTY - VÉRIFICATION ABSENCE DE NULS")
    print("=" * 80)
    
    # Charger les modèles
    csv_path = r"c:\Users\HP\Downloads\TRAIN CSV MODELE FIFA\finished_matches.csv"
    model_loader = ModelLoader("./models", csv_path=csv_path)
    model_loader.load_all()
    
    # Tester différents matchs PENALTY
    test_matches = [
        ("Real Madrid", "Barcelona", "FC25. Penalty"),
        ("Manchester City", "Liverpool", "FC24. Penalty"),
        ("Arsenal", "Napoli", "FC26. Penalty"),
        ("PSG", "Bayern Munich", "FIFA23. Penalty"),
        ("Inter Milan", "AC Milan", "Penalty"),
    ]
    
    draw_count = 0
    exact_scores = []
    
    for team_home, team_away, league in test_matches:
        try:
            prediction = model_loader.predict(team_home, team_away, league)
            
            # Vérifier le 1X2
            home_prob = prediction["predictions"]["1x2"]["home"]
            draw_prob = prediction["predictions"]["1x2"]["draw"]
            away_prob = prediction["predictions"]["1x2"]["away"]
            
            # Vérifier le score exact
            exact_score = prediction["predictions"]["exact_score"]["prediction"]
            exact_scores.append(exact_score)
            
            # Vérifier si c'est un nul
            is_draw = exact_score.split("-")[0] == exact_score.split("-")[1]
            
            if is_draw:
                draw_count += 1
                print(f"❌ {team_home} vs {team_away}: {exact_score} (NUL - ERREUR!)")
            else:
                print(f"✅ {team_home} vs {team_away}: {exact_score} (Pas de nul)")
            
            print(f"   1X2: Home={home_prob:.3f}, Draw={draw_prob:.3f}, Away={away_prob:.3f}")
            
        except Exception as e:
            print(f"Erreur pour {team_home} vs {team_away}: {e}")
    
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print(f"Total des matchs testés: {len(test_matches)}")
    print(f"Nombre de nuls détectés: {draw_count}")
    print(f"Pourcentage de nuls: {draw_count / len(test_matches) * 100:.1f}%")
    print(f"\nScores exacts: {exact_scores}")
    
    if draw_count > 0:
        print("\n⚠️  PROBLÈME: PENALTY prédit encore des nuls!")
        return False
    else:
        print("\n✅ SUCCÈS: PENALTY ne prédit plus de nuls!")
        return True

if __name__ == "__main__":
    success = test_penalty_no_draw()
    sys.exit(0 if success else 1)
