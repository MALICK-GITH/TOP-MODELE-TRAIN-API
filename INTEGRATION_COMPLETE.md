# FIFA Virtual Prediction API - Guide d'Intégration Complet

Ce guide fournit les instructions complètes pour intégrer l'API FIFA Virtual Prediction dans vos applications mobiles, web et backend.

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

## 📱 Intégration Mobile

### iOS (Swift)

#### Installation
Aucune dépendance externe requise - utilisez `URLSession` natif.

#### Exemple de code

```swift
import Foundation

class FIFAPredictionService {
    private let baseURL = "https://top-modele-train-api-vmp.onrender.com"
    
    struct PredictionRequest: Codable {
        let team_home: String
        let team_away: String
        let league: String
    }
    
    struct PredictionResponse: Codable {
        let match: String
        let league: String
        let family: String
        let predictions: Predictions
        let history: History?
    }
    
    struct Predictions: Codable {
        let `1x2`: OneXTwo
        let total_goals: TotalGoals
        let handicap: [String: Handicap]
        let parity: Parity
        let exact_score: ExactScore
    }
    
    struct OneXTwo: Codable {
        let home: Double
        let draw: Double
        let away: Double
    }
    
    struct TotalGoals: Codable {
        let predicted: Double
        let over_under: [String: OverUnder]
    }
    
    struct OverUnder: Codable {
        let over: Double
        let under: Double
    }
    
    struct Handicap: Codable {
        let home: Double
        let draw: Double
        let away: Double
    }
    
    struct Parity: Codable {
        let pair: Double
        let impair: Double
    }
    
    struct ExactScore: Codable {
        let prediction: String
    }
    
    struct History: Codable {
        let home_last_matches: [Match]
        let home_stats: Stats
        let away_last_matches: [Match]
        let away_stats: Stats
        let head_to_head: [Match]
    }
    
    struct Match: Codable {
        let date: String
        let opponent: String
        let is_home: Bool
        let score_home: Int
        let score_away: Int
        let result: String
    }
    
    struct Stats: Codable {
        let avg_goals_for: Double
        let avg_goals_against: Double
        let avg_goal_difference: Double
        let form: String
        let wins: Int
        let draws: Int
        let losses: Int
    }
    
    func predictMatch(teamHome: String, teamAway: String, league: String, completion: @escaping (Result<PredictionResponse, Error>) -> Void) {
        guard let url = URL(string: "\(baseURL)/predict") else {
            completion(.failure(NSError(domain: "Invalid URL", code: -1, userInfo: nil)))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let requestBody = PredictionRequest(team_home: teamHome, team_away: teamAway, league: league)
        
        do {
            request.httpBody = try JSONEncoder().encode(requestBody)
        } catch {
            completion(.failure(error))
            return
        }
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: -1, userInfo: nil)))
                return
            }
            
            do {
                let decoder = JSONDecoder()
                let predictionResponse = try decoder.decode(PredictionResponse.self, from: data)
                completion(.success(predictionResponse))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
}

// Utilisation
let service = FIFAPredictionService()
service.predictMatch(teamHome: "Arsenal", teamAway: "Lille OSC", league: "FC 25. Champions League") { result in
    switch result {
    case .success(let response):
        print("Match: \(response.match)")
        print("Score exact: \(response.predictions.exact_score.prediction)")
        print("1X2: Home=\(response.predictions.`1x2`.home), Draw=\(response.predictions.`1x2`.draw), Away=\(response.predictions.`1x2`.away)")
    case .failure(let error):
        print("Erreur: \(error.localizedDescription)")
    }
}
```

---

### Android (Kotlin)

#### Installation
Aucune dépendance externe requise - utilisez `OkHttp` ou `Retrofit`.

#### Exemple avec OkHttp

