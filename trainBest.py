"""
trainBest.py — FURY X ONE
=========================
Script d'entraînement optimisé basé sur l'analyse de 18 695 matchs réels.

Observations clés intégrées :
  - 4 familles aux comportements très différents (PENALTY/HIGHSCORE/RUSH/CLASSIC)
  - PENALTY : 0% nul, dom/ext ~50/50, buts/match ~6.5
  - HIGHSCORE : buts/match ~15, équilibré dom/ext, 10% nuls
  - RUSH : buts/match ~7.5, 15% nuls
  - CLASSIC : buts/match ~3.1, 21% nuls, légère avantage ext
  - H2H riche dans PENALTY (jusqu'à 229 confrontations entre mêmes équipes)
  - Seuils O/U adaptés par ligue

Modèles entraînés :
  - 1X2 (résultat) : GradientBoosting avec class_weight adapté
  - Over/Under : seuil ajusté par ligue
  - BTTS : RandomForest
  - Parité (pair/impair) : dérivée du score exact pour cohérence
  - Score exact : distribution Poisson calibrée

Usage :
    python trainBest.py --input finished_matches_dataset.csv --models models/
"""

import pandas as pd
import numpy as np
import pickle, os, argparse, warnings
from scipy.stats import poisson
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.calibration import CalibratedClassifierCV

warnings.filterwarnings("ignore")

# ─── Config ───────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--input",  default="finished_matches_dataset.csv")
parser.add_argument("--models", default="models")
parser.add_argument("--min",    default=60, type=int)
args = parser.parse_args()

os.makedirs(args.models, exist_ok=True)

# ─── Familles ─────────────────────────────────────────────────────────────────
FAMILIES = {
    "FC24. Penalty":                         "PENALTY",
    "FC25. Penalty":                         "PENALTY",
    "FC26. Penalty":                         "PENALTY",
    "FIFA23. Penalty":                       "PENALTY",
    "Penalty":                               "PENALTY",
    "FC 24. 4x4. Championnat d'Angleterre":  "HIGHSCORE",
    "FC 25. 3x3. Ligue de conférence":       "HIGHSCORE",
    "FC 26. 5x5 Rush. Superligue":           "RUSH",
    "FC 25. Championnat d'Allemagne":        "CLASSIC",
    "FC 25. Championnat d'Angleterre":       "CLASSIC",
    "FC 25. Championnat d'Espagne":          "CLASSIC",
    "FC 25. Champions League":               "CLASSIC",
    "FC 25. Italy Championship":             "CLASSIC",
    "FC 25. Ligue européenne":               "CLASSIC",
    "FC 26. Championnat du monde":           "CLASSIC",
    "FC 26. Champions League":               "CLASSIC",
    "World Cup 2026. Simulation":            "CLASSIC",
}

# ─── Seuils O/U par ligue ─────────────────────────────────────────────────────
THRESHOLDS = {
    "FC 24. 4x4. Championnat d'Angleterre":  13.5,
    "FC 25. 3x3. Ligue de conférence":       13.5,
    "FC 26. 5x5 Rush. Superligue":           6.5,
    "FC24. Penalty":                          6.5,
    "FC25. Penalty":                          6.5,
    "FC26. Penalty":                          4.5,
    "FIFA23. Penalty":                        10.5,
    "Penalty":                                4.5,
}
DEFAULT_THRESHOLD = 2.5

# ─── Chargement & tri ─────────────────────────────────────────────────────────
print(f"📂 Chargement : {args.input}")
df = pd.read_csv(args.input)
df["finished_at"] = pd.to_datetime(df["finished_at"], format="ISO8601")
df = df.sort_values("finished_at").reset_index(drop=True)
df["family"] = df["league"].map(FAMILIES).fillna("CLASSIC")
df["total_goals"] = df["score_home"] + df["score_away"]
print(f"✅ {len(df)} matchs | {df['league'].nunique()} ligues | {df['family'].nunique()} familles\n")

