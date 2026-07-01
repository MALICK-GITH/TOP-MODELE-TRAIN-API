"""
Test de l'adaptation dynamique du score_range au marché
Vérifie que les plages de score s'adaptent aux options disponibles
"""

from market_parser import MarketParser, MarketOption

def test_dynamic_score_range():
    """Test l'adaptation des plages de score selon le marché"""
    
    print("🧪 Test de l'adaptation dynamique du score_range")
    print("=" * 60)
    
    # Test 1: Marché RUSH avec options 4.5 à 15.5
    print("\n📊 Test 1: Marché RUSH (options 4.5-15.5)")
    market_data_rush = {
        "O1": "Liverpool",
        "O2": "Borussia Dortmund",
        "L": "FC 26. 5x5 Rush. Superligue",
        "E": [
            {"T": 9, "P": 7.5, "C": 2.0, "G": 17},
            {"T": 10, "P": 7.5, "C": 1.81, "G": 17},
        ],
        "AE": [
            {
                "G": 17,
                "ME": [
                    {"T": 9, "P": 4.5, "C": 2.1, "G": 17},
                    {"T": 10, "P": 4.5, "C": 1.9, "G": 17},
                    {"T": 9, "P": 15.5, "C": 3.5, "G": 17},
                    {"T": 10, "P": 15.5, "C": 1.4, "G": 17},
                ]
            }
        ]
    }
    
    options_rush = MarketParser.parse_market_data(market_data_rush)
    total_goals_rush = sorted([opt.value for opt in options_rush["total_goals"]])
    print(f"Options Total Goals disponibles: {total_goals_rush}")
    
    # Simulation de la logique d'adaptation
    score_range_labels = ["0-2", "3-5", "6-8", "9+"]
    if total_goals_rush:
        if len(total_goals_rush) >= 4:
            score_range_labels = [
                f"0-{int(total_goals_rush[0])}",
                f"{int(total_goals_rush[0])+1}-{int(total_goals_rush[len(total_goals_rush)//2])}",
                f"{int(total_goals_rush[len(total_goals_rush)//2])+1}-{int(total_goals_rush[-1])}",
                f"{int(total_goals_rush[-1])+1}+"
            ]
        elif len(total_goals_rush) >= 2:
            mid_point = total_goals_rush[len(total_goals_rush)//2]
            score_range_labels = [
                f"0-{int(mid_point)}",
                f"{int(mid_point)+1}-{int(total_goals_rush[-1])}",
                f"{int(total_goals_rush[-1])+1}-{int(total_goals_rush[-1])+3}",
                f"{int(total_goals_rush[-1])+4}+"
            ]
    
    print(f"Plages de score adaptées: {score_range_labels}")
    
    # Test 2: Marché CLASSIC avec options 0.5 à 8.5
    print("\n📊 Test 2: Marché CLASSIC (options 0.5-8.5)")
    market_data_classic = {
        "O1": "Real Madrid",
        "O2": "Barcelona",
        "L": "FC 25. Champions League",
        "E": [
            {"T": 9, "P": 2.5, "C": 2.0, "G": 17},
            {"T": 10, "P": 2.5, "C": 1.81, "G": 17},
        ],
        "AE": [
            {
                "G": 17,
                "ME": [
                    {"T": 9, "P": 0.5, "C": 3.5, "G": 17},
                    {"T": 10, "P": 0.5, "C": 1.3, "G": 17},
                    {"T": 9, "P": 8.5, "C": 4.0, "G": 17},
                    {"T": 10, "P": 8.5, "C": 1.2, "G": 17},
                ]
            }
        ]
    }
    
    options_classic = MarketParser.parse_market_data(market_data_classic)
    total_goals_classic = sorted([opt.value for opt in options_classic["total_goals"]])
    print(f"Options Total Goals disponibles: {total_goals_classic}")
    
    score_range_labels_classic = ["0-2", "3-5", "6-8", "9+"]
    if total_goals_classic:
        if len(total_goals_classic) >= 4:
            score_range_labels_classic = [
                f"0-{int(total_goals_classic[0])}",
                f"{int(total_goals_classic[0])+1}-{int(total_goals_classic[len(total_goals_classic)//2])}",
                f"{int(total_goals_classic[len(total_goals_classic)//2])+1}-{int(total_goals_classic[-1])}",
                f"{int(total_goals_classic[-1])+1}+"
            ]
        elif len(total_goals_classic) >= 2:
            mid_point = total_goals_classic[len(total_goals_classic)//2]
            score_range_labels_classic = [
                f"0-{int(mid_point)}",
                f"{int(mid_point)+1}-{int(total_goals_classic[-1])}",
                f"{int(total_goals_classic[-1])+1}-{int(total_goals_classic[-1])+3}",
                f"{int(total_goals_classic[-1])+4}+"
            ]
    
    print(f"Plages de score adaptées: {score_range_labels_classic}")
    
    # Test 3: Sans market_data (fallback)
    print("\n📊 Test 3: Sans market_data (fallback)")
    score_range_labels_fallback = ["0-2", "3-5", "6-8", "9+"]
    print(f"Plages de score par défaut: {score_range_labels_fallback}")
    
    print("\n✅ Tests terminés")
    print("\n📝 Résumé:")
    print(f"- RUSH: Plages adaptées = {score_range_labels}")
    print(f"- CLASSIC: Plages adaptées = {score_range_labels_classic}")
    print(f"- Fallback: Plages par défaut = {score_range_labels_fallback}")

if __name__ == "__main__":
    test_dynamic_score_range()