```kotlin
import okhttp3.*
import org.json.JSONObject
import java.io.IOException

class FIFAPredictionService(private val context: Context) {
    private val client = OkHttpClient()
    private val baseURL = "https://top-modele-train-api-vmp.onrender.com"
    
    data class PredictionRequest(
        val team_home: String,
        val team_away: String,
        val league: String
    )
    
    data class PredictionResponse(
        val match: String,
        val league: String,
        val family: String,
        val predictions: Predictions,
        val history: History?
    )
    
    fun predictMatch(
        teamHome: String,
        teamAway: String,
        league: String,
        callback: (Result<PredictionResponse>) -> Unit
    ) {
        val url = "$baseURL/predict"
        val requestBody = PredictionRequest(teamHome, teamAway, league)
        val json = JSONObject(Gson().toJson(requestBody))
        
        val body = json.toString().toRequestBody("application/json".toMediaType())
        val request = Request.Builder()
            .url(url)
            .post(body)
            .build()
        
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                callback(Result.failure(e))
            }
            
            override fun onResponse(call: Call, response: Response) {
                val responseBody = response.body?.string()
                if (responseBody != null) {
                    try {
                        val gson = Gson()
                        val predictionResponse = gson.fromJson(responseBody, PredictionResponse::class.java)
                        callback(Result.success(predictionResponse))
                    } catch (e: Exception) {
                        callback(Result.failure(e))
                    }
                }
            }
        })
    }
}

// Utilisation
val service = FIFAPredictionService(context)
service.predictMatch("Arsenal", "Lille OSC", "FC 25. Champions League") { result ->
    result.onSuccess { response ->
        Log.d("FIFA", "Match: ${response.match}")
        Log.d("FIFA", "Score exact: ${response.predictions.exact_score.prediction}")
    }.onFailure { error ->
        Log.e("FIFA", "Erreur: ${error.message}")
    }
}
```

---

### React Native

#### Installation
```bash
npm install axios
```

#### Exemple de code

```javascript
import axios from 'axios';

const BASE_URL = 'https://top-modele-train-api-vmp.onrender.com';

class FIFAPredictionService {
  static async predictMatch(teamHome, teamAway, league) {
    try {
      const response = await axios.post(`${BASE_URL}/predict`, {
        team_home: teamHome,
        team_away: teamAway,
        league: league
      });
      return response.data;
    } catch (error) {
      throw new Error(`Erreur de prédiction: ${error.message}`);
    }
  }
}

// Utilisation dans un composant React Native
import React, { useState } from 'react';
import { View, Text, Button, ActivityIndicator } from 'react-native';

const PredictionScreen = () => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await FIFAPredictionService.predictMatch(
        'Arsenal',
        'Lille OSC',
        'FC 25. Champions League'
      );
      setPrediction(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <Button title="Prédire le match" onPress={handlePredict} />
      
      {loading && <ActivityIndicator size="large" />}
      
      {error && <Text style={{ color: 'red' }}>{error}</Text>}
      
      {prediction && (
        <View>
          <Text>Match: {prediction.match}</Text>
          <Text>Score exact: {prediction.predictions.exact_score.prediction}</Text>
          <Text>1X2: Home={prediction.predictions['1x2'].home}, Draw={prediction.predictions['1x2'].draw}, Away={prediction.predictions['1x2'].away}</Text>
        </View>
      )}
    </View>
  );
};

export default PredictionScreen;
```

---

### Flutter

#### Installation
Ajoutez `http` à votre `pubspec.yaml`:
```yaml
dependencies:
  http: ^1.1.0
  flutter:
    sdk: flutter
```

#### Exemple de code

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class FIFAPredictionService {
  static const String baseURL = 'https://top-modele-train-api-vmp.onrender.com';

  static Future<Map<String, dynamic>> predictMatch(
      String teamHome, String teamAway, String league) async {
    final url = Uri.parse('$baseURL/predict');
    final headers = {'Content-Type': 'application/json'};
    final body = jsonEncode({
      'team_home': teamHome,
      'team_away': teamAway,
      'league': league
    });

    try {
      final response = await http.post(url, headers: headers, body: body);
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Erreur de prédiction: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erreur de connexion: $e');
    }
  }
}

