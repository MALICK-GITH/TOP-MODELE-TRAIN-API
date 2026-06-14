import pandas as pd

df = pd.read_csv(r'c:\Users\HP\Downloads\Telegram Desktop\finished_matches_dataset_20260613_234049_recent_form_advanced_features.csv')
print("Ligues présentes dans les données:")
for league in df['league'].unique():
    count = len(df[df['league'] == league])
    print(f"  - {league}: {count} matchs")
