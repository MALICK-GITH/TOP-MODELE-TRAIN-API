import pandas as pd

df = pd.read_csv('finished_matches_dataset.csv')
df['total_goals'] = df['score_home'] + df['score_away']

# Define family mappings
penalty_leagues = ['FC24. Penalty', 'FC25. Penalty', 'FC26. Penalty', 'FIFA23. Penalty', 'Penalty']
highscore_leagues = ['FC 24. 4x4. Championnat d\'Angleterre', 'FC 25. 3x3. Ligue de conférence']
rush_leagues = ['FC 26. 5x5 Rush. Superligue']

print('Distribution des buts par famille:')
print('=' * 80)

# PENALTY
mask = df['league'].isin(penalty_leagues)
data = df[mask]['total_goals']
print(f'PENALTY: min={data.min()}, max={data.max()}, mean={data.mean():.1f}, median={data.median():.1f}, 25%={data.quantile(0.25):.1f}, 75%={data.quantile(0.75):.1f}')
print(f'  Distribution des valeurs les plus fréquentes:')
print(f'  {data.value_counts().head(10).to_dict()}')

# HIGHSCORE
mask = df['league'].isin(highscore_leagues)
data = df[mask]['total_goals']
print(f'HIGHSCORE: min={data.min()}, max={data.max()}, mean={data.mean():.1f}, median={data.median():.1f}, 25%={data.quantile(0.25):.1f}, 75%={data.quantile(0.75):.1f}')
print(f'  Distribution des valeurs les plus fréquentes:')
print(f'  {data.value_counts().head(10).to_dict()}')

# RUSH
mask = df['league'].isin(rush_leagues)
data = df[mask]['total_goals']
print(f'RUSH: min={data.min()}, max={data.max()}, mean={data.mean():.1f}, median={data.median():.1f}, 25%={data.quantile(0.25):.1f}, 75%={data.quantile(0.75):.1f}')
print(f'  Distribution des valeurs les plus fréquentes:')
print(f'  {data.value_counts().head(10).to_dict()}')

# CLASSIC
mask = ~df['league'].isin(penalty_leagues + highscore_leagues + rush_leagues)
data = df[mask]['total_goals']
print(f'CLASSIC: min={data.min()}, max={data.max()}, mean={data.mean():.1f}, median={data.median():.1f}, 25%={data.quantile(0.25):.1f}, 75%={data.quantile(0.75):.1f}')
print(f'  Distribution des valeurs les plus fréquentes:')
print(f'  {data.value_counts().head(10).to_dict()}')
