import requests
import json

headers = {
    'Authorization': 'Bearer rnd_E1s5FjqxBUBV5Fw1wZZnXyOLjavz',
    'Content-Type': 'application/json'
}

r = requests.get('https://api.render.com/v1/services/srv-d8p8jsq8qa3s73bkshlg/deploys', headers=headers)
deps = r.json()

print(f'Nombre de déploiements: {len(deps)}')
print(f'Structure du premier déploiement: {json.dumps(deps[0], indent=2)[:500]}')
