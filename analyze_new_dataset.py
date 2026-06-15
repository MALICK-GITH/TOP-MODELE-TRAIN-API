import pandas as pd

df = pd.read_csv(r'c:\Users\HP\Downloads\finished_matches_dataset_20260614_235819.csv')

print("=== ANALYSE DU NOUVEAU DATASET ===")
print(f"\nNombre total de matchs: {len(df)}")
print(f"\nColonnes: {df.columns.tolist()}")
print(f"\nLigues présentes:")
for league in df['league'].unique():
    count = len(df[df['league'] == league])
    print(f"  - {league}: {count} matchs")

print(f"\nSource: {df['source'].unique()}")
print(f"\nPériode:")
print(f"  - Premier match: {df['finished_at'].min()}")
print(f"  - Dernier match: {df['finished_at'].max()}")

print(f"\nDistribution des scores:")
print(df[['score_home', 'score_away']].describe())
