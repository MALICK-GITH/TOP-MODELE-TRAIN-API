# Guide de Configuration des Variables d'Environnement sur Render

## 📋 Vue d'ensemble

Ce guide explique comment configurer les variables d'environnement sur Render pour le cache Upstash Redis.

---

## 🚀 Étape 1: Accéder au Dashboard Render

1. Aller sur https://dashboard.render.com
2. Se connecter avec votre compte
3. Sélectionner votre service API (TOP-MODELE-TRAIN-API)

---

## 🔧 Étape 2: Ajouter les Variables d'Environnement

### Méthode via l'Interface Web

1. **Dans le Dashboard Render:**
   - Cliquer sur votre service API
   - Aller dans la section "Environment"
   - Cliquer sur "Add Environment Variable"

2. **Ajouter UPSTASH_REDIS_REST_URL:**
   - **Key:** `UPSTASH_REDIS_REST_URL`
   - **Value:** `https://beloved-grouper-148747.upstash.io`
   - Cliquer sur "Save"

3. **Ajouter UPSTASH_REDIS_REST_TOKEN:**
   - **Key:** `UPSTASH_REDIS_REST_TOKEN`
   - **Value:** `gQAAAAAAAkULAAIgcDE5ZmU1NTg3ZTAxMjE0OWQzOWUzN2U4NDM3ZTNmZmI1ZA`
   - Cliquer sur "Save"

### Méthode via Render CLI (Alternative)

```bash
# Installer Render CLI
npm install -g @render-oss/render-cli

# Se connecter
render login

# Ajouter les variables d'environnement
render env set UPSTASH_REDIS_REST_URL "https://beloved-grouper-148747.upstash.io" --service votre-service-id
render env set UPSTASH_REDIS_REST_TOKEN "gQAAAAAAAkULAAIgcDE5ZmU1NTg3ZTAxMjE0OWQzOWUzN2U4NDM3ZTNmZmI1ZA" --service votre-service-id
```

---

## 🔄 Étape 3: Redéployer le Service

Après avoir ajouté les variables d'environnement, Render redéploiera automatiquement le service. Vous pouvez aussi le faire manuellement:

1. **Dans le Dashboard Render:**
   - Cliquer sur "Manual Deploy"
   - Cliquer sur "Deploy latest commit"

2. **Ou via Render CLI:**
```bash
render deploy --service votre-service-id
```

---

## ✅ Étape 4: Vérifier la Configuration

### Vérifier les Logs

1. **Dans le Dashboard Render:**
   - Cliquer sur "Logs"
   - Chercher le message: "✅ Cache Upstash initialisé"

### Vérifier via l'API

```bash
# Tester l'endpoint health
curl https://top-modele-train-api.onrender.com/health

# Tester une prédiction
curl -X POST https://top-modele-train-api.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "team_home": "Real Madrid",
    "team_away": "Barcelona",
    "league": "FC 25. Champions League"
  }'
```

### Vérifier le Cache

```bash
# Nettoyer le cache
curl -X POST https://top-modele-train-api.onrender.com/clear-cache

# Réponse attendue:
# {"status": "success", "message": "Cache nettoyé"}
```

---

## 🔒 Sécurité

### Important

- **Ne jamais commiter les tokens dans le code**
- **Utiliser toujours les variables d'environnement**
- **Les tokens sont sensibles, ne les partagez pas**

### Bonnes Pratiques

- Les variables d'environnement sont chiffrées sur Render
- Elles ne sont visibles que par les membres de l'équipe
- Elles sont injectées automatiquement dans le conteneur

---

## 🐛 Dépannage

### Problème: Cache non initialisé

**Symptôme:** Message "⚠️ Cache Upstash non disponible" dans les logs

**Solutions:**
1. Vérifier que les variables d'environnement sont correctement définies
2. Vérifier que l'URL Upstash est correcte
3. Vérifier que le token Upstash est valide
4. Redéployer le service

### Problème: Erreur de connexion

**Symptôme:** Erreur de connexion à Upstash

**Solutions:**
1. Vérifier que l'URL Upstash est accessible
2. Vérifier que le token n'a pas expiré
3. Vérifier les quotas Upstash

### Problème: Variables non prises en compte

**Symptôme:** Les variables ne semblent pas être utilisées

**Solutions:**
1. Redéployer le service après avoir ajouté les variables
2. Vérifier l'orthographe des noms de variables
3. Vérifier qu'il n'y a pas d'espaces dans les valeurs

---

## 📊 Variables d'Environnement Requises

| Variable | Valeur | Description |
|----------|--------|-------------|
| `UPSTASH_REDIS_REST_URL` | `https://beloved-grouper-148747.upstash.io` | URL de votre instance Upstash Redis |
| `UPSTASH_REDIS_REST_TOKEN` | `gQAAAAAAAkULAAIgcDE5ZmU1NTg3ZTAxMjE0OWQzOWUzN2U4NDM3ZTNmZmI1ZA` | Token d'authentification Upstash |

---

## 🎯 Résumé

1. **Accéder au Dashboard Render**
2. **Ajouter UPSTASH_REDIS_REST_URL**
3. **Ajouter UPSTASH_REDIS_REST_TOKEN**
4. **Redéployer le service**
5. **Vérifier les logs**

Une fois configuré, le cache Upstash sera automatiquement utilisé par l'API en production.

---

**Document généré par SOLITAIRE HACK**  
*Date: 15 Juin 2026 à 2h35 UTC*  
*Version: 1.0*  
*Tous droits réservés*
