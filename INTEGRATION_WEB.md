# FIFA Virtual Prediction API - Guide d'Intégration Web

## 🌐 Intégration pour Applications Web

Ce guide fournit les instructions pour intégrer l'API FIFA Virtual Prediction dans vos applications web (JavaScript, React, Vue, Angular).

---

## 🚀 Configuration de Base

### URL de l'API
- **Production:** `https://top-modele-train-api-vmp.onrender.com`
- **Local:** `http://localhost:8000`

### Headers requis
```json
{
  "Content-Type": "application/json"
}
```

---

## 📝 JavaScript Vanilla

### Exemple de code

```javascript
class FIFAPredictionService {
  constructor(baseURL = 'https://top-modele-train-api-vmp.onrender.com') {
    this.baseURL = baseURL;
  }

  async predictMatch(teamHome, teamAway, league) {
    try {
      const response = await fetch(`${this.baseURL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          team_home: teamHome,
          team_away: teamAway,
          league: league
        })
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur de prédiction:', error);
      throw error;
    }
  }

  async getHealth() {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return await response.json();
    } catch (error) {
      console.error('Erreur de santé:', error);
      throw error;
    }
  }

  async getFamilies() {
    try {
      const response = await fetch(`${this.baseURL}/families`);
      return await response.json();
    } catch (error) {
      console.error('Erreur de récupération des familles:', error);
      throw error;
    }
  }

  async getLeagues() {
    try {
      const response = await fetch(`${this.baseURL}/leagues`);
      return await response.json();
    } catch (error) {
      console.error('Erreur de récupération des ligues:', error);
      throw error;
    }
  }
}

// Utilisation
const service = new FIFAPredictionService();

// Exemple 1: Prédiction simple
service.predictMatch('Arsenal', 'Lille OSC', 'FC 25. Champions League')
  .then(data => {
    console.log('Match:', data.match);
    console.log('Score exact:', data.predictions.exact_score.prediction);
    console.log('1X2:', data.predictions['1x2']);
  })
  .catch(error => {
    console.error('Erreur:', error);
  });

// Exemple 2: Vérification de santé
service.getHealth()
  .then(data => {
    console.log('Statut:', data.status);
    console.log('Modèles chargés:', data.models_loaded);
  });

// Exemple 3: Récupération des ligues
service.getLeagues()
  .then(data => {
    console.log('Ligues disponibles:', data.leagues);
  });
```

---

## ⚛️ React

### Installation
```bash
npm install axios
```

### Composant de prédiction

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BASE_URL = 'https://top-modele-train-api-vmp.onrender.com';

const FIFAPredictionService = {
  predictMatch: async (teamHome, teamAway, league) => {
    const response = await axios.post(`${BASE_URL}/predict`, {
      team_home: teamHome,
      team_away: teamAway,
      league: league
    });
    return response.data;
  },

  getHealth: async () => {
    const response = await axios.get(`${BASE_URL}/health`);
    return response.data;
  },

  getFamilies: async () => {
    const response = await axios.get(`${BASE_URL}/families`);
    return response.data;
  },

  getLeagues: async () => {
    const response = await axios.get(`${BASE_URL}/leagues`);
    return response.data;
  }
};

const PredictionComponent = () => {
  const [teamHome, setTeamHome] = useState('Arsenal');
  const [teamAway, setTeamAway] = useState('Lille OSC');
  const [league, setLeague] = useState('FC 25. Champions League');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [leagues, setLeagues] = useState([]);

  useEffect(() => {
    // Charger les ligues au montage
    FIFAPredictionService.getLeagues()
      .then(data => setLeagues(data.leagues))
      .catch(err => console.error('Erreur de chargement des ligues:', err));
  }, []);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const result = await FIFAPredictionService.predictMatch(teamHome, teamAway, league);
      setPrediction(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prediction-container">
      <h2>Prédiction FIFA</h2>
      
      <div className="form-group">
        <label>Équipe domicile:</label>
        <input
          type="text"
          value={teamHome}
          onChange={(e) => setTeamHome(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>Équipe extérieur:</label>
        <input
          type="text"
          value={teamAway}
          onChange={(e) => setTeamAway(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label>Ligue:</label>
        <select
          value={league}
          onChange={(e) => setLeague(e.target.value)}
        >
          {leagues.map((league) => (
            <option key={league} value={league}>{league}</option>
          ))}
        </select>
      </div>

      <button onClick={handlePredict} disabled={loading}>
        {loading ? 'Prédiction en cours...' : 'Prédire'}
      </button>

      {error && <div className="error">{error}</div>}

      {prediction && (
        <div className="prediction-result">
          <h3>Résultat de la prédiction</h3>
          <p><strong>Match:</strong> {prediction.match}</p>
          <p><strong>Ligue:</strong> {prediction.league}</p>
          <p><strong>Famille:</strong> {prediction.family}</p>
          
          <h4>Prédictions</h4>
          <p><strong>Score exact:</strong> {prediction.predictions.exact_score.prediction}</p>
          <p><strong>1X2:</strong> 
            Home: {prediction.predictions['1x2'].home.toFixed(2)}, 
            Draw: {prediction.predictions['1x2'].draw.toFixed(2)}, 
            Away: {prediction.predictions['1x2'].away.toFixed(2)}
          </p>
          <p><strong>Total buts:</strong> {prediction.predictions.total_goals.predicted}</p>
          <p><strong>Parité:</strong> 
            Pair: {prediction.predictions.parity.pair.toFixed(2)}, 
            Impair: {prediction.predictions.parity.impair.toFixed(2)}
          </p>

          {prediction.history && (
            <div className="history-section">
              <h4>Historique</h4>
              <div className="home-stats">
                <h5>Stats domicile:</h5>
                <p>Forme: {prediction.history.home_stats.form}</p>
                <p>Moyenne buts pour: {prediction.history.home_stats.avg_goals_for}</p>
                <p>Moyenne buts contre: {prediction.history.home_stats.avg_goals_against}</p>
              </div>
              <div className="away-stats">
                <h5>Stats extérieur:</h5>
                <p>Forme: {prediction.history.away_stats.form}</p>
                <p>Moyenne buts pour: {prediction.history.away_stats.avg_goals_for}</p>
                <p>Moyenne buts contre: {prediction.history.away_stats.avg_goals_against}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PredictionComponent;
```

