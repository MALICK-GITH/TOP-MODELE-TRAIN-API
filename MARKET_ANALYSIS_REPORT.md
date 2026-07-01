# Rapport d'Analyse des Données de Marché FIFA
## Pour l'Entraînement des Modèles de Prédiction

**Date:** 2026-07-01  
**Source:** Données de marché JSON (20 matchs)  
**Objectif:** Comprendre les patterns de marché pour guider l'entraînement des modèles

---

## 📊 Résumé Exécutif

L'analyse des données de marché révèle **5 familles de ligues distinctes** avec des caractéristiques de marché très différentes. Les modèles doivent être entraînés pour s'adapter à ces patterns spécifiques, notamment en ce qui concerne les plages de scores, les handicaps et les options de total de buts.

---

## 🏆 Ligues Identifiées

### 1. **RUSH** - FC 26. 5x5 Rush. Superligue
- **Nombre de matchs analysés:** 4
- **Format:** 5x5 (5 joueurs par équipe)
- **Caractéristiques:**
  - Total Goals: 2.5 à 9.5 (plage moyenne)
  - Handicaps: -4.0 à +4.0 (grande amplitude)
  - Over/Under: 3.5 à 5.5
  - **Score exemple:** 2-5 (7 buts totaux)

### 2. **ENGLAND** - FC 24. 4x4. Championnat d'Angleterre
- **Nombre de matchs analysés:** 5
- **Format:** 4x4 (4 joueurs par équipe)
- **Caractéristiques:**
  - Total Goals: 6.5 à 16.5 (plage élevée)
  - Handicaps: -4.5 à +4.5 (grande amplitude)
  - Over/Under: 4.5 à 7.5
  - **Score exemple:** 8-4 (12 buts totaux)

### 3. **CLASSIC/CONFERENCE** - FC 25. 3x3. Ligue de conférence
- **Nombre de matchs analysés:** 4
- **Format:** 3x3 (3 joueurs par équipe)
- **Caractéristiques:**
  - Total Goals: 5.5 à 17.5 (plage très élevée)
  - Handicaps: -3.5 à +4.5
  - Over/Under: 6.5 à 7.5
  - **Score exemple:** 2-3 (5 buts totaux)

### 4. **CHAMPIONS** - FC 26. Champions League
- **Nombre de matchs analysés:** 5
- **Format:** Non spécifié (probablement 11v11 classique)
- **Caractéristiques:**
  - Total Goals: 1.5 à 5.5 (plage faible)
  - Handicaps: -3.5 à +3.5 (incluant demi-points)
  - Over/Under: 0.5 à 3.5
  - **Score exemple:** 1-3 (4 buts totaux)

### 5. **WORLD** - FC 26. Championnat du monde
- **Nombre de matchs analysés:** 2
- **Format:** Non spécifié (probablement 11v11 classique)
- **Caractéristiques:**
  - Total Goals: 1.5 à 5.5 (plage faible)
  - Handicaps: -2.5 à +2.5
  - Over/Under: 0.5 uniquement
  - **Score exemple:** Non disponible

---

## 📈 Analyse Globale des Options de Marché

### Total Goals (Toutes Ligues)
- **Plage complète:** 1.5 à 17.5
- **Valeurs observées:** [1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5]
- **Pattern:** Les options augmentent par incréments de 1.0, avec un saut entre 9.5 et 11.5

