"""
Script de test pour vérifier que les modèles fonctionnent sans score exact
"""
import pickle
import pandas as pd

# Charger les modèles
models = {}
for family in ["PENALTY", "HIGHSCORE", "RUSH", "CLASSIC"]:
    with open(f"models/{family}.pkl", "rb") as f:
        models[family] = pickle.load(f)
    print(f"✅ {family} chargé")

# Vérifier que les modèles Poisson ne sont pas présents
for family, model_data in models.items():
    print(f"\nFamille: {family}")
    print(f"Modèles disponibles: {list(model_data['models'].keys())}")
    
    # Vérifier que poisson_lambda_home et poisson_lambda_away ne sont pas présents
    if "poisson_lambda_home" in model_data["models"]:
        print("❌ ERREUR: poisson_lambda_home est présent")
    else:
        print("✅ poisson_lambda_home n'est pas présent")
    
    if "poisson_lambda_away" in model_data["models"]:
        print("❌ ERREUR: poisson_lambda_away est présent")
    else:
        print("✅ poisson_lambda_away n'est pas présent")

print("\n✅ Vérification terminée")
