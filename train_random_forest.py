"""
train_csv.py — Pipeline d'entraînement multi-familles / multi-tâches
=====================================================================
Familles :
  - PENALTY      : Penalty, FC24. Penalty, FC25. Penalty, FC26. Penalty, FIFA23. Penalty
  - RUSH         : FC 26. 5x5 Rush. Superligue
  - HIGHSCORE    : FC 24. 4x4. Champ. d'Angleterre, FC 25. 3x3. Ligue de conférence
  - CLASSIC      : Tous les championnats classiques + World Cup simulation

Tâches par modèle :
  1. Résultat       → classification 3 classes (dom / nul / ext)  [PENALTY : 2 classes seulement]
  2. Total buts     → régression
  3. Pair / Impair  → classification binaire
  4. Score exact    → Modèle de Poisson (lambda dom + lambda ext)
  5. Nb buts        → identique au total buts (alias)

Usage :
  python train_csv.py --csv finished_matches.csv --out ./models
  python train_csv.py --csv finished_matches.csv --out ./models --eval
"""

import argparse
import os
import json
import warnings
import joblib
import numpy as np
import pandas as pd
from scipy.stats import poisson
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, Ridge, PoissonRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, mean_absolute_error,
                              classification_report, log_loss)
from sklearn.pipeline import Pipeline
from models import PoissonScoreModel
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURATION DES FAMILLES
# ──────────────────────────────────────────────────────────────────────────────

FAMILIES = {
    "PENALTY": {
        "pattern": r"Penalty|penalty",
        "has_draw": False,          # jamais de nul en Penalty
        "typical_goals": (3, 15),   # fourchette normale
        "description": "Séances de tirs au but — 2 issues possibles, scores élevés",
    },
    "HIGHSCORE": {
        "pattern": r"3x3|4x4",
        "has_draw": True,
        "typical_goals": (8, 22),
        "description": "Formats 3x3 / 4x4 — scores très élevés (~15 buts/match)",
    },
    "RUSH": {
        "pattern": r"Rush",
        "has_draw": True,
        "typical_goals": (3, 14),
        "description": "FC 26. 5x5 Rush — profil intermédiaire, grande variance",
    },
    "CLASSIC": {
        "pattern": None,            # tout le reste
        "has_draw": True,
        "typical_goals": (0, 8),
        "description": "Championnats classiques simulés — proche du football réel",
    },
}

# Mapping des ligues live vers ligues entraînées (pour compatibilité)
# Mapping EN (API live 888starz) -> FR (CSV d'entraînement)
# Couvre toutes les 17 ligues présentes dans les données d'entraînement
LEAGUE_MAPPING = {
    # HIGHSCORE (3x3, 4x4)
    "FC 24. 4x4. England Championship": "FC 24. 4x4. Championnat d'Angleterre",
    "FC 25. 3x3. Conference League": "FC 25. 3x3. Ligue de conférence",
    # RUSH (5x5)
    "FC 26. 5x5 Rush. Superleague": "FC 26. 5x5 Rush. Superligue",
    # CLASSIC (championnats classiques)
    "FC 25. Germany Championship": "FC 25. Championnat d'Allemagne",
    "FC 25. England Championship": "FC 25. Championnat d'Angleterre",
    "FC 25. Spain Championship": "FC 25. Championnat d'Espagne",
    "FC 25. Champions League": "FC 25. Champions League",
    "FC 25. Italy Championship": "FC 25. Italy Championship",
    "FC 25. Europa League": "FC 25. Ligue européenne",
    "FC 26. World Championship": "FC 26. Championnat du monde",
    "FC 26. Champions League": "FC 26. Champions League",
    "World Cup 2026. Simulation": "World Cup 2026. Simulation",
    # PENALTY (tirs au but)
    "FC24. Penalty": "FC24. Penalty",
    "FC25. Penalty": "FC25. Penalty",
    "FC26. Penalty": "FC26. Penalty",
    "FIFA23. Penalty": "FIFA23. Penalty",
    "Penalty": "Penalty",
}

def map_league(league: str) -> str:
    """Map une ligue live (EN) vers une ligue entraînée (FR)."""
    return LEAGUE_MAPPING.get(league, league)

# ──────────────────────────────────────────────────────────────────────────────
# 2. CHARGEMENT ET PRÉPARATION DES DONNÉES
# ──────────────────────────────────────────────────────────────────────────────

def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Supprimer les colonnes inutiles
    df = df.drop(columns=['raw_json', 'created_at', 'updated_at', 'source'], errors='ignore')
    # Convertir les dates (supporte ISO8601 avec microsecondes et format JavaScript)
    df["finished_at"] = pd.to_datetime(df["finished_at"], format='ISO8601', utc=True)
    df = df.sort_values("finished_at").reset_index(drop=True)

    # Cibles brutes
    df["total_goals"] = df["score_home"] + df["score_away"]
    df["goals_parity"] = (df["total_goals"] % 2 == 0).astype(int)  # 1=pair, 0=impair
    df["result"] = df.apply(
        lambda r: "H" if r.score_home > r.score_away
        else ("A" if r.score_away > r.score_home else "D"),
        axis=1,
    )
    
    # Détecter si les features sont déjà pré-calculées
    has_advanced_features = "home_w5_played" in df.columns
    
    if has_advanced_features:
        print("  ✅ Features avancées détectées dans le CSV (pas de recalcul nécessaire)")
    else:
        print("  ℹ️  Features avancées non détectées, calcul depuis l'historique...")
    
    df["_has_advanced_features"] = has_advanced_features
    return df


def assign_family(df: pd.DataFrame) -> pd.DataFrame:
    df["family"] = "CLASSIC"
    for fam, cfg in FAMILIES.items():
        if cfg["pattern"] is not None:
            mask = df["league"].str.contains(cfg["pattern"], regex=True, na=False)
            df.loc[mask, "family"] = fam
    return df


# ──────────────────────────────────────────────────────────────────────────────
# 3. FEATURE ENGINEERING — historique glissant par équipe
# ──────────────────────────────────────────────────────────────────────────────

WINDOWS = [5, 10]  # fenêtres glissantes


