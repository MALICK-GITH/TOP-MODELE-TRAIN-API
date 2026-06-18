# FIFA Virtual Prediction API - Guide d'Intégration Mobile

## 📱 Intégration pour Applications Mobiles

Ce guide fournit les instructions pour intégrer l'API FIFA Virtual Prediction dans vos applications mobiles (iOS, Android, React Native, Flutter).

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

## 📲 iOS (Swift)

### Installation
Aucune dépendance externe requise - utilisez `URLSession` natif.

### Exemple de code

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

## 🤖 Android (Kotlin)

### Installation
Aucune dépendance externe requise - utilisez `OkHttp` ou `Retrofit`.

### Exemple avec OkHttp

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

## ⚛️ React Native

### Installation
```bash
npm install axios
```

### Exemple de code

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

## 🦋 Flutter

### Installation
Ajoutez `http` à votre `pubspec.yaml`:
```yaml
dependencies:
  http: ^1.1.0
  flutter:
    sdk: flutter
```

### Exemple de code

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

## 🔧 Bonnes Pratiques

### Gestion des erreurs
- Toujours gérer les erreurs réseau
- Implémenter des timeouts appropriés
- Afficher des messages d'erreur clairs aux utilisateurs

### Cache
- Implémenter un cache local pour les prédictions fréquentes
- Utiliser SharedPreferences (Android) ou UserDefaults (iOS)

### Performance
- Utiliser des requêtes asynchrones
- Éviter de bloquer le thread principal
- Implémenter un indicateur de chargement

### Sécurité
- Ne jamais stocker de clés API dans le code client
- Utiliser des variables d'environnement pour la configuration
- Valider les entrées utilisateur

---

## 📞 Support

Pour toute question sur l'intégration mobile, contactez l'équipe technique ou consultez le guide d'intégration principal.