// Utilisation dans un widget Flutter
import 'package:flutter/material.dart';

class PredictionScreen extends StatefulWidget {
  @override
  _PredictionScreenState createState() => _PredictionScreenState();
}

class _PredictionScreenState extends State<PredictionScreen> {
  Map<String, dynamic>? prediction;
  bool loading = false;
  String? error;

  Future<void> handlePredict() async {
    setState(() {
      loading = true;
      error = null;
    });

    try {
      final result = await FIFAPredictionService.predictMatch(
        'Arsenal',
        'Lille OSC',
        'FC 25. Champions League'
      );
      setState(() {
        prediction = result;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
      });
    } finally {
      setState(() {
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Prédiction FIFA')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            ElevatedButton(
              onPressed: handlePredict,
              child: Text('Prédire le match'),
            ),
            if (loading) CircularProgressIndicator(),
            if (error != null) Text(error!, style: TextStyle(color: Colors.red)),
            if (prediction != null)
              Column(
                children: [
                  Text('Match: ${prediction!['match']}'),
                  Text('Score exact: ${prediction!['predictions']['exact_score']['prediction']}'),
                  Text('1X2: Home=${prediction!['predictions']['1x2']['home']}, Draw=${prediction!['predictions']['1x2']['draw']}, Away=${prediction!['predictions']['1x2']['away']}'),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
```

---

## 🌐 Intégration Web

### JavaScript Vanilla

#### Exemple de code

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

### React

#### Installation
```bash
npm install axios
```

#### Composant de prédiction

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

#### Hook personnalisé

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

### Vue.js

#### Installation
```bash
npm install axios
```

#### Composant de prédiction

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

### Angular

#### Installation
```bash
npm install @angular/common@latest @angular/core@latest
```

#### Service de prédiction

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

#### Composant de prédiction

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

#### Template

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

## 🔧 Intégration Backend

### Node.js

#### Installation
```bash
npm install axios
```

#### Exemple de code

```javascript
const axios = require('axios');

class FIFAPredictionService {
  constructor(baseURL = 'https://top-modele-train-api-vmp.onrender.com') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  async predictMatch(teamHome, teamAway, league) {
    try {
      const response = await this.client.post('/predict', {
        team_home: teamHome,
        team_away: teamAway,
        league: league
      });
      return response.data;
    } catch (error) {
      console.error('Erreur de prédiction:', error.message);
      throw error;
    }
  }

  async getHealth() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('Erreur de santé:', error.message);
      throw error;
    }
  }

  async getFamilies() {
    try {
      const response = await this.client.get('/families');
      return response.data;
    } catch (error) {
      console.error('Erreur de récupération des familles:', error.message);
      throw error;
    }
  }

  async getLeagues() {
    try {
      const response = await this.client.get('/leagues');
      return response.data;
    } catch (error) {
      console.error('Erreur de récupération des ligues:', error.message);
      throw error;
    }
  }

  async batchPredict(matches) {
    try {
      const predictions = await Promise.all(
        matches.map(match => this.predictMatch(match.teamHome, match.teamAway, match.league))
      );
      return predictions;
    } catch (error) {
      console.error('Erreur de prédiction batch:', error.message);
      throw error;
    }
  }
}

// Utilisation
const service = new FIFAPredictionService();

// Prédiction simple
service.predictMatch('Arsenal', 'Lille OSC', 'FC 25. Champions League')
  .then(data => console.log('Prédiction:', data))
  .catch(error => console.error('Erreur:', error));

// Prédiction batch
const matches = [
  { teamHome: 'Arsenal', teamAway: 'Lille OSC', league: 'FC 25. Champions League' },
  { teamHome: 'Barcelone', teamAway: 'Real Madrid', league: 'FC 25. Championnat d\'Espagne' }
];

service.batchPredict(matches)
  .then(predictions => console.log('Prédictions batch:', predictions))
  .catch(error => console.error('Erreur:', error));
```

#### Express.js Middleware

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const fifaService = new FIFAPredictionService();

// Endpoint proxy pour les prédictions
app.post('/api/predict', async (req, res) => {
  try {
    const { team_home, team_away, league } = req.body;
    
    if (!team_home || !team_away || !league) {
      return res.status(400).json({ error: 'Paramètres manquants' });
    }

    const prediction = await fifaService.predictMatch(team_home, team_away, league);
    res.json(prediction);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Endpoint pour vérifier la santé
app.get('/api/health', async (req, res) => {
  try {
    const health = await fifaService.getHealth();
    res.json(health);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Serveur proxy démarré sur le port 3000');
});
```

---

### Python

#### Installation
```bash
pip install requests
```

#### Exemple de code

```python
import requests
import asyncio
from typing import List, Dict, Optional

class FIFAPredictionService:
    def __init__(self, base_url: str = "https://top-modele-train-api-vmp.onrender.com"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        self.timeout = 10

    def predict_match(self, team_home: str, team_away: str, league: str) -> Dict:
        """Prédire un match"""
        try:
            url = f"{self.base_url}/predict"
            payload = {
                "team_home": team_home,
                "team_away": team_away,
                "league": league
            }
            response = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur de prédiction: {e}")
            raise

    def get_health(self) -> Dict:
        """Vérifier la santé de l'API"""
        try:
            url = f"{self.base_url}/health"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur de santé: {e}")
            raise

    def get_families(self) -> Dict:
        """Récupérer les familles"""
        try:
            url = f"{self.base_url}/families"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur de récupération des familles: {e}")
            raise

    def get_leagues(self) -> Dict:
        """Récupérer les ligues"""
        try:
            url = f"{self.base_url}/leagues"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur de récupération des ligues: {e}")
            raise

    def batch_predict(self, matches: List[Dict]) -> List[Dict]:
        """Prédire plusieurs matchs en batch"""
        predictions = []
        for match in matches:
            try:
                prediction = self.predict_match(
                    match["team_home"],
                    match["team_away"],
                    match["league"]
                )
                predictions.append(prediction)
            except Exception as e:
                print(f"Erreur pour le match {match}: {e}")
                predictions.append({"error": str(e)})
        return predictions

# Utilisation
service = FIFAPredictionService()

# Prédiction simple
try:
    prediction = service.predict_match("Arsenal", "Lille OSC", "FC 25. Champions League")
    print(f"Match: {prediction['match']}")
    print(f"Score exact: {prediction['predictions']['exact_score']['prediction']}")
except Exception as e:
    print(f"Erreur: {e}")

# Prédiction batch
matches = [
    {"team_home": "Arsenal", "team_away": "Lille OSC", "league": "FC 25. Champions League"},
    {"team_home": "Barcelone", "team_away": "Real Madrid", "league": "FC 25. Championnat d'Espagne"}
]

predictions = service.batch_predict(matches)
for i, pred in enumerate(predictions):
    print(f"Match {i+1}: {pred.get('match', pred.get('error'))}")
```

#### Flask Integration

```python
from flask import Flask, request, jsonify
from fifa_prediction_service import FIFAPredictionService

app = Flask(__name__)
fifa_service = FIFAPredictionService()

@app.route('/api/predict', methods=['POST'])
def predict():
    """Endpoint proxy pour les prédictions"""
    try:
        data = request.json
        team_home = data.get('team_home')
        team_away = data.get('team_away')
        league = data.get('league')
        
        if not all([team_home, team_away, league]):
            return jsonify({'error': 'Paramètres manquants'}), 400
        
        prediction = fifa_service.predict_match(team_home, team_away, league)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint pour vérifier la santé"""
    try:
        health = fifa_service.get_health()
        return jsonify(health)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-predict', methods=['POST'])
def batch_predict():
    """Endpoint pour les prédictions batch"""
    try:
        matches = request.json.get('matches', [])
        predictions = fifa_service.batch_predict(matches)
        return jsonify({'predictions': predictions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

#### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fifa_prediction_service import FIFAPredictionService

app = FastAPI()
fifa_service = FIFAPredictionService()

class PredictionRequest(BaseModel):
    team_home: str
    team_away: str
    league: str

class BatchPredictionRequest(BaseModel):
    matches: List[PredictionRequest]

@app.post("/api/predict")
async def predict(request: PredictionRequest):
    """Endpoint proxy pour les prédictions"""
    try:
        prediction = fifa_service.predict_match(
            request.team_home,
            request.team_away,
            request.league
        )
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    """Endpoint pour vérifier la santé"""
    try:
        health = fifa_service.get_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/batch-predict")
async def batch_predict(request: BatchPredictionRequest):
    """Endpoint pour les prédictions batch"""
    try:
        matches_data = [
            {
                "team_home": m.team_home,
                "team_away": m.team_away,
                "league": m.league
            }
            for m in request.matches
        ]
        predictions = fifa_service.batch_predict(matches_data)
        return {"predictions": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

### PHP

#### Exemple de code

```php
<?php

class FIFAPredictionService {
    private $baseURL;
    private $timeout;

    public function __construct($baseURL = 'https://top-modele-train-api-vmp.onrender.com', $timeout = 10) {
        $this->baseURL = $baseURL;
        $this->timeout = $timeout;
    }

    public function predictMatch($teamHome, $teamAway, $league) {
        $url = $this->baseURL . '/predict';
        $data = [
            'team_home' => $teamHome,
            'team_away' => $teamAway,
            'league' => $league
        ];

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            throw new Exception("Erreur HTTP: $httpCode");
        }

        return json_decode($response, true);
    }

    public function getHealth() {
        $url = $this->baseURL . '/health';

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            throw new Exception("Erreur HTTP: $httpCode");
        }

        return json_decode($response, true);
    }

    public function getLeagues() {
        $url = $this->baseURL . '/leagues';

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200) {
            throw new Exception("Erreur HTTP: $httpCode");
        }

        return json_decode($response, true);
    }
}

// Utilisation
$service = new FIFAPredictionService();

try {
    $prediction = $service->predictMatch('Arsenal', 'Lille OSC', 'FC 25. Champions League');
    echo "Match: " . $prediction['match'] . "\n";
    echo "Score exact: " . $prediction['predictions']['exact_score']['prediction'] . "\n";
} catch (Exception $e) {
    echo "Erreur: " . $e->getMessage() . "\n";
}
```

#### Laravel Integration

```php
<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;

class FIFAPredictionService {
    private $baseURL;