def compute_team_features(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Pour chaque match, calcule les stats historiques des deux équipes
    AVANT ce match (pas de data leakage).
    
    Returns:
        feat_df: DataFrame avec les features pour chaque match
        team_history: dict {team: DataFrame} avec l'historique complet par équipe
    """
    records = []

    # Index groupé par équipe pour accès rapide
    all_teams = pd.concat([
        df[["finished_at", "team_home", "score_home", "score_away", "result", "family", "league"]].rename(
            columns={"team_home": "team", "score_home": "goals_for", "score_away": "goals_against"}
        ).assign(is_home=1),
        df[["finished_at", "team_away", "score_away", "score_home", "result", "family", "league"]].rename(
            columns={"team_away": "team", "score_away": "goals_for", "score_home": "goals_against"}
        ).assign(is_home=0),
    ], ignore_index=True).sort_values("finished_at")

    # Résultat du point de vue de l'équipe
    all_teams["win"] = all_teams.apply(
        lambda r: 1 if (r.is_home == 1 and r.result == "H") or
                        (r.is_home == 0 and r.result == "A") else 0, axis=1
    )
    all_teams["draw"] = (all_teams["result"] == "D").astype(int)
    all_teams["loss"] = ((all_teams["win"] == 0) & (all_teams["draw"] == 0)).astype(int)

    team_history: dict[str, pd.DataFrame] = {}
    for team, grp in all_teams.groupby("team"):
        team_history[team] = grp.sort_values("finished_at").reset_index(drop=True)

    def get_stats(team: str, before_dt, window: int) -> dict:
        hist = team_history.get(team, pd.DataFrame())
        if hist.empty:
            return _empty_stats(window)
        past = hist[hist["finished_at"] < before_dt].tail(window)
        if len(past) == 0:
            return _empty_stats(window)
        n = len(past)
        return {
            f"w{window}_played":    n,
            f"w{window}_wins":      past["win"].sum(),
            f"w{window}_draws":     past["draw"].sum(),
            f"w{window}_losses":    past["loss"].sum(),
            f"w{window}_gf":        past["goals_for"].mean(),
            f"w{window}_ga":        past["goals_against"].mean(),
            f"w{window}_gd":        (past["goals_for"] - past["goals_against"]).mean(),
            f"w{window}_win_rate":  past["win"].mean(),
            f"w{window}_draw_rate": past["draw"].mean(),
        }

    def _empty_stats(window: int) -> dict:
        keys = ["played", "wins", "draws", "losses", "gf", "ga", "gd", "win_rate", "draw_rate"]
        return {f"w{window}_{k}": 0.0 for k in keys}

    print("  → Calcul des features historiques (peut prendre quelques secondes)...")

    for _, row in df.iterrows():
        feat = {"id": row["id"]}
        for w in WINDOWS:
            h_stats = get_stats(row["team_home"], row["finished_at"], w)
            a_stats = get_stats(row["team_away"], row["finished_at"], w)
            for k, v in h_stats.items():
                feat[f"home_{k}"] = v
            for k, v in a_stats.items():
                feat[f"away_{k}"] = v
            # Features différentielles
            feat[f"diff_w{w}_win_rate"]  = h_stats[f"w{w}_win_rate"]  - a_stats[f"w{w}_win_rate"]
            feat[f"diff_w{w}_gf"]        = h_stats[f"w{w}_gf"]        - a_stats[f"w{w}_gf"]
            feat[f"diff_w{w}_ga"]        = h_stats[f"w{w}_ga"]        - a_stats[f"w{w}_ga"]
            feat[f"diff_w{w}_gd"]        = h_stats[f"w{w}_gd"]        - a_stats[f"w{w}_gd"]
        records.append(feat)

    feat_df = pd.DataFrame(records).set_index("id")
    return feat_df, team_history


def build_features(df: pd.DataFrame, feat_df: pd.DataFrame) -> pd.DataFrame:
    """Assemble toutes les features : historiques + encodages."""
    full = df.set_index("id").join(feat_df)

    # Encodage équipes (fréquence d'apparition → proxy de "niveau")
    home_freq = df["team_home"].value_counts(normalize=True)
    away_freq = df["team_away"].value_counts(normalize=True)
    full["home_team_freq"] = full["team_home"].map(home_freq).fillna(0)
    full["away_team_freq"] = full["team_away"].map(away_freq).fillna(0)

    # Encodage ligue (label encoding)
    le_league = LabelEncoder()
    full["league_enc"] = le_league.fit_transform(full["league"])

    return full.reset_index(), le_league


def get_feature_cols(df: pd.DataFrame) -> list:
    exclude = {
        "id", "match_id", "team_home", "team_away", "league", "family",
        "finished_at", "created_at", "updated_at", "source",
        "score_home", "score_away", "total_goals", "goals_parity", "result",
        "_has_advanced_features",  # Exclure le flag de détection
    }
    return [c for c in df.columns if c not in exclude]


# ──────────────────────────────────────────────────────────────────────────────
# 4. MODÈLE DE POISSON — score exact
# ──────────────────────────────────────────────────────────────────────────────
# La classe PoissonScoreModel est maintenant définie dans models.py pour permettre
# le pickle/unpickle correct avec uvicorn

# ──────────────────────────────────────────────────────────────────────────────
# 5. ENTRAÎNEMENT PAR FAMILLE
# ──────────────────────────────────────────────────────────────────────────────

def train_family(family: str, df_fam: pd.DataFrame, cfg: dict, out_dir: str, evaluate: bool):
    print(f"\n{'='*60}")
    print(f"  FAMILLE : {family} — {len(df_fam)} matchs")
    print(f"  {cfg['description']}")
    print(f"{'='*60}")

    has_draw = cfg["has_draw"]
    n = len(df_fam)

    if n < 50:
        print(f"  ⚠️  Pas assez de données ({n} matchs). Famille ignorée.")
        return

    # Vérifier si les features sont déjà pré-calculées
    has_advanced_features = df_fam["_has_advanced_features"].iloc[0] if "_has_advanced_features" in df_fam.columns else False
    
    if has_advanced_features:
        print("  ⚠️  Features avancées détectées mais ré-entraînement avec features de base pour compatibilité API")
        # Supprimer toutes les colonnes de features pré-calculées pour éviter les conflits
        feature_patterns = [
            "home_w5_", "away_w5_", "diff_w5_", 
            "home_w10_", "away_w10_", "diff_w10_",
            "home_only_w5_", "away_only_w5_", "diff_home_away_only_w5_",
            "home_only_w10_", "away_only_w10_", "diff_home_away_only_w10_",
            "h2h_w5_", "h2h_w10_",
            "home_win_streak", "home_loss_streak", "home_unbeaten_streak",
            "away_win_streak", "away_loss_streak", "away_unbeaten_streak",
            "diff_win_streak", "diff_loss_streak", "diff_unbeaten_streak",
            "league_w20_", "league_w50_", "league_hist_",
            "league_known", "league_goal_profile"
        ]
        cols_to_drop = [c for c in df_fam.columns if any(p in c for p in feature_patterns)]
        df_fam_clean = df_fam.drop(columns=cols_to_drop, errors='ignore')
        
        # Recalculer les features de base
        print("  → Calcul des features historiques (API-compatible)...")
        feat_df, team_history = compute_team_features(df_fam_clean.reset_index(drop=True))
        full, le_league = build_features(df_fam_clean.reset_index(drop=True), feat_df)
        full = full.fillna(0)
    else:
        print("  → Calcul des features historiques...")
        # Calculer les features comme avant
        feat_df, team_history = compute_team_features(df_fam.reset_index(drop=True))
        full, le_league = build_features(df_fam.reset_index(drop=True), feat_df)
        full = full.fillna(0)

    feature_cols = get_feature_cols(full)
    X = full[feature_cols].values

    # Cibles
    y_result   = full["result"].values          # H / D / A
    y_goals    = full["total_goals"].values
    y_parity   = full["goals_parity"].values
    y_score_h  = full["score_home"].values
    y_score_a  = full["score_away"].values

    # Pour PENALTY : supprimer les nuls (ne devraient pas exister)
    if not has_draw:
        mask = full["result"] != "D"
        X         = X[mask]
        y_result  = y_result[mask]
        y_goals   = y_goals[mask]
        y_parity  = y_parity[mask]
        y_score_h = y_score_h[mask]
        y_score_a = y_score_a[mask]
        print(f"  (Penalty : {mask.sum()} matchs sans nul conservés)")

    # Encodage résultat
    le_result = LabelEncoder()
    y_result_enc = le_result.fit_transform(y_result)

    # Split train/test
    test_size = 0.2 if n >= 200 else 0.15
    idx = np.arange(len(X))
    # Respect de l'ordre temporel
    split = int(len(idx) * (1 - test_size))
    tr, te = idx[:split], idx[split:]

    X_tr, X_te = X[tr], X[te]
    yr_tr, yr_te = y_result_enc[tr], y_result_enc[te]
    yg_tr, yg_te = y_goals[tr], y_goals[te]
    yp_tr, yp_te = y_parity[tr], y_parity[te]
    ysh_tr = y_score_h[tr]
    ysa_tr = y_score_a[tr]

    models = {}

    # ── 5.1 Résultat (1/N/2) ────────────────────────────────────────────────
    print("  [1/4] Entraînement résultat...")
    n_classes = len(np.unique(yr_tr))
    if n_classes >= 2:
        if n >= 500:
            clf_result = Pipeline([
                ("scaler", StandardScaler()),
                ("clf", GradientBoostingClassifier(
                    n_estimators=200, max_depth=4, learning_rate=0.05,
                    subsample=0.8, random_state=42
                ))
            ])
        else:
            clf_result = Pipeline([
                ("scaler", StandardScaler()),
                ("clf", RandomForestClassifier(
                    n_estimators=200, max_depth=6, random_state=42
                ))
            ])
        clf_result.fit(X_tr, yr_tr)
        models["result"] = clf_result

        if evaluate and len(te) > 0:
            preds = clf_result.predict(X_te)
            acc = accuracy_score(yr_te, preds)
            print(f"    Accuracy résultat : {acc:.3f}")
            print(classification_report(yr_te, preds,
                  target_names=le_result.classes_, zero_division=0))

    # ── 5.2 Total buts (régression) ─────────────────────────────────────────
    print("  [2/4] Entraînement total buts...")
    if n >= 500:
        reg_goals = Pipeline([
            ("scaler", StandardScaler()),
            ("reg", GradientBoostingRegressor(
                n_estimators=200, max_depth=4, learning_rate=0.05,
                subsample=0.8, random_state=42
            ))
        ])
    else:
        reg_goals = Pipeline([
            ("scaler", StandardScaler()),
            ("reg", Ridge(alpha=1.0))
        ])
    reg_goals.fit(X_tr, yg_tr)
    models["total_goals"] = reg_goals

    if evaluate and len(te) > 0:
        preds_g = reg_goals.predict(X_te)
        mae = mean_absolute_error(yg_te, preds_g)
        print(f"    MAE total buts : {mae:.3f}")

    # ── 5.3 Pair / Impair ───────────────────────────────────────────────────
    print("  [3/4] Entraînement pair/impair...")
    clf_parity = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=500, C=1.0, random_state=42))
    ])
    clf_parity.fit(X_tr, yp_tr)
    models["parity"] = clf_parity

    if evaluate and len(te) > 0:
        preds_p = clf_parity.predict(X_te)
        acc_p = accuracy_score(yp_te, preds_p)
        print(f"    Accuracy pair/impair : {acc_p:.3f}")

    # ── 5.4 Score exact — Modèle de Poisson ─────────────────────────────────
    print("  [4/4] Entraînement score exact (Poisson)...")
    max_goals_poisson = int(cfg["typical_goals"][1]) + 2
    poisson_model = PoissonScoreModel()
    poisson_model.fit(X_tr, ysh_tr, ysa_tr, feature_cols)
    models["poisson"] = poisson_model

    if evaluate and len(te) > 0:
        exact_preds = poisson_model.predict_exact_score(X_te, max_goals=max_goals_poisson)
        exact_actual = list(zip(y_score_h[te], y_score_a[te]))
        exact_acc = sum(p == a for p, a in zip(exact_preds, exact_actual)) / len(exact_actual)
        total_mae = mean_absolute_error(y_goals[te], poisson_model.predict_total_goals(X_te))
        print(f"    Accuracy score exact : {exact_acc:.3f}")
        print(f"    MAE total buts (Poisson) : {total_mae:.3f}")

    # ── Sauvegarde ───────────────────────────────────────────────────────────
    family_dir = os.path.join(out_dir, family)
    os.makedirs(family_dir, exist_ok=True)

    for name, model in models.items():
        path = os.path.join(family_dir, f"{name}.pkl")
        joblib.dump(model, path)

    # Sauvegarder team_history pour l'API (format optimisé)
    team_history_serializable = {k: v.to_dict("records") for k, v in team_history.items()}
    joblib.dump(team_history_serializable, os.path.join(family_dir, "team_history.pkl"))

    # Métadonnées
    meta = {
        "family":        family,
        "description":   cfg["description"],
        "has_draw":      bool(has_draw),
        "n_train":       int(len(tr)),
        "n_test":        int(len(te)),
        "feature_cols":  feature_cols,
        "result_classes": list(le_result.classes_),
        "typical_goals": cfg["typical_goals"],
        "max_goals_poisson": max_goals_poisson,
        "leagues":       list(df_fam["league"].unique()),
        "has_advanced_features": bool(has_advanced_features),
    }
    joblib.dump(le_result, os.path.join(family_dir, "le_result.pkl"))
    
    # Sauvegarder le_league seulement s'il a été créé (pas déjà encodé)
    if le_league is not None:
        joblib.dump(le_league, os.path.join(family_dir, "le_league.pkl"))
    elif "league_enc" in full.columns:
        # Créer un LabelEncoder factice pour compatibilité
        le_league_dummy = LabelEncoder()
        le_league_dummy.fit(full["league_enc"].unique())
        joblib.dump(le_league_dummy, os.path.join(family_dir, "le_league.pkl"))
    with open(os.path.join(family_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"\n  ✅ Modèles sauvegardés dans : {family_dir}/")
    print(f"     Fichiers : {', '.join(models.keys())}.pkl + meta.json")
    return meta


# ──────────────────────────────────────────────────────────────────────────────
# 6. VALIDATION DE COHÉRENCE GLOBALE
# ──────────────────────────────────────────────────────────────────────────────

def apply_global_coherence(output: dict, meta: dict) -> dict:
    """
    Applique des validations de cohérence globales pour éviter les contradictions
    entre les différentes prédictions.
    
    Règles appliquées:
    1. Cohérence entre seuils over/under (monotonie)
    2. Cohérence entre handicaps (monotonie)
    3. Cohérence score exact ↔ total_goals
    4. Cohérence score exact ↔ 1x2
    5. Cohérence score exact ↔ parity
    """
    preds = output["predictions"]
    
    # Règle 1: Cohérence entre seuils over/under (monotonie)
    # Si over est favori pour un seuil, il doit l'être pour tous les seuils inférieurs
    over_under = preds["total_goals"]["over_under"]
    sorted_thresholds = sorted([float(k) for k in over_under.keys()])
    
    # Trouver le point de basculement
    predicted_total = preds["total_goals"]["predicted"]
    for i, threshold in enumerate(sorted_thresholds):
        if i > 0:
            prev_threshold = sorted_thresholds[i - 1]
            # Utiliser la clé originale pour accéder aux valeurs
            prev_key = str(prev_threshold)
            curr_key = str(threshold)
            
            if prev_key not in over_under or curr_key not in over_under:
                continue
                
            prev_over = over_under[prev_key]["over"]
            curr_over = over_under[curr_key]["over"]
            
            # Si le seuil précédent favorisait over, le seuil actuel doit aussi favoriser over
            # (ou au moins ne pas favoriser under plus fortement)
            if prev_over > 0.5 and curr_over < 0.5:
                # Corriger: forcer over à être >= 0.5
                over_under[curr_key]["over"] = max(0.5, curr_over)
                over_under[curr_key]["under"] = 1 - over_under[curr_key]["over"]
    
    # Règle 2: Cohérence entre handicaps (monotonie)
    # Si home est favori pour +1, il doit être encore plus favori pour +2
    handicap = preds["handicap"]
    sorted_handicaps = sorted([float(k) for k in handicap.keys()])
    
    # Pour les handicaps positifs: home doit être de plus en plus favori
    positive_handicaps = [h for h in sorted_handicaps if h > 0]
    for i in range(1, len(positive_handicaps)):
        prev_h = positive_handicaps[i - 1]
        curr_h = positive_handicaps[i]
        prev_key = str(prev_h)
        curr_key = str(curr_h)
        
        if prev_key not in handicap or curr_key not in handicap:
            continue
            
        prev_home = handicap[prev_key]["home"]
        curr_home = handicap[curr_key]["home"]
        
        # Si home était favori pour le handicap précédent, il doit l'être encore plus pour le suivant
        if prev_home > 0.5 and curr_home < prev_home:
            # Corriger: forcer home à être >= prev_home
            handicap[curr_key]["home"] = max(prev_home, curr_home)
            # Répartir draw et away proportionnellement
            remaining = 1 - handicap[curr_key]["home"]
            handicap[curr_key]["draw"] = remaining * 0.3
            handicap[curr_key]["away"] = remaining * 0.7
    
    # Pour les handicaps négatifs: away doit être de plus en plus favori
    negative_handicaps = [h for h in sorted_handicaps if h < 0]
    negative_handicaps.sort(reverse=True)  # Du plus proche de 0 au plus négatif
    for i in range(1, len(negative_handicaps)):
        prev_h = negative_handicaps[i - 1]
        curr_h = negative_handicaps[i]
        prev_key = str(prev_h)
        curr_key = str(curr_h)
        
        if prev_key not in handicap or curr_key not in handicap:
            continue
            
        prev_away = handicap[prev_key]["away"]
        curr_away = handicap[curr_key]["away"]
        
        # Si away était favori pour le handicap précédent, il doit l'être encore plus pour le suivant
        if prev_away > 0.5 and curr_away < prev_away:
            # Corriger: forcer away à être >= prev_away
            handicap[curr_key]["away"] = max(prev_away, curr_away)
            # Répartir home et draw proportionnellement
            remaining = 1 - handicap[curr_key]["away"]
            handicap[curr_key]["home"] = remaining * 0.7
            handicap[curr_key]["draw"] = remaining * 0.3
    
    # Règle 3: Cohérence score exact ↔ total_goals
    exact_score_str = preds["exact_score"]["prediction"]
    exact_home, exact_away = map(int, exact_score_str.split("-"))
    exact_total = exact_home + exact_away
    predicted_total = preds["total_goals"]["predicted"]
    
    # Si l'écart est trop grand (> 2 buts), ajuster le score exact
    if abs(exact_total - predicted_total) > 2:
        # Recalculer le score exact le plus proche du total prédit
        # En utilisant la distribution de Poisson
        from scipy.stats import poisson as poisson_dist
        lambda_total = predicted_total
        best_score = (0, 0)
        best_prob = 0
        for h in range(int(lambda_total) - 2, int(lambda_total) + 3):
            for a in range(int(lambda_total) - 2, int(lambda_total) + 3):
                if h >= 0 and a >= 0:
                    # Probabilité simplifiée
                    prob = poisson_dist.pmf(h, lambda_total / 2) * poisson_dist.pmf(a, lambda_total / 2)
                    if prob > best_prob:
                        best_prob = prob
                        best_score = (h, a)
        preds["exact_score"]["prediction"] = f"{best_score[0]}-{best_score[1]}"
    
    # NOTE: Les règles 4 et 5 (cohérence score exact ↔ 1x2 et score exact ↔ parity) 
    # ont été retirées car maintenant le 1X2 et la parité sont dérivés du score exact,
    # et non l'inverse. Cela garantit une cohérence parfaite.
    
    return output


# ──────────────────────────────────────────────────────────────────────────────
# 7. MODEL LOADER (API - chargement unique au démarrage)
# ──────────────────────────────────────────────────────────────────────────────

class ModelLoader:
    """
    Charge tous les modèles une seule fois au démarrage de l'API.
    Évite de recharger les modèles à chaque requête.
    """
    
    def __init__(self, models_dir: str, csv_path: str = None):
        self.models_dir = models_dir
        self.loaded = False
        self.models = {}
        self.csv_data = None
        self.csv_path = csv_path
    
    def load_all(self):
        """Charge tous les modèles de toutes les familles."""
        if self.loaded:
            return
        
        print("Chargement des modèles...")
        
        for family in FAMILIES.keys():
            family_dir = os.path.join(self.models_dir, family)
            if not os.path.exists(family_dir):
                print(f"  ⚠️  Famille {family} : modèles non trouvés, ignorée.")
                continue
            
            try:
                with open(os.path.join(family_dir, "meta.json"), encoding="utf-8") as f:
                    meta = json.load(f)
                
                self.models[family] = {
                    "meta": meta,
                    "le_result": joblib.load(os.path.join(family_dir, "le_result.pkl")),
                    "clf_result": joblib.load(os.path.join(family_dir, "result.pkl")),
                    "reg_goals": joblib.load(os.path.join(family_dir, "total_goals.pkl")),
                    "clf_parity": joblib.load(os.path.join(family_dir, "parity.pkl")),
                    "poisson_mdl": joblib.load(os.path.join(family_dir, "poisson.pkl")),
                    "le_league": joblib.load(os.path.join(family_dir, "le_league.pkl")),
                    "team_history": {k: pd.DataFrame(v) for k, v in 
                                    joblib.load(os.path.join(family_dir, "team_history.pkl")).items()},
                }
                print(f"  ✅ {family} chargée")
            except Exception as e:
                print(f"  ❌ Erreur chargement {family}: {e}")
        
        # Charger le CSV pour l'historique des matchs
        if self.csv_path and os.path.exists(self.csv_path):
            try:
                self.csv_data = pd.read_csv(self.csv_path)
                self.csv_data["finished_at"] = pd.to_datetime(self.csv_data["finished_at"], utc=True, format='ISO8601')
                print(f"✅ Données CSV chargées: {len(self.csv_data)} matchs")
            except Exception as e:
                print(f"⚠️  Erreur chargement CSV: {e}")
        
        self.loaded = True
        print(f"\n✅ {len(self.models)} familles chargées")
    
    def get_team_last_matches(self, team: str, league: str, limit: int = 5) -> dict:
        """
        Récupère les derniers matchs d'une équipe dans une ligue spécifique avec statistiques.
        
        Args:
            team: Nom de l'équipe
            league: Nom de la ligue
            limit: Nombre de matchs à retourner (défaut: 5)
            
        Returns:
            Dictionnaire avec les matchs et les statistiques
        """
        if self.csv_data is None:
            return {"matches": [], "stats": {}}
        
        # Filtrer les matchs où l'équipe a joué (domicile ou extérieur)
        team_matches = self.csv_data[
            ((self.csv_data["team_home"] == team) | (self.csv_data["team_away"] == team)) &
            (self.csv_data["league"] == league)
        ].sort_values("finished_at", ascending=False).head(limit)
        
        # Convertir en liste de dictionnaires
        matches = []
        goals_for = []
        goals_against = []
        results = []
        
        for _, row in team_matches.iterrows():
            is_home = row["team_home"] == team
            team_score = int(row["score_home"]) if is_home else int(row["score_away"])
            opponent_score = int(row["score_away"]) if is_home else int(row["score_home"])
            if (is_home and row["score_home"] > row["score_away"]) or (not is_home and row["score_away"] > row["score_home"]):
                result = "W"
            elif row["score_home"] == row["score_away"]:
                result = "D"
            else:
                result = "L"
            
            matches.append({
                "date": row["finished_at"].strftime("%Y-%m-%d %H:%M:%S"),
                "opponent": row["team_away"] if is_home else row["team_home"],
                "is_home": is_home,
                "score_home": int(row["score_home"]),
                "score_away": int(row["score_away"]),
                "team_score": team_score,
                "opponent_score": opponent_score,
                "result": result
            })
            
            goals_for.append(team_score)
            goals_against.append(opponent_score)
            results.append(result)
        
        # Calculer les statistiques
        stats = {}
        if matches:
            wins = results.count("W")
            draws = results.count("D")
            losses = results.count("L")
            
            stats = {
                "avg_goals_for": round(sum(goals_for) / len(matches), 2),
                "avg_goals_against": round(sum(goals_against) / len(matches), 2),
                "avg_goal_difference": round((sum(goals_for) - sum(goals_against)) / len(matches), 2),
                "form": f"{wins}W-{draws}D-{losses}L",
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "total_matches": len(matches)
            }
            
            # Performance domicile/extérieur
            home_matches = [m for m in matches if m["is_home"]]
            away_matches = [m for m in matches if not m["is_home"]]
            
            if home_matches:
                home_wins = sum(1 for m in home_matches if m["result"] == "W")
                home_draws = sum(1 for m in home_matches if m["result"] == "D")
                home_losses = len(home_matches) - home_wins - home_draws
                stats["home_performance"] = f"{home_wins}W-{home_draws}D-{home_losses}L"
            
            if away_matches:
                away_wins = sum(1 for m in away_matches if m["result"] == "W")
                away_draws = sum(1 for m in away_matches if m["result"] == "D")
                away_losses = len(away_matches) - away_wins - away_draws
                stats["away_performance"] = f"{away_wins}W-{away_draws}D-{away_losses}L"
        
        return {"matches": matches, "stats": stats}
    
    def get_head_to_head(self, team_home: str, team_away: str, league: str, limit: int = 5) -> list:
        """
        Récupère les confrontations directes entre deux équipes dans une ligue spécifique.
        
        Args:
            team_home: Équipe domicile
            team_away: Équipe extérieur
            league: Nom de la ligue
            limit: Nombre de matchs à retourner (défaut: 5)
            
        Returns:
            Liste des confrontations directes (dictionnaires)
        """
        if self.csv_data is None:
            return []
        
        # Filtrer les matchs où les deux équipes se sont affrontées dans cette ligue
        h2h_matches = self.csv_data[
            (((self.csv_data["team_home"] == team_home) & (self.csv_data["team_away"] == team_away)) |
             ((self.csv_data["team_home"] == team_away) & (self.csv_data["team_away"] == team_home))) &
            (self.csv_data["league"] == league)
        ].sort_values("finished_at", ascending=False).head(limit)
        
        # Convertir en liste de dictionnaires
        matches = []
        for _, row in h2h_matches.iterrows():
            is_home_home = row["team_home"] == team_home
            matches.append({
                "date": row["finished_at"].strftime("%Y-%m-%d %H:%M:%S"),
                "home_team": row["team_home"],
                "away_team": row["team_away"],
                "score_home": int(row["score_home"]),
                "score_away": int(row["score_away"]),
                "winner": "H" if row["score_home"] > row["score_away"] else 
                          "A" if row["score_away"] > row["score_home"] else "D"
            })
        
        return matches
    
    def predict(self, team_home: str, team_away: str, league: str) -> dict:
        """
        Prédiction rapide avec modèles déjà chargés en mémoire.
        """
        if not self.loaded:
            self.load_all()
        
        # Déterminer la famille
        family = "CLASSIC"
        for fam, cfg in FAMILIES.items():
            if cfg["pattern"] and pd.Series([league]).str.contains(cfg["pattern"], regex=True)[0]:
                family = fam
                break
        
        if family not in self.models:
            raise ValueError(f"Modèles non chargés pour la famille {family}")
        
        mdl = self.models[family]
        meta = mdl["meta"]
        team_history = mdl["team_history"]
        
        # Calculer features pour ce match uniquement
        match_time = pd.Timestamp.now(tz="UTC")
        feat = compute_single_match_features(team_home, team_away, match_time, team_history)
        
        # Ajouter features de fréquence équipe (approximation)
        total_matches = sum(len(v) for v in team_history.values())
        home_matches = len(team_history.get(team_home, []))
        away_matches = len(team_history.get(team_away, []))
        feat["home_team_freq"] = home_matches / total_matches if total_matches > 0 else 0
        feat["away_team_freq"] = away_matches / total_matches if total_matches > 0 else 0
        
        # Encodage ligue avec mapping pour les noms anglais
        mapped_league = map_league(league)
        
        # Si la ligue mappée n'est pas connue, utiliser une valeur par défaut
        try:
            feat["league_enc"] = mdl["le_league"].transform([mapped_league])[0]
        except ValueError:
            # Ligue inconnue, utiliser la première classe comme fallback
            feat["league_enc"] = 0
        
        # Construire X
        feature_cols = meta["feature_cols"]
        X = np.array([feat.get(col, 0) for col in feature_cols]).reshape(1, -1)
        
        # Prédictions
        result_proba = mdl["clf_result"].predict_proba(X)[0]
        result_classes = mdl["le_result"].classes_
        result_pred = mdl["le_result"].inverse_transform([mdl["clf_result"].predict(X)[0]])[0]
        
        total_goals_pred = float(mdl["reg_goals"].predict(X)[0])
        parity_pred = "pair" if mdl["clf_parity"].predict(X)[0] == 1 else "impair"
        parity_proba = mdl["clf_parity"].predict_proba(X)[0]
        
        max_g = meta["max_goals_poisson"]
        exact_score = mdl["poisson_mdl"].predict_exact_score(X, max_goals=max_g)[0]
        lh, la = mdl["poisson_mdl"].predict_lambdas(X)
        
        # Calculer les probabilités Over/Under pour différents seuils
        # Utiliser la distribution de Poisson pour calculer P(total > threshold)
        # Sélectionner intelligemment les seuils en fonction du total prédit
        from scipy.stats import poisson as poisson_dist
        
        # Lambda total = lambda_home + lambda_away
        lambda_total = float(lh[0]) + float(la[0])
        
        # Sélectionner les seuils pertinents en fonction du total prédit
        predicted_total = total_goals_pred
        thresholds = []
        
        # Ajouter des seuils autour du total prédit
        base_threshold = round(predicted_total / 0.5) * 0.5  # Arrondir au 0.5 le plus proche
        
        # Ajouter 3 seuils en dessous et 3 seuils au-dessus du total prédit
        for i in range(-3, 4):
            threshold = base_threshold + (i * 0.5)
            if threshold >= 0.5:  # Minimum 0.5 buts
                thresholds.append(threshold)
        
        # S'assurer qu'on a au moins quelques seuils standards
        if not thresholds:
            thresholds = [2.5, 3.5, 4.5, 5.5, 6.5]
        
        # Limiter à 7 seuils maximum pour éviter trop d'options
        thresholds = sorted(set(thresholds))[:7]
        
        over_under_probs = {}
        for threshold in thresholds:
            # P(total > threshold) = 1 - P(total <= threshold)
            prob_under = sum(poisson_dist.pmf(k, lambda_total) for k in range(int(threshold) + 1))
            prob_over = 1 - prob_under
            
            # Ajuster pour cohérence avec le total prédit
            # Si le total prédit est supérieur au seuil, over devrait être plus probable
            if predicted_total > threshold:
                # Forcer over à être > under
                diff = predicted_total - threshold
                adjustment = min(0.4, diff * 0.1)  # Ajustement plus fort
                prob_over = min(0.95, prob_over + adjustment)
                prob_under = 1 - prob_over
                # S'assurer que over > under
                if prob_over <= prob_under:
                    prob_over = 0.6
                    prob_under = 0.4
            elif predicted_total < threshold:
                # Forcer under à être > over
                diff = threshold - predicted_total
                adjustment = min(0.4, diff * 0.1)  # Ajustement plus fort
                prob_over = max(0.05, prob_over - adjustment)
                prob_under = 1 - prob_over
                # S'assurer que under > over
                if prob_under <= prob_over:
                    prob_over = 0.4
                    prob_under = 0.6
            
            over_under_probs[str(threshold)] = {
                "over": round(float(prob_over), 3),
                "under": round(float(prob_under), 3)
            }
        
        # Calculer les probabilités de handicap
        # Sélectionner intelligemment les handicaps en fonction de la différence de buts prédite
        # ET assurer la cohérence avec le 1x2
        handicap_probs = {}
        
        # Calculer la distribution de probabilité pour chaque score possible
        score_probs = {}
        for h in range(max_g + 1):
            for a in range(max_g + 1):
                prob_home = poisson_dist.pmf(h, float(lh[0]))
                prob_away = poisson_dist.pmf(a, float(la[0]))
                score_probs[(h, a)] = prob_home * prob_away
        
        # Normaliser les probabilités
        total_prob = sum(score_probs.values())
        score_probs = {k: v / total_prob for k, v in score_probs.items()}
        
        # Calculer la différence de buts prédite (lambda_home - lambda_away)
        predicted_diff = float(lh[0]) - float(la[0])
        
        # Sélectionner les handicaps pertinents en fonction de la différence prédite
        handicaps = []
        base_handicap = round(predicted_diff)  # Arrondir à l'entier le plus proche
        
        # Ajouter des handicaps autour de la différence prédite
        for i in range(-2, 3):
            handicap = base_handicap + i
            if handicap != 0:  # Exclure handicap 0 (nul)
                handicaps.append(handicap)
        
        # S'assurer qu'on a au moins quelques handicaps standards
        if not handicaps:
            handicaps = [-1.0, 1.0]
        
        # Limiter à 5 handicaps maximum
        handicaps = sorted(set(handicaps))[:5]
        
        for handicap in handicaps:
            # Handicap pour home: P(home_score + handicap > away_score)
            prob_handicap_home = sum(p for (h, a), p in score_probs.items() if h + handicap > a)
            prob_handicap_draw = sum(p for (h, a), p in score_probs.items() if h + handicap == a)
            prob_handicap_away = 1 - prob_handicap_home - prob_handicap_draw
            
            # Ajuster pour cohérence avec 1x2
            # Si home est favori dans 1x2, les handicaps positifs pour home devraient être plus probables
            home_1x2_prob = result_proba[result_classes.tolist().index("H")] if "H" in result_classes else 0.5
            away_1x2_prob = result_proba[result_classes.tolist().index("A")] if "A" in result_classes else 0.5
            
            # Ajustement progressif basé sur le handicap
            if handicap > 0 and home_1x2_prob > 0.5:
                # Handicap positif pour home quand home est favori: forcer home à être favori
                adjustment_factor = 0.2 * min(handicap, 3)  # Ajustement plus fort (max 60%)
                prob_handicap_home = min(0.95, prob_handicap_home + adjustment_factor)
                # S'assurer que away reste positif
                prob_handicap_away = max(0.01, 1 - prob_handicap_home - prob_handicap_draw)
                # Réajuster home si nécessaire pour que la somme = 1
                if prob_handicap_home + prob_handicap_draw + prob_handicap_away > 1:
                    prob_handicap_home = 1 - prob_handicap_draw - prob_handicap_away
                # Forcer home à être le favori
                if prob_handicap_home <= max(prob_handicap_draw, prob_handicap_away):
                    prob_handicap_home = 0.6
                    prob_handicap_draw = 0.2
                    prob_handicap_away = 0.2
            elif handicap < 0 and home_1x2_prob > 0.5:
                # Handicap négatif pour home quand home est favori: forcer away à être favori
                adjustment_factor = 0.2 * min(abs(handicap), 3)
                prob_handicap_home = max(0.05, prob_handicap_home - adjustment_factor)
                prob_handicap_away = 1 - prob_handicap_home - prob_handicap_draw
                # Forcer away à être le favori
                if prob_handicap_away <= max(prob_handicap_home, prob_handicap_draw):
                    prob_handicap_home = 0.2
                    prob_handicap_draw = 0.2
                    prob_handicap_away = 0.6
            elif handicap > 0 and away_1x2_prob > 0.5:
                # Handicap positif pour home quand away est favori: forcer away à être favori
                adjustment_factor = 0.2 * min(handicap, 3)
                prob_handicap_home = max(0.05, prob_handicap_home - adjustment_factor)
                prob_handicap_away = 1 - prob_handicap_home - prob_handicap_draw
                # Forcer away à être le favori
                if prob_handicap_away <= max(prob_handicap_home, prob_handicap_draw):
                    prob_handicap_home = 0.2
                    prob_handicap_draw = 0.2
                    prob_handicap_away = 0.6
            elif handicap < 0 and away_1x2_prob > 0.5:
                # Handicap négatif pour home quand away est favori: forcer home à être favori
                adjustment_factor = 0.2 * min(abs(handicap), 3)
                prob_handicap_home = min(0.95, prob_handicap_home + adjustment_factor)
                # S'assurer que away reste positif
                prob_handicap_away = max(0.01, 1 - prob_handicap_home - prob_handicap_draw)
                # Réajuster home si nécessaire pour que la somme = 1
                if prob_handicap_home + prob_handicap_draw + prob_handicap_away > 1:
                    prob_handicap_home = 1 - prob_handicap_draw - prob_handicap_away
                # Forcer home à être le favori
                if prob_handicap_home <= max(prob_handicap_draw, prob_handicap_away):
                    prob_handicap_home = 0.6
                    prob_handicap_draw = 0.2
                    prob_handicap_away = 0.2
            
            handicap_probs[str(handicap)] = {
                "home": round(float(prob_handicap_home), 3),
                "draw": round(float(prob_handicap_draw), 3),
                "away": round(float(prob_handicap_away), 3)
            }
        
        # Assembler les prédictions brutes
        output = {
            "match": f"{team_home} vs {team_away}",
            "league": league,
            "family": family,
            "predictions": {
                "1x2": {
                    "home": round(float(result_proba[result_classes.tolist().index("H")]), 3) if "H" in result_classes else 0.0,
                    "draw": round(float(result_proba[result_classes.tolist().index("D")]), 3) if "D" in result_classes else 0.0,
                    "away": round(float(result_proba[result_classes.tolist().index("A")]), 3) if "A" in result_classes else 0.0,
                },
                "total_goals": {
                    "predicted": round(total_goals_pred, 1),
                    "over_under": over_under_probs
                },
                "handicap": handicap_probs,
                "parity": {
                    "pair": round(float(parity_proba[1]), 3),
                    "impair": round(float(parity_proba[0]), 3)
                },
                "exact_score": {
                    "prediction": f"{exact_score[0]}-{exact_score[1]}",
                }
            }
        }
        
        # Dériver le 1X2 et la parité du score exact pour garantir la cohérence
        exact_score_str = output["predictions"]["exact_score"]["prediction"]
        exact_home, exact_away = map(int, exact_score_str.split("-"))
        
        # Dériver le 1X2 du score exact
        if exact_home > exact_away:
            derived_1x2 = "1"
        elif exact_home == exact_away:
            derived_1x2 = "X"
        else:
            derived_1x2 = "2"
        
        # Dériver la parité du score exact
        exact_total = exact_home + exact_away
        derived_parity = "pair" if exact_total % 2 == 0 else "impair"
        
        # Ajuster les probabilités 1X2 pour refléter le résultat dérivé
        if derived_1x2 == "1":
            output["predictions"]["1x2"]["home"] = max(output["predictions"]["1x2"]["home"], 0.6)
            output["predictions"]["1x2"]["draw"] = min(output["predictions"]["1x2"]["draw"], 0.2)
            output["predictions"]["1x2"]["away"] = min(output["predictions"]["1x2"]["away"], 0.2)
        elif derived_1x2 == "X":
            output["predictions"]["1x2"]["draw"] = max(output["predictions"]["1x2"]["draw"], 0.5)
            output["predictions"]["1x2"]["home"] = min(output["predictions"]["1x2"]["home"], 0.3)
            output["predictions"]["1x2"]["away"] = min(output["predictions"]["1x2"]["away"], 0.3)
        else:  # derived_1x2 == "2"
            output["predictions"]["1x2"]["away"] = max(output["predictions"]["1x2"]["away"], 0.6)
            output["predictions"]["1x2"]["draw"] = min(output["predictions"]["1x2"]["draw"], 0.2)
            output["predictions"]["1x2"]["home"] = min(output["predictions"]["1x2"]["home"], 0.2)
        
        # Ajuster les probabilités de parité pour refléter la parité dérivée
        if derived_parity == "pair":
            output["predictions"]["parity"]["pair"] = max(output["predictions"]["parity"]["pair"], 0.6)
            output["predictions"]["parity"]["impair"] = min(output["predictions"]["parity"]["impair"], 0.4)
        else:
            output["predictions"]["parity"]["impair"] = max(output["predictions"]["parity"]["impair"], 0.6)
            output["predictions"]["parity"]["pair"] = min(output["predictions"]["parity"]["pair"], 0.4)
        
        # Appliquer les validations de cohérence globales restantes
        output = apply_global_coherence(output, meta)
        
        # Ajouter les données historiques si disponibles
        if self.csv_data is not None:
            # Récupérer les 5 derniers matchs de chaque équipe avec statistiques
            home_data = self.get_team_last_matches(team_home, league, limit=5)
            away_data = self.get_team_last_matches(team_away, league, limit=5)
            
            # Récupérer les confrontations directes
            head_to_head = self.get_head_to_head(team_home, team_away, league, limit=5)
            
            # Construire la réponse avec statistiques
            history_data = {
                "home_last_matches": home_data["matches"],
                "home_stats": home_data["stats"],
                "away_last_matches": away_data["matches"],
                "away_stats": away_data["stats"]
            }
            
            # N'ajouter la section head_to_head que s'il y a des matchs en commun
            if head_to_head:
                history_data["head_to_head"] = head_to_head
            
            output["history"] = history_data
        
        return output
    
    def update_history(self, match_data: dict):
        """
        Met à jour l'historique avec un match terminé.
        
        Args:
            match_data: dict avec clés:
                - team_home, team_away, league
                - score_home, score_away
                - finished_at (ISO8601)
                - family (optionnel, auto-détecté sinon)
        """
        if not self.loaded:
            self.load_all()
        
        # Déterminer la famille
        league = match_data["league"]
        family = match_data.get("family")
        if family is None:
            family = "CLASSIC"
            for fam, cfg in FAMILIES.items():
                if cfg["pattern"] and pd.Series([league]).str.contains(cfg["pattern"], regex=True)[0]:
                    family = fam
                    break
        
        if family not in self.models:
            print(f"⚠️  Famille {family} non chargée, mise à jour ignorée")
            return
        
        mdl = self.models[family]
        team_history = mdl["team_history"]
        
        # Calculer le résultat
        score_home = match_data["score_home"]
        score_away = match_data["score_away"]
        result = "H" if score_home > score_away else ("A" if score_away > score_home else "D")
        
        finished_at = pd.to_datetime(match_data["finished_at"], utc=True)
        
        # Ajouter l'entrée pour l'équipe domicile
        home_entry = {
            "finished_at": finished_at,
            "goals_for": score_home,
            "goals_against": score_away,
            "result": result,
            "win": 1 if result == "H" else 0,
            "draw": 1 if result == "D" else 0,
            "loss": 1 if result == "A" else 0,
            "is_home": 1,
            "family": family,
            "league": league,
        }
        
        # Ajouter l'entrée pour l'équipe extérieur
        away_entry = {
            "finished_at": finished_at,
            "goals_for": score_away,
            "goals_against": score_home,
            "result": result,
            "win": 1 if result == "A" else 0,
            "draw": 1 if result == "D" else 0,
            "loss": 1 if result == "H" else 0,
            "is_home": 0,
            "family": family,
            "league": league,
        }
        
        # Mettre à jour l'historique
        team_home_name = match_data["team_home"]
        team_away_name = match_data["team_away"]
        
        if team_home_name not in team_history:
            team_history[team_home_name] = pd.DataFrame()
        team_history[team_home_name] = pd.concat([
            team_history[team_home_name], 
            pd.DataFrame([home_entry])
        ], ignore_index=True).sort_values("finished_at").reset_index(drop=True)
        
        if team_away_name not in team_history:
            team_history[team_away_name] = pd.DataFrame()
        team_history[team_away_name] = pd.concat([
            team_history[team_away_name], 
            pd.DataFrame([away_entry])
        ], ignore_index=True).sort_values("finished_at").reset_index(drop=True)
        
        print(f"✅ Historique mis à jour: {team_home_name} vs {team_away_name}")
    
    def save_history(self, family: str = None):
        """
        Sauvegarde l'historique mis à jour sur disque.
        
        Args:
            family: si None, sauvegarde toutes les familles
        """
        if not self.loaded:
            self.load_all()
        
        families_to_save = [family] if family else self.models.keys()
        
        for fam in families_to_save:
            if fam not in self.models:
                continue
            
            family_dir = os.path.join(self.models_dir, fam)
            team_history_serializable = {
                k: v.to_dict("records") for k, v in self.models[fam]["team_history"].items()
            }
            joblib.dump(team_history_serializable, os.path.join(family_dir, "team_history.pkl"))
            print(f"✅ Historique sauvegardé pour {fam}")


# ──────────────────────────────────────────────────────────────────────────────
# 7. PRÉDICTION API (fonction standalone)
# ──────────────────────────────────────────────────────────────────────────────

def compute_single_match_features(team_home: str, team_away: str, match_time: pd.Timestamp,
                                   team_history: dict, windows: list = [5, 10]) -> dict:
    """
    Calcule les features pour un seul match à partir de l'historique pré-calculé.
    Évite de recalculer tout l'historique à chaque appel API.
    """
    def get_stats_from_history(team: str, before_dt: pd.Timestamp, window: int, is_home_only: bool = False) -> dict:
        hist = team_history.get(team, pd.DataFrame())
        if hist.empty:
            return _empty_stats(window)
        
        # Filtrer les matchs avant la date courante
        hist["finished_at"] = pd.to_datetime(hist["finished_at"], utc=True)
        
        # Filtrer par domicile/extérieur si demandé
        if is_home_only:
            hist = hist[hist["is_home"] == 1]
        
        past = hist[hist["finished_at"] < before_dt].tail(window)
        
        if past.empty:
            return _empty_stats(window)
        
        n = len(past)
        wins = past["win"].sum()
        draws = past["draw"].sum()
        losses = past["loss"].sum()
        gf = past["goals_for"].mean()
        ga = past["goals_against"].mean()
        
        return {
            f"w{window}_played":    n,
            f"w{window}_wins":      wins,
            f"w{window}_draws":     draws,
            f"w{window}_losses":    losses,
            f"w{window}_gf":        gf,
            f"w{window}_ga":        ga,
            f"w{window}_gd":        gf - ga,
            f"w{window}_win_rate":  wins / n,
            f"w{window}_draw_rate": draws / n,
            f"w{window}_unbeaten_rate": (wins + draws) / n,
            f"w{window}_form_points": wins * 3 + draws,
            f"w{window}_form_ppg": (wins * 3 + draws) / n,
        }
    
    def get_h2h_stats(team_home: str, team_away: str, before_dt: pd.Timestamp, window: int) -> dict:
        """Calcule les stats tête-à-tête entre deux équipes."""
        hist_home = team_history.get(team_home, pd.DataFrame())
        hist_away = team_history.get(team_away, pd.DataFrame())
        
        if hist_home.empty or hist_away.empty:
            return _empty_h2h_stats(window)
        
        hist_home["finished_at"] = pd.to_datetime(hist_home["finished_at"], utc=True)
        hist_away["finished_at"] = pd.to_datetime(hist_away["finished_at"], utc=True)
        
        # Trouver les matchs où les deux équipes se sont affrontées
        # On regarde du point de vue de team_home
        h2h_matches = hist_home[
            (hist_home["finished_at"] < before_dt) &
            (hist_home["finished_at"].isin(hist_away["finished_at"]))
        ].tail(window)
        
        if h2h_matches.empty:
            return _empty_h2h_stats(window)
        
        n = len(h2h_matches)
        home_wins = (h2h_matches["win"] == 1).sum()
        draws = (h2h_matches["draw"] == 1).sum()
        away_wins = n - home_wins - draws
        home_gf = h2h_matches["goals_for"].mean()
        away_gf = h2h_matches["goals_against"].mean()
        
        return {
            f"h2h_w{window}_played": n,
            f"h2h_w{window}_home_win_rate": home_wins / n,
            f"h2h_w{window}_draw_rate": draws / n,
            f"h2h_w{window}_away_win_rate": away_wins / n,
            f"h2h_w{window}_home_gf": home_gf,
            f"h2h_w{window}_away_gf": away_gf,
            f"h2h_w{window}_goal_diff": home_gf - away_gf,
        }
    
    def _empty_stats(window: int) -> dict:
        keys = ["played", "wins", "draws", "losses", "gf", "ga", "gd", "win_rate", "draw_rate", "unbeaten_rate", "form_points", "form_ppg"]
        return {f"w{window}_{k}": 0.0 for k in keys}
    
    def _empty_h2h_stats(window: int) -> dict:
        keys = ["played", "home_win_rate", "draw_rate", "away_win_rate", "home_gf", "away_gf", "goal_diff"]
        return {f"h2h_w{window}_{k}": 0.0 for k in keys}
    
    feat = {}
    for w in windows:
        # Stats générales
        h_stats = get_stats_from_history(team_home, match_time, w, is_home_only=False)
        a_stats = get_stats_from_history(team_away, match_time, w, is_home_only=False)
        
        for k, v in h_stats.items():
            feat[f"home_{k}"] = v
        for k, v in a_stats.items():
            feat[f"away_{k}"] = v
        
        # Features différentielles
        feat[f"diff_w{w}_win_rate"]  = h_stats[f"w{w}_win_rate"]  - a_stats[f"w{w}_win_rate"]
        feat[f"diff_w{w}_unbeaten_rate"] = h_stats[f"w{w}_unbeaten_rate"] - a_stats[f"w{w}_unbeaten_rate"]
        feat[f"diff_w{w}_form_points"] = h_stats[f"w{w}_form_points"] - a_stats[f"w{w}_form_points"]
        feat[f"diff_w{w}_form_ppg"] = h_stats[f"w{w}_form_ppg"] - a_stats[f"w{w}_form_ppg"]
        feat[f"diff_w{w}_gf"]        = h_stats[f"w{w}_gf"]        - a_stats[f"w{w}_gf"]
        feat[f"diff_w{w}_ga"]        = h_stats[f"w{w}_ga"]        - a_stats[f"w{w}_ga"]
        feat[f"diff_w{w}_gd"]        = h_stats[f"w{w}_gd"]        - a_stats[f"w{w}_gd"]
        
        # Stats domicile/extérieur uniquement
        h_only_stats = get_stats_from_history(team_home, match_time, w, is_home_only=True)
        a_only_stats = get_stats_from_history(team_away, match_time, w, is_home_only=True)
        
        for k, v in h_only_stats.items():
            feat[f"home_only_{k}"] = v
        for k, v in a_only_stats.items():
            feat[f"away_only_{k}"] = v
        
        # Features différentielles domicile/extérieur uniquement
        feat[f"diff_home_away_only_w{w}_form_ppg"] = h_only_stats[f"w{w}_form_ppg"] - a_only_stats[f"w{w}_form_ppg"]
        feat[f"diff_home_away_only_w{w}_unbeaten_rate"] = h_only_stats[f"w{w}_unbeaten_rate"] - a_only_stats[f"w{w}_unbeaten_rate"]
        
        # Stats tête-à-tête
        h2h_stats = get_h2h_stats(team_home, team_away, match_time, w)
        for k, v in h2h_stats.items():
            feat[k] = v
    
    return feat


def predict_api(team_home: str, team_away: str, league: str, models_dir: str):
    """
    Version optimisée pour API : utilise l'historique pré-calculé.
    Ne nécessite PAS le DataFrame historique complet.
    """
    # Déterminer la famille
    family = "CLASSIC"
    for fam, cfg in FAMILIES.items():
        if cfg["pattern"] and pd.Series([league]).str.contains(cfg["pattern"], regex=True)[0]:
            family = fam
            break
    
    family_dir = os.path.join(models_dir, family)
    if not os.path.exists(family_dir):
        raise FileNotFoundError(f"Modèles non trouvés pour la famille {family}. Lance d'abord l'entraînement.")
    
    # Charger métadonnées et historique
    with open(os.path.join(family_dir, "meta.json")) as f:
        meta = json.load(f)
    
    team_history_serializable = joblib.load(os.path.join(family_dir, "team_history.pkl"))
    team_history = {k: pd.DataFrame(v) for k, v in team_history_serializable.items()}
    
    # Calculer features pour ce match uniquement
    match_time = pd.Timestamp.now(tz="UTC")
    feat = compute_single_match_features(team_home, team_away, match_time, team_history)
    
    # Ajouter features de fréquence équipe (approximation)
    total_matches = sum(len(v) for v in team_history.values())
    home_matches = len(team_history.get(team_home, []))
    away_matches = len(team_history.get(team_away, []))
    feat["home_team_freq"] = home_matches / total_matches if total_matches > 0 else 0
    feat["away_team_freq"] = away_matches / total_matches if total_matches > 0 else 0
    
    # Encodage ligue
    le_league = joblib.load(os.path.join(family_dir, "le_league.pkl"))
    feat["league_enc"] = le_league.transform([league])[0]
    
    # Construire X
    feature_cols = meta["feature_cols"]
    X = np.array([feat.get(col, 0) for col in feature_cols]).reshape(1, -1)
    
    # Charger les modèles
    le_result   = joblib.load(os.path.join(family_dir, "le_result.pkl"))
    clf_result  = joblib.load(os.path.join(family_dir, "result.pkl"))
    reg_goals   = joblib.load(os.path.join(family_dir, "total_goals.pkl"))
    clf_parity  = joblib.load(os.path.join(family_dir, "parity.pkl"))
    poisson_mdl = joblib.load(os.path.join(family_dir, "poisson.pkl"))
    
    # Prédictions
    result_proba = clf_result.predict_proba(X)[0]
    result_classes = le_result.classes_
    result_pred = le_result.inverse_transform([clf_result.predict(X)[0]])[0]
    
    total_goals_pred = float(reg_goals.predict(X)[0])
    parity_pred = "pair" if clf_parity.predict(X)[0] == 1 else "impair"
    parity_proba = clf_parity.predict_proba(X)[0]
    
    max_g = meta["max_goals_poisson"]
    exact_score = poisson_mdl.predict_exact_score(X, max_goals=max_g)[0]
    lh, la = poisson_mdl.predict_lambdas(X)
    
    output = {
        "match": f"{team_home} vs {team_away}",
        "league": league,
        "family": family,
        "result": {
            "prediction": result_pred,
            "probabilities": {c: round(float(p), 3)
                              for c, p in zip(result_classes, result_proba)},
        },
        "total_goals": {
            "prediction": round(total_goals_pred, 1),
            "lambda_home": round(float(lh[0]), 2),
            "lambda_away": round(float(la[0]), 2),
        },
        "parity": {
            "prediction": parity_pred,
            "prob_pair":   round(float(parity_proba[1]), 3),
            "prob_impair": round(float(parity_proba[0]), 3),
        },
        "exact_score": {
            "prediction": f"{exact_score[0]}-{exact_score[1]}",
        },
    }
    return output


# ──────────────────────────────────────────────────────────────────────────────
# 7. PRÉDICTION (helper réutilisable - version legacy)
# ──────────────────────────────────────────────────────────────────────────────

def predict_match(team_home: str, team_away: str, league: str, models_dir: str,
                  history_df: pd.DataFrame):
    """
    Prédit toutes les issues pour un match donné.
    history_df : le DataFrame historique pour calculer les features.
    """
    # Déterminer la famille
    family = "CLASSIC"
    for fam, cfg in FAMILIES.items():
        if cfg["pattern"] and pd.Series([league]).str.contains(cfg["pattern"], regex=True)[0]:
            family = fam
            break

    family_dir = os.path.join(models_dir, family)
    if not os.path.exists(family_dir):
        raise FileNotFoundError(f"Modèles non trouvés pour la famille {family}. Lance d'abord l'entraînement.")

    with open(os.path.join(family_dir, "meta.json")) as f:
        meta = json.load(f)

    # Construire une ligne fictive pour ce match
    fake_row = pd.DataFrame([{
        "id": 999999,
        "match_id": 999999,
        "team_home": team_home,
        "team_away": team_away,
        "league": league,
        "score_home": 0,
        "score_away": 0,
        "finished_at": pd.Timestamp.now(tz="UTC"),
        "source": "predict",
        "created_at": pd.Timestamp.now(tz="UTC"),
        "updated_at": pd.Timestamp.now(tz="UTC"),
    }])
    fake_row["finished_at"] = pd.to_datetime(fake_row["finished_at"], utc=True)
    fake_row["total_goals"] = 0
    fake_row["goals_parity"] = 0
    fake_row["result"] = "H"
    fake_row["family"] = family

    combined = pd.concat([history_df, fake_row], ignore_index=True)
    combined = combined.sort_values("finished_at").reset_index(drop=True)

    feat_df = compute_team_features(combined)
    full, _ = build_features(combined, feat_df)
    full = full.fillna(0)

    row = full[full["id"] == 999999].iloc[0]
    feature_cols = meta["feature_cols"]
    X = row[feature_cols].values.reshape(1, -1)

    # Charger les modèles
    le_result   = joblib.load(os.path.join(family_dir, "le_result.pkl"))
    clf_result  = joblib.load(os.path.join(family_dir, "result.pkl"))
    reg_goals   = joblib.load(os.path.join(family_dir, "total_goals.pkl"))
    clf_parity  = joblib.load(os.path.join(family_dir, "parity.pkl"))
    poisson_mdl = joblib.load(os.path.join(family_dir, "poisson.pkl"))

    # Prédictions
    result_proba = clf_result.predict_proba(X)[0]
    result_classes = le_result.classes_
    result_pred = le_result.inverse_transform([clf_result.predict(X)[0]])[0]

    total_goals_pred = float(reg_goals.predict(X)[0])
    parity_pred = "pair" if clf_parity.predict(X)[0] == 1 else "impair"
    parity_proba = clf_parity.predict_proba(X)[0]

    max_g = meta["max_goals_poisson"]
    exact_score = poisson_mdl.predict_exact_score(X, max_goals=max_g)[0]
    lh, la = poisson_mdl.predict_lambdas(X)

    output = {
        "match": f"{team_home} vs {team_away}",
        "league": league,
        "family": family,
        "result": {
            "prediction": result_pred,
            "probabilities": {c: round(float(p), 3)
                              for c, p in zip(result_classes, result_proba)},
        },
        "total_goals": {
            "prediction": round(total_goals_pred, 1),
            "lambda_home": round(float(lh[0]), 2),
            "lambda_away": round(float(la[0]), 2),
        },
        "parity": {
            "prediction": parity_pred,
            "prob_pair":   round(float(parity_proba[1]), 3),
            "prob_impair": round(float(parity_proba[0]), 3),
        },
        "exact_score": {
            "prediction": f"{exact_score[0]}-{exact_score[1]}",
        },
    }
    return output


# ──────────────────────────────────────────────────────────────────────────────
# 7. POINT D'ENTRÉE
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Entraînement multi-familles / multi-tâches")
    parser.add_argument("--csv",  required=True, help="Chemin vers le CSV des matchs terminés")
    parser.add_argument("--out",  default="./models", help="Répertoire de sortie des modèles")
    parser.add_argument("--eval", action="store_true", help="Afficher les métriques d'évaluation")
    parser.add_argument("--predict", action="store_true",
                        help="Mode démo : prédit un match exemple après l'entraînement")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    print("=" * 60)
    print("  CHARGEMENT DES DONNÉES")
    print("=" * 60)
    df = load_data(args.csv)
    df = assign_family(df)

    print(f"  {len(df)} matchs chargés")
    for fam in FAMILIES:
        n = (df["family"] == fam).sum()
        print(f"  {fam:12s} : {n} matchs")

    all_meta = {}
    for family, cfg in FAMILIES.items():
        df_fam = df[df["family"] == family].copy()
        if len(df_fam) == 0:
            print(f"\n⚠️  Famille {family} : aucun match trouvé, ignorée.")
            continue
        meta = train_family(family, df_fam, cfg, args.out, evaluate=args.eval)
        if meta:
            all_meta[family] = meta

    # Résumé global
    summary_path = os.path.join(args.out, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(all_meta, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("  ENTRAÎNEMENT TERMINÉ")
    print(f"  Résumé global : {summary_path}")
    print("=" * 60)

    # Démo de prédiction
    if args.predict:
        print("\n--- DÉMO PRÉDICTION ---")
        try:
            result = predict_match(
                team_home="Bayern Munich",
                team_away="Manchester City",
                league="FC 26. Champions League",
                models_dir=args.out,
                history_df=df,
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Erreur prédiction démo : {e}")


if __name__ == "__main__":
    main()
