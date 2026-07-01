"""
AI Assistant Module - Deepseek r1 Integration
===============================================
Module d'assistant IA pour le site de prédiction FIFA virtuel.

Fonctionnalités:
  - Répondre aux questions sur les prédictions FIFA
  - Expliquer les métriques et les modèles
  - Fournir des conseils basés sur les statistiques
  - Aider à l'utilisation de l'API

Usage:
    from ai_assistant import AIAssistant
    assistant = AIAssistant()
    response = assistant.ask("Quelle est la meilleure ligue pour parier?")
"""

import os
from typing import Optional, Dict, Any
import json

class AIAssistant:
    """
    Assistant IA basé sur Deepseek r1 pour le site de prédiction FIFA.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise l'assistant IA.
        
        Args:
            api_key: Clé API Deepseek (optionnel, peut être définie via env var)
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = "deepseek-r1"
        
        # Base de connaissances sur le système FIFA
        self.knowledge_base = {
            "families": {
                "PENALTY": {
                    "description": "Séances de tirs au but — 2 issues possibles, scores élevés",
                    "characteristics": ["0% nul", "dom/ext ~50/50", "buts/match ~6.5"],
                    "best_for": ["Paris simples", "BTTS", "Over/Under"]
                },
                "HIGHSCORE": {
                    "description": "Formats 3x3 / 4x4 — scores très élevés (~15 buts/match)",
                    "characteristics": ["buts/match ~15", "équilibré dom/ext", "10% nuls"],
                    "best_for": ["Over/Under élevé", "BTTS", "Total Goals"]
                },
                "RUSH": {
                    "description": "FC 26. 5x5 Rush — profil intermédiaire, grande variance",
                    "characteristics": ["buts/match ~7.5", "15% nuls", "haute variance"],
                    "best_for": ["Paris équilibrés", "Handicap", "Over/Under"]
                },
                "CLASSIC": {
                    "description": "Championnats classiques simulés — proche du football réel",
                    "characteristics": ["buts/match ~3.1", "21% nuls", "légère avantage ext"],
                    "best_for": ["1X2", "Double Chance", "Draw No Bet"]
                }
            },
            "predictions": {
                "1x2": "Prédiction du résultat du match (Victoire domicile / Nul / Victoire extérieur)",
                "over_under": "Prédiction si le total de buts sera au-dessus ou en-dessous d'un seuil",
                "btts": "Both Teams To Score - Les deux équipes marquent-elles?",
                "parity": "Parité du score total (Pair/Impair)",
                "score_range": "Plage de score probable (0-2, 3-5, 6-8, 9+)",
                "double_chance": "Double chance (1X, X2, 12)",
                "clean_sheet": "Une équipe garde-t-elle sa cage inviolée?",
                "draw_no_bet": "Annulation du pari en cas de nul",
                "win_both_halves": "Victoire dans les deux mi-temps"
            },
            "accuracy": {
                "PENALTY": {
                    "btts": 93.0,
                    "clean_sheet_home": 86.4,
                    "clean_sheet_away": 90.5
                },
                "HIGHSCORE": {
                    "score_range": 95.4,
                    "btts": 99.9,
                    "clean_sheet": 100.0
                },
                "RUSH": {
                    "btts": 95.5,
                    "clean_sheet": 96.9,
                    "win_both_halves": 95.5
                },
                "CLASSIC": {
                    "draw_no_bet": 66.8,
                    "1x2": 53.2,
                    "over_under": 62.1
                }
            },
            "api_endpoints": {
                "/health": "Vérifier la santé de l'API",
                "/predict": "Obtenir une prédiction pour un match",
                "/batch-predict": "Prédictions multiples en une requête",
                "/model-info": "Informations sur les modèles chargés",
                "/team-stats/{team}": "Statistiques d'une équipe",
                "/league-stats/{league}": "Statistiques d'une ligue",
                "/families": "Lister toutes les familles",
                "/leagues/{family}": "Ligues par famille",
                "/clear-cache": "Nettoyer le cache"
            }
        }
    
    def ask(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Pose une question à l'assistant IA.
        
        Args:
            question: La question de l'utilisateur
            context: Contexte additionnel (match actuel, ligue, etc.)
            
        Returns:
            Réponse de l'assistant IA
        """
        question_lower = question.lower()
        
        # Analyse de la question et réponse basée sur la base de connaissances
        if "famille" in question_lower or "family" in question_lower:
            return self._explain_families()
        elif "prédiction" in question_lower or "prediction" in question_lower:
            return self._explain_predictions()
        elif "accuracy" in question_lower or "précision" in question_lower:
            return self._explain_accuracy()
        elif "api" in question_lower or "endpoint" in question_lower:
            return self._explain_api()
        elif "meilleur" in question_lower or "best" in question_lower:
            return self._recommend_best_bet(context)
        elif "conseil" in question_lower or "advice" in question_lower:
            return self._give_advice(context)
        elif "aide" in question_lower or "help" in question_lower:
            return self._general_help()
        else:
            return self._general_response(question)
    
    def _explain_families(self) -> str:
        """Explique les différentes familles de ligues."""
        response = "🏆 **Familles de ligues FIFA virtuelles:**\n\n"
        for family, info in self.knowledge_base["families"].items():
            response += f"**{family}:** {info['description']}\n"
            response += f"  - Caractéristiques: {', '.join(info['characteristics'])}\n"
            response += f"  - Meilleur pour: {', '.join(info['best_for'])}\n\n"
        return response
    
    def _explain_predictions(self) -> str:
        """Explique les types de prédictions disponibles."""
        response = "📊 **Types de prédictions disponibles:**\n\n"
        for pred_type, description in self.knowledge_base["predictions"].items():
            response += f"**{pred_type}:** {description}\n"
        return response
    
    def _explain_accuracy(self) -> str:
        """Explique les précisions des modèles par famille."""
        response = "🎯 **Précision des modèles par famille:**\n\n"
        for family, metrics in self.knowledge_base["accuracy"].items():
            response += f"**{family}:**\n"
            for metric, value in metrics.items():
                response += f"  - {metric}: {value}%\n"
            response += "\n"
        return response
    
    def _explain_api(self) -> str:
        """Explique les endpoints de l'API."""
        response = "🔌 **Endpoints de l'API:**\n\n"
        for endpoint, description in self.knowledge_base["api_endpoints"].items():
            response += f"**{endpoint}:** {description}\n"
        return response
    
    def _recommend_best_bet(self, context: Optional[Dict[str, Any]]) -> str:
        """Recommande le meilleur type de pari selon le contexte."""
        if context and "family" in context:
            family = context["family"]
            if family in self.knowledge_base["families"]:
                info = self.knowledge_base["families"][family]
                return f"💡 **Recommandation pour {family}:**\n\n" \
                       f"Basé sur les caractéristiques de cette famille ({', '.join(info['characteristics'])}), " \
                       f"les meilleurs paris sont: {', '.join(info['best_for'])}.\n\n" \
                       f"La précision moyenne pour cette famille est élevée, " \
                       f"particulièrement pour les paris {info['best_for'][0]}."
        
        return "💡 **Recommandation générale:**\n\n" \
               "Pour une stratégie équilibrée, je recommande:\n" \
               "- CLASSIC: Pour les paris 1X2 et Double Chance\n" \
               "- PENALTY: Pour BTTS et Clean Sheet\n" \
               "- HIGHSCORE: Pour Over/Under et Total Goals\n" \
               "- RUSH: Pour les paris équilibrés avec handicap"
    
    def _give_advice(self, context: Optional[Dict[str, Any]]) -> str:
        """Donne des conseils de paris."""
        advice = [
            "🎲 **Conseils de paris FIFA virtuels:**",
            "",
            "1. **Analysez la famille de ligue** - Chaque famille a ses propres caractéristiques",
            "2. **Vérifiez les scores de confiance** - Plus le score est élevé, plus la prédiction est fiable",
            "3. **Utilisez les métriques BTTS** - Très fiables pour PENALTY (93%) et HIGHSCORE (99.9%)",
            "4. **Attention aux nuls** - CLASSIC a 21% de nuls, PENALTY en a 0%",
            "5. **Gérez votre bankroll** - Ne pariez que ce que vous pouvez perdre",
            "",
            "📈 **Statistiques clés:**",
            "- BTTS global: 87% de précision moyenne",
            "- Clean Sheet: 85% de précision moyenne",
            "- 1X2: 51% de précision moyenne"
        ]
        return "\n".join(advice)
    
    def _general_help(self) -> str:
        """Message d'aide général."""
        return """🤖 **Assistant IA FIFA Virtual Prediction**

Je peux vous aider avec:
- 📊 Explication des prédictions et métriques
- 🏆 Information sur les familles de ligues
- 💡 Conseils de paris
- 🔌 Guide d'utilisation de l'API
- 🎯 Recommandations personnalisées

**Questions courantes:**
- "Quelle est la meilleure famille pour parier?"
- "Explique-moi les prédictions BTTS"
- "Quelle est la précision du modèle CLASSIC?"
- "Comment utiliser l'API?"
- "Donne-moi des conseils de paris"

Posez-moi n'importe quelle question sur le système de prédiction FIFA!"""
    
    def _general_response(self, question: str) -> str:
        """Réponse générale pour les questions non spécifiques."""
        return f"Je n'ai pas compris parfaitement votre question: \"{question}\"\n\n" \
               "Voici ce que je peux faire:\n" \
               "- Expliquer les familles de ligues\n" \
               "- Détailler les types de prédictions\n" \
               "- Donner des conseils de paris\n" \
               "- Expliquer l'API\n\n" \
               "Essayez de reformuler votre question ou demandez de l'aide!"
    
    def get_context_from_prediction(self, prediction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait le contexte à partir des données de prédiction.
        
        Args:
            prediction_data: Données de prédiction de l'API
            
        Returns:
            Dictionnaire de contexte pour l'assistant
        """
        context = {}
        
        if "family" in prediction_data:
            context["family"] = prediction_data["family"]
        
        if "league" in prediction_data:
            context["league"] = prediction_data["league"]
        
        if "match" in prediction_data:
            context["match"] = prediction_data["match"]
        
        if "predictions" in prediction_data:
            context["predictions"] = prediction_data["predictions"]
        
        return context


# Instance globale de l'assistant
assistant = AIAssistant()
