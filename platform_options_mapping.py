"""
Mapping des options de paris disponibles sur la plateforme
Basé sur l'analyse des familles de ligues et leurs caractéristiques
"""

# Options spécifiques par famille de ligue
# Basé sur les distributions réelles des données historiques
FAMILY_OPTIONS = {
    "PENALTY": {
        "avg_goals": 6.5,
        "has_draw": True,
        "handicap": {
            "available": True,
            "values": [-4, -3, -2, -1, 0, 1, 2, 3, 4],
            "step": 1
        },
        "total_goals": {
            "available": True,
            "values": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            "step": 1
        },
        "over_under": {
            "available": True,
            "values": [4, 5, 6, 7, 8, 9, 10],
            "step": 1
        }
    },
    "HIGHSCORE": {
        "avg_goals": 15.0,
        "has_draw": True,
        "handicap": {
            "available": True,
            "values": [-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8],
            "step": 1
        },
        "total_goals": {
            "available": True,
            "values": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
            "step": 1
        },
        "over_under": {
            "available": True,
            "values": [12, 13, 14, 15, 16, 17, 18, 19, 20],
            "step": 1
        }
    },
    "RUSH": {
        "avg_goals": 7.5,
        "has_draw": True,
        "handicap": {
            "available": True,
            "values": [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5],
            "step": 1
        },
        "total_goals": {
            "available": True,
            "values": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            "step": 1
        },
        "over_under": {
            "available": True,
            "values": [6, 7, 8, 9, 10, 11],
            "step": 1
        }
    },
    "CLASSIC": {
        "avg_goals": 3.2,
        "has_draw": True,
        "handicap": {
            "available": True,
            "values": [-3, -2, -1, 0, 1, 2, 3],
            "step": 1
        },
        "total_goals": {
            "available": True,
            "values": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "step": 1
        },
        "over_under": {
            "available": True,
            "values": [2, 3, 4, 5, 6],
            "step": 1
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
