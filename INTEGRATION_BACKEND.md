# FIFA Virtual Prediction API - Guide d'Intégration Backend

## 🔧 Intégration pour Applications Backend

Ce guide fournit les instructions pour intégrer l'API FIFA Virtual Prediction dans vos applications backend (Node.js, Python, PHP, Java, Go).

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

## 🟢 Node.js

### Installation
```bash
npm install axios
```

### Exemple de code

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

### Express.js Middleware

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

## 🐍 Python

### Installation
```bash
pip install requests
```

### Exemple de code

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

### Flask Integration

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

### FastAPI Integration

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

## 🐘 PHP

### Exemple de code

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

### Laravel Integration

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

## ☕ Java

### Installation (Maven)
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

### Exemple de code

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

## 🐹 Go

### Exemple de code

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

### Performance
- Utiliser des connexions persistantes
- Implémenter le cache pour les requêtes fréquentes
- Utiliser des timeouts appropriés

### Sécurité
- Valider les entrées utilisateur
- Utiliser HTTPS pour toutes les requêtes
- Ne jamais exposer de clés API dans le code

### Monitoring
- Surveiller les temps de réponse
- Tracker les taux d'erreur
- Implémenter des alertes pour les pannes

---

## 📞 Support

Pour toute question sur l'intégration backend, contactez l'équipe technique ou consultez le guide d'intégration principal.