    public function __construct() {
        $this->baseURL = config('services.fifa.base_url', 'https://top-modele-train-api-vmp.onrender.com');
    }

    public function predictMatch($teamHome, $teamAway, $league) {
        $response = Http::timeout(10)->post($this->baseURL . '/predict', [
            'team_home' => $teamHome,
            'team_away' => $teamAway,
            'league' => $league
        ]);

        if (!$response->successful()) {
            throw new \Exception("Erreur de prédiction: " . $response->status());
        }

        return $response->json();
    }

    public function getHealth() {
        $response = Http::timeout(10)->get($this->baseURL . '/health');

        if (!$response->successful()) {
            throw new \Exception("Erreur de santé: " . $response->status());
        }

        return $response->json();
    }

    public function getLeagues() {
        $response = Http::timeout(10)->get($this->baseURL . '/leagues');

        if (!$response->successful()) {
            throw new \Exception("Erreur de récupération des ligues: " . $response->status());
        }

        return $response->json();
    }
}

// Controller
namespace App\Http\Controllers;

use App\Services\FIFAPredictionService;
use Illuminate\Http\Request;

class PredictionController extends Controller {
    private $fifaService;

    public function __construct(FIFAPredictionService $fifaService) {
        $this->fifaService = $fifaService;
    }

