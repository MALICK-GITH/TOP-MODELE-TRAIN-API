"""
Parser pour les options de marché dynamiques
Extrait les options disponibles depuis la réponse de l'API de marché
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class MarketOption:
    """Représente une option de marché"""
    value: float
    coefficient: float
    type_id: int
    group_id: int


class MarketParser:
    """Parse les réponses de l'API de marché pour extraire les options disponibles"""
    
    # Mapping des types d'options vers nos types de prédiction
    TYPE_MAPPING = {
        # 1x2
        1: "home",
        2: "draw",
        3: "away",
        4: "x2",
        5: "1x",
        6: "12",
        
        # Handicap
        7: "handicap_home",
        8: "handicap_away",
        
        # Total Goals
        9: "total_goals_under",
        10: "total_goals_over",
        
        # Over/Under (différents seuils)
        11: "over_under_1",
        12: "over_under_2",
        13: "over_under_3",
        14: "over_under_4",
        
        # 1ère mi-temps
        180: "first_half_home",
        181: "first_half_away",
    }
    
    # Mapping des groupes vers nos catégories
    GROUP_MAPPING = {
        2: "handicap",
        15: "over_under",
        17: "total_goals",
        19: "first_half",
        62: "over_under_alt",
    }
    
    @staticmethod
    def parse_market_data(market_data: Dict[str, Any]) -> Dict[str, List[MarketOption]]:
        """
        Parse les données de marché pour un match
        
        Args:
            market_data: Données JSON de l'API de marché pour un match
            
        Returns:
            Dictionnaire des options disponibles par catégorie
        """
        options = {
            "handicap": [],
            "total_goals": [],
            "over_under": [],
            "1x2": [],
        }
        
        # Parser les événements principaux (E)
        if "E" in market_data:
            MarketParser._parse_events(market_data["E"], options)
        
        # Parser les événements additionnels (AE)
        if "AE" in market_data:
            for group in market_data["AE"]:
                if "ME" in group:
                    MarketParser._parse_events(group["ME"], options)
        
        return options
    
    @staticmethod
    def _parse_events(events: List[Dict[str, Any]], options: Dict[str, List[MarketOption]]):
        """Parse une liste d'événements"""
        for event in events:
            type_id = event.get("T")
            param = event.get("P", 0)  # Valeur du handicap ou seuil
            coefficient = event.get("C", 1.0)
            group_id = event.get("G", 0)
            
            # Ignorer les événements sans paramètre (1x2 simple)
            if param is None:
                continue
            
            # Classifier selon le groupe
            if group_id == 2:  # Handicap
                options["handicap"].append(MarketOption(
                    value=float(param),
                    coefficient=float(coefficient),
                    type_id=type_id,
                    group_id=group_id
                ))
            elif group_id == 17:  # Total Goals
                options["total_goals"].append(MarketOption(
                    value=float(param),
                    coefficient=float(coefficient),
                    type_id=type_id,
                    group_id=group_id
                ))
            elif group_id in [15, 62]:  # Over/Under
                options["over_under"].append(MarketOption(
                    value=float(param),
                    coefficient=float(coefficient),
                    type_id=type_id,
                    group_id=group_id
                ))
    
    @staticmethod
    def find_closest_option(predicted_value: float, available_options: List[MarketOption]) -> Optional[MarketOption]:
        """
        Trouve l'option la plus proche à la valeur prédite
        
        Args:
            predicted_value: Valeur prédite par le modèle
            available_options: Liste des options disponibles
            
        Returns:
            L'option la plus proche ou None si aucune option disponible
        """
        if not available_options:
            return None
        
        closest = min(available_options, key=lambda opt: abs(opt.value - predicted_value))
        return closest
    
    @staticmethod
    def extract_match_info(market_data: Dict[str, Any]) -> Dict[str, str]:
        """Extrait les informations de base du match"""
        return {
            "team_home": market_data.get("O1", ""),
            "team_away": market_data.get("O2", ""),
            "league": market_data.get("L", ""),
            "league_id": str(market_data.get("LI", "")),
        }


def test_parser():
    """Test du parser avec un exemple de données"""
    # Exemple simplifié basé sur les données fournies
    sample_data = {
        "O1": "Borussia Dortmund",
        "O2": "Club Atlético de Madrid",
        "L": "FC 26. 5x5 Rush. Superligue",
        "E": [
            {"T": 9, "P": 7.5, "C": 2.0, "G": 17},
            {"T": 10, "P": 7.5, "C": 1.81, "G": 17},
        ],
        "AE": [
            {
                "G": 2,
                "ME": [
                    {"T": 7, "P": -1.0, "C": 3.03, "G": 2},
                    {"T": 8, "P": -1.0, "C": 2.625, "G": 2},
                ]
            }
        ]
    }
    
    options = MarketParser.parse_market_data(sample_data)
    print("Options extraites:")
    for category, opts in options.items():
        print(f"  {category}: {[f'{opt.value} ({opt.coefficient})' for opt in opts]}")
    
    # Test de recherche d'option la plus proche
    predicted = 8.0
    closest = MarketParser.find_closest_option(predicted, options["total_goals"])
    if closest:
        print(f"\nPour prédiction {predicted}, option la plus proche: {closest.value} (cote: {closest.coefficient})")


if __name__ == "__main__":
    test_parser()
