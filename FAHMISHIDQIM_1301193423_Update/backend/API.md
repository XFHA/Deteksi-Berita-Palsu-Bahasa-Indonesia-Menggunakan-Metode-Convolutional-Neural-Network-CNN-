# API Documentation

## Base URL
```
http://localhost:5000
```

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check server status and model availability

**Response:**
```json
{
  "status": "online",
  "model_loaded": true,
  "vectorizer_loaded": true,
  "detection_method": "CNN + TF-IDF"
}
```

**Status Codes:**
- `200 OK`: Server is running

---

### 2. Analyze Text

**Endpoint:** `POST /analyze`

**Description:** Analyze single news text for fake news detection

**Request Body:**
```json
{
  "text": "VIRAL!!! HEBOH! Pemerintah akan melarang semua orang keluar rumah!"
}
```

**Parameters:**
- `text` (string, required): News text to analyze (minimum 10 characters)

**Response:**
```json
{
  "prediction": "fake",
  "confidence": 0.8523,
  "fake_score": 85.23,
  "real_score": 14.77,
  "word_count": 18,
  "processed_text": "viral heboh pemerintah larang orang keluar rumah",
  "indicators": {
    "exclamation_marks": 3,
    "all_caps_words": 2,
    "hoax_keywords": 2,
    "question_marks": 0,
    "url_count": 0
  },
  "hoax_indicator_score": 19,
  "detection_method": "CNN + TF-IDF",
  "recommendations": [
    "Sangat disarankan untuk TIDAK menyebarkan berita ini",
    "Cek sumber berita dari website resmi",
    "Verifikasi ke situs fact-checking seperti TurnBackHoax",
    "Laporkan jika terbukti hoax"
  ]
}
```

**Response Fields:**
- `prediction`: Classification result ("fake" or "real")
- `confidence`: Model confidence score (0-1)
- `fake_score`: Probability of being fake news (0-100%)
- `real_score`: Probability of being real news (0-100%)
- `word_count`: Number of words after preprocessing
- `processed_text`: Preprocessed version of input text
- `indicators`: Various hoax indicators detected
- `hoax_indicator_score`: Combined hoax indicator score
- `detection_method`: Method used for detection
- `recommendations`: Action recommendations based on result

**Status Codes:**
- `200 OK`: Successful analysis
- `400 Bad Request`: Invalid input (missing text, too short)
- `500 Internal Server Error`: Server error

**Example (cURL):**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Menurut data Kementerian Kesehatan, tingkat vaksinasi COVID-19 telah mencapai 70%"
  }'
```

---

### 3. Batch Analysis

**Endpoint:** `POST /batch-analyze`

**Description:** Analyze multiple texts at once

**Request Body:**
```json
{
  "texts": [
    "VIRAL!!! HEBOH banget!",
    "Menurut data Kementerian Kesehatan..."
  ]
}
```

**Parameters:**
- `texts` (array, required): Array of text strings (max 50 texts)

**Response:**
```json
{
  "results": [
    {
      "prediction": "fake",
      "confidence": 0.82,
      "fake_score": 82.5,
      "real_score": 17.5
    },
    {
      "prediction": "real",
      "confidence": 0.75,
      "fake_score": 25.3,
      "real_score": 74.7
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Successful batch analysis
- `400 Bad Request`: Invalid input (not array, too many texts)
- `500 Internal Server Error`: Server error

**Example (cURL):**
```bash
curl -X POST http://localhost:5000/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "VIRAL!!! Share sebelum dihapus!",
      "Presiden meresmikan jalan tol baru"
    ]
  }'
```

---

### 4. Get Statistics

**Endpoint:** `GET /stats`

**Description:** Get system information and configuration

**Response:**
```json
{
  "model_type": "CNN (Convolutional Neural Network)",
  "feature_extraction": "TF-IDF Vectorization",
  "preprocessing_steps": [
    "Text Cleaning",
    "Case Folding",
    "Slang Normalization",
    "Stopword Removal",
    "Stemming (Sastrawi)"
  ],
  "supported_language": "Indonesian",
  "max_text_length": 500,
  "model_status": "loaded"
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved stats

**Example (cURL):**
```bash
curl http://localhost:5000/stats
```

---

## Error Responses

All endpoints may return error responses:

```json
{
  "error": "Error message description"
}
```

### Common Error Codes:
- `400 Bad Request`: Invalid input parameters
- `404 Not Found`: Endpoint not found
- `500 Internal Server Error`: Server-side error

---

## Rate Limiting

Currently no rate limiting implemented. Consider adding for production:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)
```

---

## CORS

CORS is enabled for all origins in development. For production, configure specific origins:

```python
CORS(app, resources={
    r"/*": {
        "origins": ["https://your-frontend-domain.com"]
    }
})
```

---

## Authentication (Optional)

To add API key authentication:

```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != 'your-secret-key':
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/analyze', methods=['POST'])
@require_api_key
def analyze():
    # ...
```

---

## Testing with Postman

### Import Collection

Create a Postman collection with these requests:

1. **Health Check**
   - Method: GET
   - URL: `http://localhost:5000/health`

2. **Analyze Text**
   - Method: POST
   - URL: `http://localhost:5000/analyze`
   - Body (raw JSON):
   ```json
   {
     "text": "Your news text here"
   }
   ```

3. **Batch Analyze**
   - Method: POST
   - URL: `http://localhost:5000/batch-analyze`
   - Body (raw JSON):
   ```json
   {
     "texts": ["Text 1", "Text 2"]
   }
   ```

4. **Get Stats**
   - Method: GET
   - URL: `http://localhost:5000/stats`

---

## Python Client Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:5000"

# Analyze text
def analyze_news(text):
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={"text": text}
    )
    return response.json()

# Usage
result = analyze_news("VIRAL!!! HEBOH banget!")
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']:.2%}")
```

---

## JavaScript Client Example

```javascript
// Analyze text
async function analyzeNews(text) {
  const response = await fetch('http://localhost:5000/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });
  
  return await response.json();
}

// Usage
const result = await analyzeNews('VIRAL!!! HEBOH banget!');
console.log('Prediction:', result.prediction);
console.log('Confidence:', result.confidence);
```

---

## Response Time

Typical response times:
- Health Check: < 10ms
- Single Analysis: 50-200ms
- Batch Analysis: 100-500ms (depends on number of texts)
- Stats: < 10ms

---

## Best Practices

1. **Input Validation**
   - Always validate text length client-side
   - Minimum 10 characters
   - Maximum recommended: 5000 characters

2. **Error Handling**
   - Always check response status
   - Handle errors gracefully
   - Show user-friendly messages

3. **Performance**
   - Use batch analysis for multiple texts
   - Implement caching if needed
   - Consider debouncing for real-time analysis

4. **Security**
   - Sanitize user input
   - Use HTTPS in production
   - Implement rate limiting
   - Add authentication for production

---

Last Updated: 2024