    public function predict(Request $request) {
        $validated = $request->validate([
            'team_home' => 'required|string',
            'team_away' => 'required|string',
            'league' => 'required|string'
        ]);

        try {
            $prediction = $this->fifaService->predictMatch(
                $validated['team_home'],
                $validated['team_away'],
                $validated['league']
            );
            return response()->json($prediction);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function health() {
        try {
            $health = $this->fifaService->getHealth();
            return response()->json($health);
        } catch (\Exception $e) {
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }
}
```

---

### Java

#### Installation (Maven)
```xml
<dependency>
    <groupId>com.squareup.okhttp3</groupId>
    <artifactId>okhttp</artifactId>
    <version>4.12.0</version>
</dependency>
<dependency>
    <groupId>com.google.code.gson</groupId>
    <artifactId>gson</artifactId>
    <version>2.10.1</version>
</dependency>
```

#### Exemple de code

```java
import okhttp3.*;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

public class FIFAPredictionService {
    private final OkHttpClient client;
    private final Gson gson;
    private final String baseURL;

    public FIFAPredictionService(String baseURL) {
        this.baseURL = baseURL;
        this.client = new OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(10, TimeUnit.SECONDS)
            .build();
        this.gson = new Gson();
    }

    public JsonObject predictMatch(String teamHome, String teamAway, String league) throws IOException {
        String url = baseURL + "/predict";
        
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("team_home", teamHome);
        requestBody.addProperty("team_away", teamAway);
        requestBody.addProperty("league", league);

        RequestBody body = RequestBody.create(
            requestBody.toString(),
            MediaType.parse("application/json")
        );

        Request request = new Request.Builder()
            .url(url)
            .post(body)
            .addHeader("Content-Type", "application/json")
            .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Erreur HTTP: " + response.code());
            }
            
            String responseData = response.body().string();
            return gson.fromJson(responseData, JsonObject.class);
        }
    }

    public JsonObject getHealth() throws IOException {
        String url = baseURL + "/health";
        
        Request request = new Request.Builder()
            .url(url)
            .get()
            .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Erreur HTTP: " + response.code());
            }
            
            String responseData = response.body().string();
            return gson.fromJson(responseData, JsonObject.class);
        }
    }
}