### Hook personnalisé

```jsx
import { useState, useCallback } from 'react';
import axios from 'axios';

const BASE_URL = 'https://top-modele-train-api-vmp.onrender.com';

export const useFIFAPrediction = () => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const predictMatch = useCallback(async (teamHome, teamAway, league) => {
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const response = await axios.post(`${BASE_URL}/predict`, {
        team_home: teamHome,
        team_away: teamAway,
        league: league
      });
      setPrediction(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { prediction, loading, error, predictMatch };
};

// Utilisation
const PredictionComponent = () => {
  const { prediction, loading, error, predictMatch } = useFIFAPrediction();

  const handlePredict = () => {
    predictMatch('Arsenal', 'Lille OSC', 'FC 25. Champions League');
  };

  return (
    <div>
      <button onClick={handlePredict} disabled={loading}>
        Prédire
      </button>
      {loading && <p>Chargement...</p>}
      {error && <p>Erreur: {error}</p>}
      {prediction && (
        <div>
          <p>Score exact: {prediction.predictions.exact_score.prediction}</p>
        </div>
      )}
    </div>
  );
};
```

---

## 🟢 Vue.js

### Installation
```bash
npm install axios
```

### Composant de prédiction

```vue
<template>
  <div class="prediction-container">
    <h2>Prédiction FIFA</h2>
    
    <div class="form-group">
      <label>Équipe domicile:</label>
      <input v-model="teamHome" type="text" />
    </div>

    <div class="form-group">
      <label>Équipe extérieur:</label>
      <input v-model="teamAway" type="text" />
    </div>

    <div class="form-group">
      <label>Ligue:</label>
      <select v-model="league">
        <option v-for="l in leagues" :key="l" :value="l">{{ l }}</option>
      </select>
    </div>

    <button @click="handlePredict" :disabled="loading">
      {{ loading ? 'Prédiction en cours...' : 'Prédire' }}
    </button>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="prediction" class="prediction-result">
      <h3>Résultat de la prédiction</h3>
      <p><strong>Match:</strong> {{ prediction.match }}</p>
      <p><strong>Score exact:</strong> {{ prediction.predictions.exact_score.prediction }}</p>
      <p><strong>1X2:</strong> 
        Home: {{ prediction.predictions['1x2'].home.toFixed(2) }}, 
        Draw: {{ prediction.predictions['1x2'].draw.toFixed(2) }}, 
        Away: {{ prediction.predictions['1x2'].away.toFixed(2) }}
      </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

const BASE_URL = 'https://top-modele-train-api-vmp.onrender.com';

export default {
  name: 'PredictionComponent',
  data() {
    return {
      teamHome: 'Arsenal',
      teamAway: 'Lille OSC',
      league: 'FC 25. Champions League',
      prediction: null,
      loading: false,
      error: null,
      leagues: []
    };
  },
  async mounted() {
    try {
      const response = await axios.get(`${BASE_URL}/leagues`);
      this.leagues = response.data.leagues;
    } catch (error) {
      console.error('Erreur de chargement des ligues:', error);
    }
  },
  methods: {
    async handlePredict() {
      this.loading = true;
      this.error = null;
      this.prediction = null;

      try {
        const response = await axios.post(`${BASE_URL}/predict`, {
          team_home: this.teamHome,
          team_away: this.teamAway,
          league: this.league
        });
        this.prediction = response.data;
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.prediction-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.error {
  color: red;
  margin-top: 10px;
}

.prediction-result {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 5px;
}
</style>
```

