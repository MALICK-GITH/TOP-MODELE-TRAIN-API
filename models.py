"""
Module contenant les classes de modèles ML pour FIFA Prediction.
Ce module est séparé pour permettre le pickle/unpickle correct des modèles.
"""

import numpy as np
from scipy.stats import poisson
from sklearn.linear_model import PoissonRegressor
from sklearn.preprocessing import StandardScaler


class PoissonScoreModel:
    """
    Modèle de Poisson indépendant pour chaque équipe.
    Prédit lambda_home et lambda_away puis calcule P(score_home=i, score_away=j).
    """

    def __init__(self):
        self.model_home = PoissonRegressor(max_iter=500)
        self.model_away = PoissonRegressor(max_iter=500)
        self.scaler = StandardScaler()
        self.feature_cols = None

    def fit(self, X: np.ndarray, y_home: np.ndarray, y_away: np.ndarray, feature_cols: list):
        self.feature_cols = feature_cols
        Xs = self.scaler.fit_transform(X)
        self.model_home.fit(Xs, y_home)
        self.model_away.fit(Xs, y_away)
        return self

    def predict_lambdas(self, X: np.ndarray):
        Xs = self.scaler.transform(X)
        lh = np.clip(self.model_home.predict(Xs), 0.1, 30)
        la = np.clip(self.model_away.predict(Xs), 0.1, 30)
        return lh, la

    def predict_exact_score(self, X: np.ndarray, max_goals: int = 10):
        lh, la = self.predict_lambdas(X)
        results = []
        for lh_i, la_i in zip(lh, la):
            best_prob = 0
            best_score = (0, 0)
            for i in range(max_goals + 1):
                for j in range(max_goals + 1):
                    p = poisson.pmf(i, lh_i) * poisson.pmf(j, la_i)
                    if p > best_prob:
                        best_prob = p
                        best_score = (i, j)
            results.append(best_score)
        return results

    def predict_total_goals(self, X: np.ndarray):
        lh, la = self.predict_lambdas(X)
        return lh + la

    def predict_result_proba(self, X: np.ndarray, has_draw: bool = True, max_goals: int = 15):
        """Calcule P(H), P(D), P(A) en intégrant la distribution de Poisson."""
        lh, la = self.predict_lambdas(X)
        probas = []
        for lh_i, la_i in zip(lh, la):
            ph = pd_ = pa = 0.0
            for i in range(max_goals + 1):
                for j in range(max_goals + 1):
                    p = poisson.pmf(i, lh_i) * poisson.pmf(j, la_i)
                    if i > j:
                        ph += p
                    elif i == j:
                        pd_ += p
                    else:
                        pa += p
            if not has_draw:
                total = ph + pa
                probas.append([ph / total, 0.0, pa / total])
            else:
                probas.append([ph, pd_, pa])
        return np.array(probas)