### Handicaps (Toutes Ligues)
- **Plage complète:** -4.5 à +4.5
- **Valeurs observées:** [-4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
- **Pattern:** Incréments de 0.5, avec handicap 0 absent (probablement implicite)

### Over/Under (Toutes Ligues)
- **Plage complète:** 0.5 à 7.5
- **Valeurs observées:** [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5]
- **Pattern:** Incréments de 1.0

---

## 🎯 Patterns par Famille de Ligue

### RUSH (5x5)
- **Score Range attendu:** 0-10 buts
- **Total Goals typique:** 2.5-9.5
- **Handicap typique:** -4.0 à +4.0
- **Caractéristique:** Matchs rapides avec scores modérés

### ENGLAND (4x4)
- **Score Range attendu:** 5-20 buts
- **Total Goals typique:** 6.5-16.5
- **Handicap typique:** -4.5 à +4.5
- **Caractéristique:** Scores élevés dus au format 4x4

### CLASSIC/CONFERENCE (3x3)
- **Score Range attendu:** 3-20 buts
- **Total Goals typique:** 5.5-17.5
- **Handicap typique:** -3.5 à +4.5
- **Caractéristique:** Grande variabilité de scores

### CHAMPIONS (11v11 probable)
- **Score Range attendu:** 0-8 buts
- **Total Goals typique:** 1.5-5.5
- **Handicap typique:** -3.5 à +3.5
- **Caractéristique:** Scores faibles, matchs compétitifs

### WORLD (11v11 probable)
- **Score Range attendu:** 0-8 buts
- **Total Goals typique:** 1.5-5.5
- **Handicap typique:** -2.5 à +2.5
- **Caractéristique:** Scores faibles, handicaps plus restreints

---

## 🔧 Recommandations pour l'Entraînement des Modèles

### 1. **Adaptation Dynamique des Score Ranges**
Les modèles doivent générer des labels de score range dynamiques basés sur les options de marché disponibles:

- **RUSH:** ["0-2", "3-5", "6-8", "9+"]
- **ENGLAND:** ["0-8", "9-12", "13-16", "17+"]
- **CLASSIC/CONFERENCE:** ["0-6", "7-10", "11-14", "15+"]
- **CHAMPIONS/WORLD:** ["0-2", "3-4", "5-6", "7+"]

### 2. **Mapping des Handicaps par Famille**
Chaque famille de ligue nécessite un mapping spécifique des handicaps:

```python
HANDICAP_RANGES = {
    "RUSH": [-4.0, -3.0, -2.0, -1.0, 1.0, 2.0, 3.0, 4.0],
    "ENGLAND": [-4.5, -3.5, -2.5, -1.5, 1.5, 2.5, 3.5, 4.5],
    "CLASSIC": [-3.5, -2.5, -1.5, 1.5, 2.5, 3.5, 4.5],
    "CHAMPIONS": [-3.5, -3.0, -2.5, -2.0, -1.5, -1.0, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
    "WORLD": [-2.5, -2.0, -1.5, -1.0, 1.0, 1.5, 2.0, 2.5]
}
```

### 3. **Mapping des Total Goals par Famille**
```python
TOTAL_GOALS_RANGES = {
    "RUSH": [2.5, 3.5, 5.5, 6.5, 7.5, 8.5, 9.5],
    "ENGLAND": [6.5, 7.5, 8.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5],
    "CLASSIC": [5.5, 7.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5],
    "CHAMPIONS": [1.5, 2.5, 3.5, 4.5, 5.5],
    "WORLD": [1.5, 2.5, 3.5, 4.5, 5.5]
}
```

### 4. **Stratégie de Fallback**
Si aucune donnée de marché n'est fournie:
- Utiliser les ranges par défaut de la famille de ligue
- Si la famille est inconnue, utiliser les ranges CLASSIC comme fallback

### 5. **Entraînement Spécifique par Famille**
- Chaque modèle (1X2, BTTS, Total Goals, etc.) doit être entraîné avec des données spécifiques à chaque famille
- Les features doivent inclure le format du match (3x3, 4x4, 5x5, 11v11)
- Les modèles de régression (Total Goals, Handicap) doivent être calibrés sur les plages spécifiques

---

## 📊 Statistiques Clés

| Famille | Matchs | Min TG | Max TG | Min HC | Max HC | Format |
|---------|--------|--------|--------|--------|--------|--------|
| RUSH | 4 | 2.5 | 9.5 | -4.0 | +4.0 | 5x5 |
| ENGLAND | 5 | 6.5 | 16.5 | -4.5 | +4.5 | 4x4 |
| CLASSIC | 4 | 5.5 | 17.5 | -3.5 | +4.5 | 3x3 |
| CHAMPIONS | 5 | 1.5 | 5.5 | -3.5 | +3.5 | 11v11? |
| WORLD | 2 | 1.5 | 5.5 | -2.5 | +2.5 | 11v11? |

---

## 🚀 Actions Recommandées

1. **Mettre à jour `platform_options_mapping.py`** avec les ranges spécifiques par famille
2. **Modifier la logique de prédiction** pour utiliser les ranges dynamiques basés sur les données de marché
3. **Entraîner des modèles séparés** pour chaque format de jeu (3x3, 4x4, 5x5, 11v11)
4. **Ajouter des features de format** dans le pipeline d'entraînement
5. **Valider les prédictions** sur chaque famille de ligue séparément

---

**SIGNÉ:** SOLITAIRE HACK