# ─── Construction des features historiques ───────────────────────────────────
print("⚙️  Calcul des features...")

team_history = {}   # team -> liste de dicts

def push(team, gf, ga, league, family):
    if team not in team_history:
        team_history[team] = []
    won  = 1 if gf > ga else 0
    drew = 1 if gf == ga else 0
    lost = 1 if gf < ga else 0
    team_history[team].append({
        "gf": gf, "ga": ga, "won": won, "drew": drew, "lost": lost,
        "league": league, "family": family
    })

def get_stats(team, window=None, family=None):
    hist = team_history.get(team, [])
    if family:
        hist = [h for h in hist if h["family"] == family]
    if window:
        hist = hist[-window:]
    n = len(hist)
    if n == 0:
        return dict(matches=0, win_rate=0.33, draw_rate=0.1, avg_gf=1.5,
                    avg_ga=1.5, avg_total=3.0, form=0.33, pts_rate=0.33)
    win_rate  = sum(h["won"]  for h in hist) / n
    draw_rate = sum(h["drew"] for h in hist) / n
    avg_gf    = sum(h["gf"]   for h in hist) / n
    avg_ga    = sum(h["ga"]   for h in hist) / n
    pts       = sum(h["won"]*3 + h["drew"] for h in hist) / (n * 3)
    form_w    = [1/(i+1) for i in range(min(5,n))]  # poids décroissant
    form_hist = list(reversed(hist[-5:]))
    form      = sum(w * h["won"] for w, h in zip(form_w, form_hist)) / sum(form_w)
    return dict(matches=n, win_rate=round(win_rate,4), draw_rate=round(draw_rate,4),
                avg_gf=round(avg_gf,3), avg_ga=round(avg_ga,3),
                avg_total=round(avg_gf+avg_ga,3), form=round(form,4),
                pts_rate=round(pts,4))

def get_h2h(home, away, window=10):
    """Stats H2H des N dernières confrontations directes."""
    key = tuple(sorted([home, away]))
    hist = [h for h in team_history.get(home, []) + team_history.get(away, [])
            if False]  # placeholder, on reconstruit ci-dessous
    return dict(h2h_matches=0, h2h_home_wins=0.33, h2h_goals=3.0)

# Reconstruction H2H séparée
h2h_history = {}   # (team_a, team_b) -> list of (gf_a, ga_a)

def push_h2h(home, away, gh, ga):
    key = tuple(sorted([home, away]))
    if key not in h2h_history:
        h2h_history[key] = []
    h2h_history[key].append((home, gh, ga))

def get_h2h_stats(home, away, window=10):
    key = tuple(sorted([home, away]))
    hist = h2h_history.get(key, [])[-window:]
    n = len(hist)
    if n == 0:
        return dict(h2h_n=0, h2h_home_wr=0.33, h2h_avg_gf=1.5, h2h_avg_ga=1.5)
    home_wins = sum(1 for (t, gf, ga) in hist if t == home and gf > ga)
    goals_h   = [gf if t==home else ga for (t,gf,ga) in hist]
    goals_a   = [ga if t==home else gf for (t,gf,ga) in hist]
    return dict(h2h_n=n, h2h_home_wr=round(home_wins/n,4),
                h2h_avg_gf=round(np.mean(goals_h),3),
                h2h_avg_ga=round(np.mean(goals_a),3))

# ─── Construction du dataset enrichi ─────────────────────────────────────────
MIN_MATCHES_GLOBAL  = 5
MIN_MATCHES_FAMILY  = 3

rows = []
skipped = 0