// Utilisation
public class Main {
    public static void main(String[] args) {
        FIFAPredictionService service = new FIFAPredictionService("https://top-modele-train-api-vmp.onrender.com");
        
        try {
            JsonObject prediction = service.predictMatch("Arsenal", "Lille OSC", "FC 25. Champions League");
            System.out.println("Match: " + prediction.get("match").getAsString());
            System.out.println("Score exact: " + prediction.getAsJsonObject("predictions")
                .getAsJsonObject("exact_score").get("prediction").getAsString());
        } catch (IOException e) {
            System.err.println("Erreur: " + e.getMessage());
        }
    }
}
```

---

### Go

#### Exemple de code

```go
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"
)

type FIFAPredictionService struct {
	BaseURL string
	Client  *http.Client
}

type PredictionRequest struct {
	TeamHome string `json:"team_home"`
	TeamAway string `json:"team_away"`
	League   string `json:"league"`
}

type PredictionResponse struct {
	Match       string       `json:"match"`
	League      string       `json:"league"`
	Family      string       `json:"family"`
	Predictions Predictions  `json:"predictions"`
	History     *History     `json:"history"`
}

type Predictions struct {
	OneXTwo     OneXTwo     `json:"1x2"`
	TotalGoals  TotalGoals  `json:"total_goals"`
	Handicap    map[string]Handicap `json:"handicap"`
	Parity      Parity      `json:"parity"`
	ExactScore  ExactScore  `json:"exact_score"`
}

