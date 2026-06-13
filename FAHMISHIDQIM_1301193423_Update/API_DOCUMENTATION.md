# API Documentation - Fake News Detector

Base URL: `http://localhost:5000`

## Endpoints

### 1. Health Check
**GET** `/health`

Cek status server dan model.

**Response:**
```json
{
  "status": "online",
  "model_loaded": false,
  "vectorizer_loaded": false,
  "detection_method": "Rule-based",
  "features": ["text_analysis", "url_scraping", "dataset_management"]
}
```

---

### 2. Analyze Text
**POST** `/analyze`

Analisis teks berita untuk deteksi fake news.

**Request Body:**
```json
{
  "text": "VIRAL!!! Pemerintah akan tutup semua bank besok!!!"
}
```

**Response:**
```json
{
  "prediction": "fake",
  "confidence": 0.85,
  "fake_score": 85.23,
  "real_score": 14.77,
  "word_count": 45,
  "processed_text": "viral pemerintah tutup bank besok...",
  "indicators": {
    "exclamation_marks": 3,
    "all_caps_words": 2,
    "hoax_keywords": 1,
    "question_marks": 0,
    "url_count": 0
  },
  "hoax_indicator_score": 15,
  "detection_method": "Rule-based",
  "source": "manual_text_input",
  "recommendations": [
    "Sangat disarankan untuk TIDAK menyebarkan berita ini",
    "Cek sumber berita dari website resmi",
    "Verifikasi ke situs fact-checking seperti TurnBackHoax"
  ]
}
```

---

### 3. Analyze URL
**POST** `/analyze-url`

Scraping dan analisis berita dari URL.

**Request Body:**
```json
{
  "url": "https://www.detik.com/news/berita/..."
}
```

**Response:**
```json
{
  "prediction": "real",
  "confidence": 0.72,
  "fake_score": 28.45,
  "real_score": 71.55,
  "word_count": 250,
  "processed_text": "...",
  "indicators": {...},
  "hoax_indicator_score": 5,
  "detection_method": "Rule-based",
  "source": "url_scraping",
  "source_info": {
    "url": "https://www.detik.com/news/berita/...",
    "title": "Judul Berita",
    "scraping_method": "newspaper3k",
    "authors": ["Penulis 1", "Penulis 2"],
    "publish_date": "2024-12-22",
    "image_url": "https://...",
    "original_word_count": 250
  },
  "recommendations": [...]
}
```

**Error Response:**
```json
{
  "error": "Failed to fetch URL: Connection timeout"
}
```

---

### 4. Upload Dataset
**POST** `/upload-dataset`

Upload dataset untuk training model.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file`
- Allowed formats: CSV, TXT, JSON
- Max size: 50MB

**Response:**
```json
{
  "success": true,
  "message": "Dataset uploaded successfully",
  "filename": "20241222_143025_dataset.csv",
  "size": 1048576,
  "path": "datasets/20241222_143025_dataset.csv"
}
```

**Error Response:**
```json
{
  "error": "Invalid file type. Allowed: csv, txt, json"
}
```

---

### 5. List Datasets
**GET** `/datasets`

Dapatkan daftar semua dataset yang tersimpan.

**Response:**
```json
{
  "datasets": [
    {
      "filename": "20241222_143025_dataset.csv",
      "size": 1048576,
      "upload_date": "2024-12-22T14:30:25.123456",
      "original_filename": "dataset.csv"
    },
    {
      "filename": "20241222_150000_news_data.json",
      "size": 2097152,
      "upload_date": "2024-12-22T15:00:00.654321",
      "original_filename": "news_data.json"
    }
  ]
}
```

---

### 6. Delete Dataset
**DELETE** `/delete-dataset/<filename>`

Hapus dataset yang tersimpan.

**Example:**
```
DELETE /delete-dataset/20241222_143025_dataset.csv
```

**Response:**
```json
{
  "success": true,
  "message": "Dataset deleted successfully"
}
```

**Error Response:**
```json
{
  "error": "Dataset not found"
}
```

---

### 7. Batch Analyze
**POST** `/batch-analyze`

Analisis multiple teks sekaligus (max 50).

**Request Body:**
```json
{
  "texts": [
    "VIRAL!!! Pemerintah akan tutup bank!!!",
    "Presiden meresmikan jalan tol baru.",
    "HEBOH! Ditemukan cara mudah kaya!"
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "prediction": "fake",
      "confidence": 0.85,
      "fake_score": 85.23,
      "real_score": 14.77
    },
    {
      "prediction": "real",
      "confidence": 0.75,
      "fake_score": 25.12,
      "real_score": 74.88
    },
    {
      "prediction": "fake",
      "confidence": 0.92,
      "fake_score": 92.15,
      "real_score": 7.85
    }
  ]
}
```

---

### 8. Get Statistics
**GET** `/stats`

Dapatkan statistik sistem.

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
  "model_status": "not loaded",
  "features": {
    "text_analysis": true,
    "url_scraping": true,
    "dataset_management": true
  },
  "datasets_count": 2
}
```

---

## Dataset Format

### CSV Format
```csv
text,label
"Berita asli...",0
"Berita palsu!!!",1
```

### TXT Format
```
Berita asli...|0
Berita palsu!!!|1
```

### JSON Format
```json
[
  {"text": "Berita asli...", "label": 0},
  {"text": "Berita palsu!!!", "label": 1}
]
```

**Label values:**
- `0` = Real/Asli
- `1` = Fake/Palsu

Alternative labels supported:
- Real: `0`, `"real"`, `"true"`, `"asli"`, `"benar"`, `"valid"`
- Fake: `1`, `"fake"`, `"false"`, `"palsu"`, `"hoax"`, `"invalid"`

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Example Usage

### cURL Examples

**Analyze Text:**
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "VIRAL!!! Pemerintah akan tutup bank!!!"}'
```

**Analyze URL:**
```bash
curl -X POST http://localhost:5000/analyze-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.detik.com/news/..."}'
```

**Upload Dataset:**
```bash
curl -X POST http://localhost:5000/upload-dataset \
  -F "file=@dataset.csv"
```

**List Datasets:**
```bash
curl http://localhost:5000/datasets
```

**Delete Dataset:**
```bash
curl -X DELETE http://localhost:5000/delete-dataset/filename.csv
```

### Python Examples

```python
import requests

# Analyze text
response = requests.post('http://localhost:5000/analyze', 
    json={'text': 'VIRAL!!! Pemerintah akan tutup bank!!!'})
print(response.json())

# Analyze URL
response = requests.post('http://localhost:5000/analyze-url',
    json={'url': 'https://www.detik.com/news/...'})
print(response.json())

# Upload dataset
with open('dataset.csv', 'rb') as f:
    response = requests.post('http://localhost:5000/upload-dataset',
        files={'file': f})
print(response.json())
```

### JavaScript/Fetch Examples

```javascript
// Analyze text
fetch('http://localhost:5000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'VIRAL!!! Pemerintah akan tutup bank!!!' })
})
.then(res => res.json())
.then(data => console.log(data));

// Analyze URL
fetch('http://localhost:5000/analyze-url', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://www.detik.com/news/...' })
})
.then(res => res.json())
.then(data => console.log(data));

// Upload dataset
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:5000/upload-dataset', {
  method: 'POST',
  body: formData
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## Training Model

To train the model with custom dataset:

```bash
cd backend
python train_model.py --dataset datasets/your_dataset.csv
```

Or use the sample dataset:

```bash
python train_model.py
```

After training, the server will automatically use the new model on restart.
