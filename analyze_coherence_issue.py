import requests
import json

def analyze_coherence(team_home, team_away, league):
    """Analyse la cohérence des prédictions pour un match"""
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
    
    print(f"\n{'='*70}")
    print(f"ANALYSE DE COHÉRENCE: {data['match']} ({data['family']})")
    print(f"{'='*70}")
    
    # 1x2
    home_1x2 = predictions["1x2"]["home"]
    draw_1x2 = predictions["1x2"]["draw"]
    away_1x2 = predictions["1x2"]["away"]
    print(f"\n📊 1x2:")
    print(f"   Home: {home_1x2:.3f} ({home_1x2*100:.1f}%)")
    print(f"   Draw: {draw_1x2:.3f} ({draw_1x2*100:.1f}%)")
    print(f"   Away: {away_1x2:.3f} ({away_1x2*100:.1f}%)")
    print(f"   Somme: {home_1x2 + draw_1x2 + away_1x2:.3f}")
    
    # Total goals
    total_pred = predictions["total_goals"]["predicted"]
    print(f"\n📊 Total Goals:")
    print(f"   Prédit: {total_pred}")
    
    # Over/Under
    over_under = predictions["total_goals"]["over_under"]
    print(f"\n📊 Over/Under (seuils dynamiques autour de {total_pred}):")
    coherence_issues = []
    for threshold, probs in sorted(over_under.items(), key=lambda x: float(x[0])):
        over = probs["over"]
        under = probs["under"]
        threshold_val = float(threshold)
        
        # Vérifier la cohérence avec le total prédit
        if total_pred > threshold_val:
            expected_fav = "over"
        else:
            expected_fav = "under"
        
        actual_fav = "over" if over > under else "under"
        is_coherent = expected_fav == actual_fav
        
        status = "✓" if is_coherent else "✗"
        print(f"   {threshold}: Over={over:.3f}, Under={under:.3f} | {status} (attendu: {expected_fav}, actuel: {actual_fav})")
        
        if not is_coherent:
            coherence_issues.append(f"Over/Under {threshold}: incohérent (total={total_pred}, seuil={threshold})")
    
    # Handicap
    handicap = predictions["handicap"]
    print(f"\n📊 Handicap (seuils dynamiques):")
    for h, probs in sorted(handicap.items(), key=lambda x: float(x[0])):
        home = probs["home"]
        draw = probs["draw"]
        away = probs["away"]
        h_val = float(h)
        
        # Vérifier la cohérence avec 1x2
        if h_val > 0:
            # Handicap positif pour home: home devrait être favori si home est favori en 1x2
            expected_fav = "home" if home_1x2 > 0.5 else "away"
        elif h_val < 0:
            # Handicap négatif pour home: away devrait être favori si home est favori en 1x2
            expected_fav = "away" if home_1x2 > 0.5 else "home"
        else:
            expected_fav = "home" if home_1x2 > 0.5 else "away"
        
        actual_fav = max(["home", "draw", "away"], key=lambda x: probs[x])
        is_coherent = expected_fav == actual_fav
        
        status = "✓" if is_coherent else "✗"
        print(f"   {h}: Home={home:.3f}, Draw={draw:.3f}, Away={away:.3f} | {status} (attendu: {expected_fav}, actuel: {actual_fav})")
        
        if not is_coherent:
            coherence_issues.append(f"Handicap {h}: incohérent (1x2 favori=home, handicap favori={actual_fav})")
    
    # Résumé
    print(f"\n{'='*70}")
    if coherence_issues:
        print("⚠️  PROBLÈMES DE COHÉRENCE DÉTECTÉS:")
        for issue in coherence_issues:
            print(f"   - {issue}")
    else:
        print("✅ AUCUN PROBLÈME DE COHÉRENCE DÉTECTÉ (côté API)")
    print(f"{'='*70}")
    
    return data, coherence_issues

# Tester avec différents matchs
print("\n" + "="*70)
print("ANALYSE DE LA COHÉRENCE DES PRÉDICTIONS API")
print("="*70)

all_issues = []

data1, issues1 = analyze_coherence("Real Madrid", "Barcelona", "FC 25. Champions League")
all_issues.extend(issues1)

data2, issues2 = analyze_coherence("Manchester City", "Liverpool", "FC 24. 4x4. Championnat d'Angleterre")
all_issues.extend(issues2)

data3, issues3 = analyze_coherence("Arsenal", "Napoli", "FC 26. 5x5 Rush. Superligue")
all_issues.extend(issues3)

data4, issues4 = analyze_coherence("PSG", "Bayern Munich", "FC25. Penalty")
all_issues.extend(issues4)

print(f"\n{'='*70}")
print("RÉSUMÉ GLOBAL")
print(f"{'='*70}")
if all_issues:
    print(f"⚠️  {len(all_issues)} problème(s) de cohérence détecté(s)")
    for issue in all_issues:
        print(f"   - {issue}")
else:
    print("✅ AUCUN PROBLÈME DE COHÉRENCE DÉTECTÉ (côté API)")
    print("\n📝 CONCLUSION:")
    print("   Les prédictions de l'API sont cohérentes.")
    print("   Le problème se situe probablement au niveau de la plateforme.")
    print("   Vérifiez que la plateforme utilise correctement les données de l'API:")
    print("   - Les seuils over/under doivent être lus depuis predictions.total_goals.over_under")
    print("   - Les handicaps doivent être lus depuis predictions.handicap")
    print("   - Les probabilités doivent être utilisées directement")
print(f"{'='*70}")
