import requests
import json

def check_coherence(team_home, team_away, league):
    """Vérifie la cohérence des prédictions pour un match"""
    response = requests.post(
        "http://localhost:8000/predict",
        json={
            "team_home": team_home,
            "team_away": team_away,
            "league": league
        }
    )
    
    data = response.json()
    predictions = data["predictions"]
    
    print(f"\n=== {data['match']} ({data['family']}) ===")
    
    # 1x2
    home_1x2 = predictions["1x2"]["home"]
    draw_1x2 = predictions["1x2"]["draw"]
    away_1x2 = predictions["1x2"]["away"]
    print(f"\n1x2: Home={home_1x2:.3f}, Draw={draw_1x2:.3f}, Away={away_1x2:.3f}")
    print(f"Somme: {home_1x2 + draw_1x2 + away_1x2:.3f}")
    
    # Total goals
    total_pred = predictions["total_goals"]["predicted"]
    print(f"\nTotal prédit: {total_pred}")
    
    # Over/Under
    over_under = predictions["total_goals"]["over_under"]
    print(f"\nOver/Under (seuils dynamiques autour de {total_pred}):")
    for threshold, probs in sorted(over_under.items(), key=lambda x: float(x[0])):
        over = probs["over"]
        under = probs["under"]
        print(f"  {threshold}: Over={over:.3f}, Under={under:.3f}, Somme={over+under:.3f}")
        
        # Vérifier la cohérence avec le total prédit
        if total_pred > float(threshold):
            expected_fav = "over"
        else:
            expected_fav = "under"
        
        actual_fav = "over" if over > under else "under"
        coherence = "✓" if expected_fav == actual_fav else "✗"
        print(f"    Cohérence: {coherence} (attendu: {expected_fav}, actuel: {actual_fav})")
    
    # Handicap
    handicap = predictions["handicap"]
    print(f"\nHandicap (seuils dynamiques):")
    for h, probs in sorted(handicap.items(), key=lambda x: float(x[0])):
        home = probs["home"]
        draw = probs["draw"]
        away = probs["away"]
        print(f"  {h}: Home={home:.3f}, Draw={draw:.3f}, Away={away:.3f}, Somme={home+draw+away:.3f}")
        
        # Vérifier la cohérence avec 1x2
        h_val = float(h)
        if h_val > 0:
            # Handicap positif pour home: home devrait être favori si home est favori en 1x2
            expected_fav = "home" if home_1x2 > 0.5 else "away"
        else:
            # Handicap négatif pour home: away devrait être favori si home est favori en 1x2
            expected_fav = "away" if home_1x2 > 0.5 else "home"
        
        actual_fav = max(["home", "draw", "away"], key=lambda x: probs[x])
        coherence = "✓" if expected_fav == actual_fav else "✗"
        print(f"    Cohérence: {coherence} (attendu: {expected_fav}, actuel: {actual_fav})")
    
    # Parity
    parity = predictions["parity"]
    print(f"\nParité: Pair={parity['pair']:.3f}, Impair={parity['impair']:.3f}")
    print(f"Somme: {parity['pair'] + parity['impair']:.3f}")
    
    # Exact score
    print(f"\nScore exact: {predictions['exact_score']['prediction']}")
    
    return data

# Démarrer l'API
import subprocess
import time

print("Démarrage de l'API...")
api_process = subprocess.Popen(["python", "api.py"], cwd=r"c:\Users\HP\Downloads\TRAIN CSV MODELE FIFA")
time.sleep(5)

try:
    # Tester avec différents matchs
    print("\n" + "="*60)
    print("VÉRIFICATION DE LA COHÉRENCE DES PRÉDICTIONS")
    print("="*60)
    
    check_coherence("Real Madrid", "Barcelona", "FC 25. Champions League")
    check_coherence("Manchester City", "Liverpool", "FC 24. 4x4. Championnat d'Angleterre")
    check_coherence("Arsenal", "Napoli", "FC 26. 5x5 Rush. Superligue")
    check_coherence("PSG", "Bayern Munich", "FC25. Penalty")
    
finally:
    # Arrêter l'API
    print("\nArrêt de l'API...")
    api_process.terminate()
    api_process.wait()
