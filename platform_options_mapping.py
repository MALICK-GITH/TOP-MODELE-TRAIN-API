"""
Mapping des options de paris disponibles sur la plateforme
Basé sur l'analyse des familles de ligues et leurs caractéristiques
"""

# Options spécifiques par famille de ligue
FAMILY_OPTIONS = {
    "PENALTY": {
        "avg_goals": 6.52,
        "has_draw": True,
        "handicap": {
            "available": True,
            "values": [-4.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
            "step": 0.5
        },
        "total_goals": {
            "available": True,
            "values": [3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5],
            "step": 0.5
        },
        "over_under": {
            "available": True,
            "values": [5.5, 6.5, 7.5, 8.5, 9.5],
            "step": 0.5
        }
    },
    "HIGHSCORE": {
        "avg_goals": 15.16,
        "has_draw": True,
        "handicap": {
            "available": True,
            "values": [-8.0, -7.5, -7.0, -6.5, -6.0, -5.5, -5.0, -4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0],
            "step": 0.5
        },
        "total_goals": {
            "available": True,
            "values": [10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5, 21.5, 22.5, 23.5, 24.5, 25.5],
            "step": 0.5
        },
        "over_under": {
            "available": True,
            "values": [12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5],
            "step": 0.5
        }
    },
    "RUSH": {
        "avg_goals": 7.52,
        "has_draw": True,
        "handicap": {
            "available": True,
            "values": [-5.0, -4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
            "step": 0.5
        },
        "total_goals": {
            "available": True,
            "values": [4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5],
            "step": 0.5
        },
        "over_under": {
            "available": True,
            "values": [6.5, 7.5, 8.5, 9.5, 10.5, 11.5],
            "step": 0.5
        }
    },
    "CLASSIC": {
        "avg_goals": 3.12,
        "has_draw": True,
        "handicap": {
            "available": True,
            "values": [-3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
            "step": 0.5
        },
        "total_goals": {
            "available": True,
            "values": [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5],
            "step": 0.5
        },
        "over_under": {
            "available": True,
            "values": [2.5, 3.5, 4.5, 5.5, 6.5],
            "step": 0.5
        }
    }
}

def map_prediction_to_platform(prediction_type, predicted_value, family):
    """
    Mappe une prédiction du modèle à l'option la plus proche disponible sur la plateforme
    pour une famille spécifique
    
    Args:
        prediction_type: Type de prédiction ('handicap', 'total_goals', 'over_under')
        predicted_value: Valeur prédite par le modèle
        family: Famille de ligue (PENALTY, HIGHSCORE, RUSH, CLASSIC)
    
    Returns:
        Tuple (option_value, option_name) la plus proche
    """
    if family not in FAMILY_OPTIONS:
        return (None, None)
    
    family_config = FAMILY_OPTIONS[family]
    
    if prediction_type == "handicap" and family_config["handicap"]["available"]:
        options = family_config["handicap"]["values"]
        closest = min(options, key=lambda x: abs(x - predicted_value))
        return (closest, "Handicap")
    
    elif prediction_type == "total_goals" and family_config["total_goals"]["available"]:
        options = family_config["total_goals"]["values"]
        closest = min(options, key=lambda x: abs(x - predicted_value))
        return (closest, "Total Goals")
    
    elif prediction_type == "over_under" and family_config["over_under"]["available"]:
        options = family_config["over_under"]["values"]
        closest = min(options, key=lambda x: abs(x - predicted_value))
        return (closest, "Over/Under")
    
    else:
        return (None, None)

def get_available_options_for_family(family):
    """
    Retourne les options disponibles pour une famille spécifique
    """
    if family not in FAMILY_OPTIONS:
        return {}
    
    return FAMILY_OPTIONS[family]

if __name__ == "__main__":
    # Test du mapping
    print("Test du mapping des prédictions vers les options de la plateforme")
    print("="*80)
    
    test_predictions = [
        ("handicap", 0.9),
        ("handicap", -2.0),
        ("total_goals", 7.9),
        ("total_goals", 6.1),
        ("over_under", 2.5),
    ]
    
    for pred_type, pred_value in test_predictions:
        opt_type, opt_value, opt_name = map_prediction_to_platform(pred_type, pred_value)
        print(f"{pred_type:15} {pred_value:5.1f} -> {opt_type:5} {opt_value:5.1f} ({opt_name})")