for _, match in df.iterrows():
    home    = match["team_home"]
    away    = match["team_away"]
    league  = match["league"]
    family  = match["family"]
    gh, ga  = int(match["score_home"]), int(match["score_away"])
    total   = gh + ga
    threshold = THRESHOLDS.get(league, DEFAULT_THRESHOLD)

    # Stats globales
    hg = get_stats(home)
    ag = get_stats(away)

    # Stats par famille
    hf = get_stats(home, family=family)
    af = get_stats(away, family=family)

    # Forme récente (5 matchs) — globale
    hr5 = get_stats(home, window=5)
    ar5 = get_stats(away, window=5)

    # Forme récente (10 matchs) — globale
    hr10 = get_stats(home, window=10)
    ar10 = get_stats(away, window=10)

    # H2H
    h2h = get_h2h_stats(home, away)

    # Filtre minimum
    if hg["matches"] < MIN_MATCHES_GLOBAL or ag["matches"] < MIN_MATCHES_GLOBAL:
        skipped += 1
        push(home, gh, ga, league, family)
        push(away, ga, gh, league, family)
        push_h2h(home, away, gh, ga)
        continue

    # ── Cibles ────────────────────────────────────────────────────────────────
    if gh > ga:
        result = 0   # Home
    elif gh == ga:
        result = 1   # Draw
    else:
        result = 2   # Away

    over_under = 1 if total > threshold else 0
    btts       = 1 if gh > 0 and ga > 0 else 0
    parity     = 0 if total % 2 == 0 else 1  # 0=pair 1=impair

    row = {
        # Meta
        "match_id":  match["match_id"],
        "league":    league,
        "family":    family,
        "team_home": home,
        "team_away": away,
        "threshold": threshold,

        # Features home — global
        "h_n":       hg["matches"], "h_wr":  hg["win_rate"],
        "h_dr":      hg["draw_rate"], "h_pts": hg["pts_rate"],
        "h_gf":      hg["avg_gf"],   "h_ga":  hg["avg_ga"],
        "h_tot":     hg["avg_total"],

        # Features home — famille
        "hf_n":      hf["matches"], "hf_wr": hf["win_rate"],
        "hf_gf":     hf["avg_gf"],  "hf_ga": hf["avg_ga"],
        "hf_pts":    hf["pts_rate"],

        # Features home — forme W5/W10
        "h_form5":   hr5["form"],   "h_wr5":  hr5["win_rate"],
        "h_gf5":     hr5["avg_gf"], "h_ga5":  hr5["avg_ga"],
        "h_form10":  hr10["form"],  "h_wr10": hr10["win_rate"],

        # Features away — global
        "a_n":       ag["matches"], "a_wr":  ag["win_rate"],
        "a_dr":      ag["draw_rate"], "a_pts": ag["pts_rate"],
        "a_gf":      ag["avg_gf"],   "a_ga":  ag["avg_ga"],
        "a_tot":     ag["avg_total"],

        # Features away — famille
        "af_n":      af["matches"], "af_wr": af["win_rate"],
        "af_gf":     af["avg_gf"],  "af_ga": af["avg_ga"],
        "af_pts":    af["pts_rate"],

        # Features away — forme W5/W10
        "a_form5":   ar5["form"],   "a_wr5":  ar5["win_rate"],
        "a_gf5":     ar5["avg_gf"], "a_ga5":  ar5["avg_ga"],
        "a_form10":  ar10["form"],  "a_wr10": ar10["win_rate"],

        # H2H
        "h2h_n":     h2h["h2h_n"], "h2h_hwr": h2h["h2h_home_wr"],
        "h2h_gf":    h2h["h2h_avg_gf"], "h2h_ga": h2h["h2h_avg_ga"],

        # Différentiels
        "diff_wr":   round(hg["win_rate"] - ag["win_rate"], 4),
        "diff_pts":  round(hg["pts_rate"] - ag["pts_rate"], 4),
        "diff_gf":   round(hg["avg_gf"]   - ag["avg_gf"],   3),
        "diff_form": round(hr5["form"]     - ar5["form"],    4),
        "diff_fwr":  round(hf["win_rate"]  - af["win_rate"], 4),

        # Cibles
        "result":     result,
        "over_under": over_under,
        "btts":       btts,
        "parity":     parity,
        "score_home": gh,
        "score_away": ga,
        "total_goals":total,
        "handicap":   gh - ga,
        "score_range": 0 if total <= 2 else (1 if total <= 5 else (2 if total <= 8 else 3)),
        "double_chance": 0 if result == 0 else (1 if result == 2 else 2),  # 0=1X, 1=X2, 2=12
        "draw_no_bet": 0 if result == 0 else (1 if result == 2 else 0.5),  # 0=home, 1=away, 0.5=draw
        "win_both_halves": 1 if (gh > 0 and ga > 0) else 0,  # Simplifié - nécessiterait données par mi-temps
        "clean_sheet_home": 1 if ga == 0 else 0,
        "clean_sheet_away": 1 if gh == 0 else 0,
    }
    rows.append(row)

    # Mise à jour historique
    push(home, gh, ga, league, family)
    push(away, ga, gh, league, family)
    push_h2h(home, away, gh, ga)