---

## 🅰️ Angular

### Installation
```bash
npm install @angular/common@latest @angular/core@latest
```

### Service de prédiction

```typescript
// fifa-prediction.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class FIFAPredictionService {
  private baseURL = 'https://top-modele-train-api-vmp.onrender.com';
  private headers = new HttpHeaders({ 'Content-Type': 'application/json' });

  constructor(private http: HttpClient) {}

  predictMatch(teamHome: string, teamAway: string, league: string): Observable<any> {
    const body = {
      team_home: teamHome,
      team_away: teamAway,
      league: league
    };

    return this.http.post(`${this.baseURL}/predict`, body, { headers: this.headers })
      .pipe(catchError(this.handleError));
  }

  getHealth(): Observable<any> {
    return this.http.get(`${this.baseURL}/health`)
      .pipe(catchError(this.handleError));
  }

  getFamilies(): Observable<any> {
    return this.http.get(`${this.baseURL}/families`)
      .pipe(catchError(this.handleError));
  }

  getLeagues(): Observable<any> {
    return this.http.get(`${this.baseURL}/leagues`)
      .pipe(catchError(this.handleError));
  }

  private handleError(error: any) {
    console.error('Erreur API:', error);
    return throwError(() => error);
  }
}
```

### Composant de prédiction

```typescript
// prediction.component.ts
import { Component, OnInit } from '@angular/core';
import { FIFAPredictionService } from './fifa-prediction.service';

@Component({
  selector: 'app-prediction',
  templateUrl: './prediction.component.html',
  styleUrls: ['./prediction.component.css']
})
export class PredictionComponent implements OnInit {
  teamHome = 'Arsenal';
  teamAway = 'Lille OSC';
  league = 'FC 25. Champions League';
  prediction: any = null;
  loading = false;
  error: string | null = null;
  leagues: string[] = [];

  constructor(private fifaService: FIFAPredictionService) {}

  ngOnInit() {
    this.loadLeagues();
  }

  loadLeagues() {
    this.fifaService.getLeagues().subscribe({
      next: (data) => {
        this.leagues = data.leagues;
      },
      error: (error) => {
        console.error('Erreur de chargement des ligues:', error);
      }
    });
  }

  handlePredict() {
    this.loading = true;
    this.error = null;
    this.prediction = null;

    this.fifaService.predictMatch(this.teamHome, this.teamAway, this.league).subscribe({
      next: (data) => {
        this.prediction = data;
        this.loading = false;
      },
      error: (error) => {
        this.error = error.message;
        this.loading = false;
      }
    });
  }
}
```

### Template

```html
<!-- prediction.component.html -->
<div class="prediction-container">
  <h2>Prédiction FIFA</h2>
  
  <div class="form-group">
    <label>Équipe domicile:</label>
    <input [(ngModel)]="teamHome" type="text" />
  </div>

  <div class="form-group">
    <label>Équipe extérieur:</label>
    <input [(ngModel)]="teamAway" type="text" />
  </div>

  <div class="form-group">
    <label>Ligue:</label>
    <select [(ngModel)]="league">
      <option *ngFor="let l of leagues" [value]="l">{{ l }}</option>
    </select>
  </div>

  <button (click)="handlePredict()" [disabled]="loading">
    {{ loading ? 'Prédiction en cours...' : 'Prédire' }}
  </button>

  <div *ngIf="error" class="error">{{ error }}</div>

  <div *ngIf="prediction" class="prediction-result">
    <h3>Résultat de la prédiction</h3>
    <p><strong>Match:</strong> {{ prediction.match }}</p>
    <p><strong>Score exact:</strong> {{ prediction.predictions.exact_score.prediction }}</p>
    <p><strong>1X2:</strong> 
      Home: {{ prediction.predictions['1x2'].home | number:'1.2-2' }}, 
      Draw: {{ prediction.predictions['1x2'].draw | number:'1.2-2' }}, 
      Away: {{ prediction.predictions['1x2'].away | number:'1.2-2' }}
    </p>
  </div>
</div>
```

---

## 🔧 Bonnes Pratiques

### Gestion des erreurs
- Toujours gérer les erreurs réseau
- Afficher des messages d'erreur clairs aux utilisateurs
- Implémenter des retries pour les requêtes échouées

### Performance
- Utiliser le cache pour les requêtes fréquentes
- Implémenter le lazy loading pour les composants
- Optimiser les images et assets

### Sécurité
- Valider les entrées utilisateur
- Utiliser HTTPS pour toutes les requêtes
- Ne jamais exposer de clés API dans le code client

### UX
- Afficher des indicateurs de chargement
- Implémenter des animations fluides
- Rendre l'interface responsive

---

## 📞 Support

Pour toute question sur l'intégration web, contactez l'équipe technique ou consultez le guide d'intégration principal.