type OneXTwo struct {
	Home float64 `json:"home"`
	Draw float64 `json:"draw"`
	Away float64 `json:"away"`
}

type ExactScore struct {
	Prediction string `json:"prediction"`
}

func NewFIFAPredictionService(baseURL string) *FIFAPredictionService {
	return &FIFAPredictionService{
		BaseURL: baseURL,
		Client: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

func (s *FIFAPredictionService) PredictMatch(teamHome, teamAway, league string) (*PredictionResponse, error) {
	url := s.BaseURL + "/predict"
	
	request := PredictionRequest{
		TeamHome: teamHome,
		TeamAway: teamAway,
		League:   league,
	}
	
	jsonData, err := json.Marshal(request)
	if err != nil {
		return nil, fmt.Errorf("erreur de marshalling: %v", err)
	}
	
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("erreur de création de requête: %v", err)
	}
	
	req.Header.Set("Content-Type", "application/json")
	
	resp, err := s.Client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("erreur de requête: %v", err)
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		body, _ := ioutil.ReadAll(resp.Body)
		return nil, fmt.Errorf("erreur HTTP %d: %s", resp.StatusCode, string(body))
	}
	
	var prediction PredictionResponse
	if err := json.NewDecoder(resp.Body).Decode(&prediction); err != nil {
		return nil, fmt.Errorf("erreur de décodage: %v", err)
	}
	
	return &prediction, nil
}

func (s *FIFAPredictionService) GetHealth() (map[string]interface{}, error) {
	url := s.BaseURL + "/health"
	
	resp, err := s.Client.Get(url)
	if err != nil {
		return nil, fmt.Errorf("erreur de requête: %v", err)
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("erreur HTTP: %d", resp.StatusCode)
	}
	
	var health map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&health); err != nil {
		return nil, fmt.Errorf("erreur de décodage: %v", err)
	}
	
	return health, nil
}

func main() {
	service := NewFIFAPredictionService("https://top-modele-train-api-vmp.onrender.com")
	
	prediction, err := service.PredictMatch("Arsenal", "Lille OSC", "FC 25. Champions League")
	if err != nil {
		fmt.Printf("Erreur: %v\n", err)
		return
	}
	
	fmt.Printf("Match: %s\n", prediction.Match)
	fmt.Printf("Score exact: %s\n", prediction.Predictions.ExactScore.Prediction)
}
```

---

## 🔧 Bonnes Pratiques

### Gestion des erreurs
- Toujours gérer les erreurs réseau
- Implémenter des retries avec backoff exponentiel
- Logger les erreurs pour le débogage
- Afficher des messages d'erreur clairs aux utilisateurs

### Performance
- Utiliser des connexions persistantes
- Implémenter le cache pour les requêtes fréquentes
- Utiliser des timeouts appropriés
- Utiliser le cache local pour les prédictions fréquentes (mobile)
- Utiliser des requêtes asynchrones
- Éviter de bloquer le thread principal

### Sécurité
- Valider les entrées utilisateur
- Utiliser HTTPS pour toutes les requêtes
- Ne jamais exposer de clés API dans le code
- Ne jamais stocker de clés API dans le code client
- Utiliser des variables d'environnement pour la configuration

### UX (Mobile/Web)
- Afficher des indicateurs de chargement
- Implémenter des animations fluides
- Rendre l'interface responsive
- Implémenter un indicateur de chargement

### Monitoring (Backend)
- Surveiller les temps de réponse
- Tracker les taux d'erreur
- Implémenter des alertes pour les pannes

---

## 📞 Support

Pour toute question sur l'intégration, contactez l'équipe technique ou consultez le guide d'intégration principal (INTEGRATION_GUIDE.md).

**Repository GitHub :** https://github.com/MALICK-GITH/TOP-MODELE-TRAIN-API