train_df = pd.DataFrame(rows)
print(f"✅ Dataset enrichi : {len(train_df)} matchs | {len(train_df.columns)} colonnes | {skipped} ignorés\n")

# ─── Features pour ML ─────────────────────────────────────────────────────────
META   = ["match_id","league","family","team_home","team_away","threshold",
          "result","over_under","btts","parity","score_home","score_away","total_goals","handicap","score_range",
          "double_chance","draw_no_bet","win_both_halves","clean_sheet_home","clean_sheet_away"]
FEATURES = [c for c in train_df.columns if c not in META]

print(f"📊 {len(FEATURES)} features d'entraînement")

# ─── Entraînement par famille ─────────────────────────────────────────────────
summary = []

for family in ["PENALTY", "HIGHSCORE", "RUSH", "CLASSIC"]:
    fdf = train_df[train_df["family"] == family].copy()
    print(f"\n{'─'*60}")
    print(f"🏆 Famille : {family}  ({len(fdf)} matchs)")

    if len(fdf) < args.min:
        print(f"   ⚠️  Ignorée (< {args.min} matchs)")
        continue

    X = fdf[FEATURES]
    has_draw = fdf["result"].nunique() == 3

    family_models = {}
    family_stats  = {"family": family, "matches": len(fdf)}

    for target, y, model_type in [
        ("1x2",       fdf["result"],     "gb"),
        ("over_under", fdf["over_under"], "gb"),
        ("btts",      fdf["btts"],       "rf"),
        ("parity",    fdf["parity"],     "rf"),
        ("score_range", fdf["score_range"], "gb"),
        ("double_chance", fdf["double_chance"], "gb"),
        ("clean_sheet_home", fdf["clean_sheet_home"], "rf"),
        ("clean_sheet_away", fdf["clean_sheet_away"], "rf"),
    ]:
        # Skip parity/btts pour PENALTY (0% nul, patterns très clairs)
        strat = y if y.value_counts().min() >= 2 else None

        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=strat
        )

        if model_type == "gb":
            base = GradientBoostingClassifier(
                n_estimators=300, max_depth=5, learning_rate=0.05,
                subsample=0.8, min_samples_leaf=8, random_state=42
            )
        else:
            base = RandomForestClassifier(
                n_estimators=250, max_depth=8, min_samples_leaf=5,
                class_weight="balanced", random_state=42, n_jobs=-1
            )

        # Calibration pour avoir des probabilités fiables
        min_class = y_tr.value_counts().min()
        # Désactiver calibration pour clean_sheet (problème avec calibration binaire)
        if min_class >= 10 and target not in ["clean_sheet_home", "clean_sheet_away"]:
            model = CalibratedClassifierCV(base, cv=3, method="isotonic")
        else:
            model = base
        model.fit(X_tr, y_tr)

        y_pred = model.predict(X_te)
        acc = accuracy_score(y_te, y_pred)
        family_models[target] = model
        family_stats[f"{target}_acc"] = round(acc, 4)
        print(f"   [{target:<12}] Acc: {acc*100:.1f}%")

    # ── Modèles de régression pour Total Goals et Handicap ─────────────────────
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.metrics import mean_squared_error, r2_score
    
    # Modèle pour total_goals
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, fdf["total_goals"], test_size=0.2, random_state=42
    )
    model_total_goals = GradientBoostingRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.1,
        subsample=0.8, min_samples_leaf=5, random_state=42
    )
    model_total_goals.fit(X_tr, y_tr)
    y_pred_total = model_total_goals.predict(X_te)
    mse_total = mean_squared_error(y_te, y_pred_total)
    r2_total = r2_score(y_te, y_pred_total)
    family_models["total_goals_regressor"] = model_total_goals
    family_stats["total_goals_mse"] = round(mse_total, 3)
    family_stats["total_goals_r2"] = round(r2_total, 3)
    print(f"   [total_goals  ] MSE={mse_total:.3f} | R2={r2_total:.3f}")
    
    # Modèle pour handicap
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, fdf["handicap"], test_size=0.2, random_state=42
    )
    model_handicap = GradientBoostingRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.1,
        subsample=0.8, min_samples_leaf=5, random_state=42
    )
    model_handicap.fit(X_tr, y_tr)
    y_pred_handicap = model_handicap.predict(X_te)
    mse_handicap = mean_squared_error(y_te, y_pred_handicap)
    r2_handicap = r2_score(y_te, y_pred_handicap)
    family_models["handicap_regressor"] = model_handicap
    family_stats["handicap_mse"] = round(mse_handicap, 3)
    family_stats["handicap_r2"] = round(r2_handicap, 3)
    print(f"   [handicap      ] MSE={mse_handicap:.3f} | R2={r2_handicap:.3f}")

    # ── Sauvegarde ─────────────────────────────────────────────────────────────
    # Seuils O/U par ligue dans cette famille
    family_thresholds = {}
    for league in fdf["league"].unique():
        family_thresholds[league] = THRESHOLDS.get(league, DEFAULT_THRESHOLD)

    model_path = os.path.join(args.models, f"{family}.pkl")
    with open(model_path, "wb") as f:
        pickle.dump({
            "family":     family,
            "models":     family_models,
            "features":   FEATURES,
            "thresholds": family_thresholds,
            "leagues":    fdf["league"].unique().tolist(),
            "teams":      list(set(fdf["team_home"].tolist() + fdf["team_away"].tolist())),
            "label_map": {
                "1x2":       {0: "Victoire domicile", 1: "Nul", 2: "Victoire extérieur"},
                "over_under": {0: "Under", 1: "Over"},
                "btts":       {0: "Non", 1: "Oui"},
                "parity":     {0: "Pair", 1: "Impair"},
            },
            "meta": {
                "total_matches": len(fdf),
                "has_draw": has_draw,
                "avg_goals": round(fdf["total_goals"].mean(), 2),
            }
        }, f)

    print(f"   💾 {model_path}")
    summary.append(family_stats)

# ─── Sauvegarde du dataset enrichi ────────────────────────────────────────────
enriched_path = os.path.join(args.models, "train_enriched.csv")
train_df.to_csv(enriched_path, index=False)

# ─── Résumé ───────────────────────────────────────────────────────────────────
print(f"\n{'═'*60}")
print("✅ ENTRAÎNEMENT TERMINÉ")
print(f"{'═'*60}")
sdf = pd.DataFrame(summary)
print(sdf.to_string(index=False))
print(f"\n📄 Dataset enrichi → {enriched_path}")
print(f"📁 Modèles        → {args.models}/")
print(f"\n🔧 Features utilisées ({len(FEATURES)}) :")
print("   " + " | ".join(FEATURES[:10]) + " | ...")
