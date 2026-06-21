"""
Script pour contrôler Render via l'API
"""

import requests
import json

API_KEY = "rnd_E1s5FjqxBUBV5Fw1wZZnXyOLjavz"
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def get_services():
    """Récupérer tous les services"""
    r = requests.get('https://api.render.com/v1/services', headers=headers)
    return r.json()

def find_fifa_service():
    """Trouver le service FIFA"""
    services = get_services()
    fifa_services = []
    
    for item in services:
        service = item.get('service', {})
        name = service.get('name', '').lower()
        if 'fifa' in name or 'prediction' in name:
            fifa_services.append(service)
    
    return fifa_services

def get_service_status(service_id):
    """Récupérer le statut d'un service"""
    r = requests.get(f'https://api.render.com/v1/services/{service_id}', headers=headers)
    return r.json()

def get_service_logs(service_id):
    """Récupérer les logs d'un service"""
    r = requests.get(f'https://api.render.com/v1/services/{service_id}/logs', headers=headers)
    return r.json()

def get_deployments(service_id):
    """Récupérer les déploiements d'un service"""
    r = requests.get(f'https://api.render.com/v1/services/{service_id}/deployments', headers=headers)
    return r.json()

def get_service_details(service_id):
    """Récupérer les détails d'un service"""
    r = requests.get(f'https://api.render.com/v1/services/{service_id}', headers=headers)
    return r.json()

def get_service_events(service_id):
    """Récupérer les événements d'un service"""
    r = requests.get(f'https://api.render.com/v1/services/{service_id}/events', headers=headers)
    return r.json()

def trigger_deployment(service_id):
    """Déclencher un déploiement manuel"""
    r = requests.post(f'https://api.render.com/v1/services/{service_id}/deploys', headers=headers)
    return r.json()

def update_environment_variables(service_id, env_vars):
    """Mettre à jour les variables d'environnement"""
    # D'abord récupérer les variables actuelles
    r = requests.get(f'https://api.render.com/v1/services/{service_id}/env-vars', headers=headers)
    current_vars = r.json()
    
    # Préparer les nouvelles variables
    new_vars = []
    for key, value in env_vars.items():
        new_vars.append({
            'key': key,
            'value': value
        })
    
    # Envoyer les nouvelles variables
    r = requests.patch(f'https://api.render.com/v1/services/{service_id}/env-vars', 
                     headers=headers, 
                     json=new_vars)
    return r.json()

if __name__ == "__main__":
    print("=" * 80)
    print("CONTRÔLE RENDER - SERVICE FIFA")
    print("=" * 80)
    
    # ID du service FIFA
    fifa_service_id = "srv-d8p8jsq8qa3s73bkshlg"
    
    print(f"\n� Service FIFA: TOP-MODELE-TRAIN-API_VMP")
    print(f"   ID: {fifa_service_id}")
    
    # Récupérer les détails du service
    try:
        details = get_service_details(fifa_service_id)
        print(f"\n� Détails du service:")
        print(f"   Nom: {details.get('name')}")
        print(f"   URL: {details.get('serviceDetails', {}).get('url')}")
        print(f"   Statut: {details.get('suspended')}")
        print(f"   Auto-déploiement: {details.get('autoDeploy')}")
        print(f"   Branche: {details.get('branch')}")
        print(f"   Repo: {details.get('repo')}")
        print(f"   Créé le: {details.get('createdAt')}")
        print(f"   Mis à jour le: {details.get('updatedAt')}")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    # Récupérer les événements
    try:
        events = get_service_events(fifa_service_id)
        print(f"\n📋 Événements récents:")
        if events:
            for event in events[:5]:
                print(f"  - {event.get('createdAt')}: {event.get('type')} - {event.get('message', '')[:100]}")
        else:
            print("  Aucun événement trouvé")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    # Récupérer les déploiements
    try:
        deployments = get_deployments(fifa_service_id)
        print(f"\n📦 Déploiements récents:")
        if deployments:
            for dep in deployments[:5]:
                print(f"  - {dep.get('createdAt')}: {dep.get('status')} ({dep.get('id')[:20]}...)")
                print(f"    Commit: {dep.get('commit', {}).get('message', '')[:50]}")
        else:
            print("  Aucun déploiement trouvé")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    # Déclencher un nouveau déploiement
    print(f"\n🚀 Déclenchement d'un nouveau déploiement...")
    try:
        deploy_result = trigger_deployment(fifa_service_id)
        print(f"   Déploiement déclenché avec succès!")
        print(f"   ID: {deploy_result.get('id')}")
        print(f"   Statut: {deploy_result.get('status')}")
    except Exception as e:
        print(f"   Erreur lors du déclenchement: {e}")
    
    # Mettre à jour les variables d'environnement
    print(f"\n🔧 Mise à jour des variables d'environnement...")
    try:
        env_vars = {
            'UPSTASH_REDIS_REST_URL': 'https://beloved-grouper-148747.upstash.io',
            'UPSTASH_REDIS_REST_TOKEN': 'gQAAAAAAAkULAAIgcDE5ZmU1NTg3ZTAxMjE0OWQzOWUzN2U4NDM3ZTNmZmI1ZA'
        }
        env_result = update_environment_variables(fifa_service_id, env_vars)
        print(f"   Variables d'environnement mises à jour avec succès!")
        print(f"   Résultat: {env_result}")
    except Exception as e:
        print(f"   Erreur lors de la mise à jour: {e}")
