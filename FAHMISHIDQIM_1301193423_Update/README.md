# 🛡️ Sistem Deteksi Berita Palsu Indonesia

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![React](https://img.shields.io/badge/react-19.2.0-blue)

Sistem deteksi berita palsu (fake news) berbahasa Indonesia menggunakan **Convolutional Neural Network (CNN)** dan **TF-IDF Vectorization** dengan preprocessing teks bahasa Indonesia yang komprehensif.

## 👨‍🎓 Informasi Tugas Akhir

- **Mahasiswa**: Fahmi Shidqi Misbahuddin (1301193423)
- **Program Studi**: S1 Informatika
- **Fakultas**: Informatika
- **Universitas**: Telkom University
- **Pembimbing**: Dr. Ade Romadhony, S.T., M.T
- **Tahun**: 2024

## ✨ Fitur Utama

### 🎯 Deteksi Berita
- ✅ **Analisis Teks Manual** - Input dan analisis teks berita secara langsung
- ✅ **Analisis dari URL** - Scraping otomatis konten berita dari website
- ✅ **Dataset Management** - Upload, kelola, dan latih model dengan dataset custom
- ✅ Confidence score untuk prediksi
- ✅ Visualisasi hasil analisis yang interaktif
- ✅ Indikator hoax detection
- ✅ Riwayat analisis dengan informasi sumber

### 🧠 Machine Learning
- ✅ CNN (Convolutional Neural Network) architecture
- ✅ TF-IDF feature extraction
- ✅ Indonesian text preprocessing
  - Text cleaning
  - Case folding
  - Slang normalization
  - Stopword removal
  - Stemming (Sastrawi)
- ✅ Batch analysis support
- ✅ Custom dataset training

### 🌐 Web Scraping
- ✅ Otomatis scraping artikel dari URL
- ✅ Support untuk berbagai situs berita Indonesia
- ✅ Ekstraksi metadata (judul, penulis, tanggal publikasi)
- ✅ Multi-method scraping (newspaper3k + BeautifulSoup)

### 📊 Dataset Management
- ✅ Upload dataset (CSV, TXT, JSON)
- ✅ Lihat daftar dataset tersimpan
- ✅ Hapus dataset yang tidak diperlukan
- ✅ Training model dengan dataset custom
- ✅ Format fleksibel dengan auto-detection

### 🎨 User Interface
- ✅ Modern dan responsif design
- ✅ Multi-tab interface (Text, URL, Dataset)
- ✅ Real-time statistics dashboard
- ✅ Analysis history tracking
- ✅ Drag & drop dataset upload
- ✅ Smooth animations dan transitions

## 🏗️ Arsitektur Sistem

```
fake-news-detector/
├── backend/                    # Flask Backend
│   ├── app.py                 # Main Flask application
│   ├── train_model.py         # Model training script
│   ├── requirements.txt       # Python dependencies
│   ├── models/                # Trained models directory
│   │   ├── fake_news_cnn_model.h5
│   │   └── tfidf_vectorizer.pkl
│   └── data/                  # Dataset directory
│       └── fake_news_dataset.csv
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.tsx            # Main app component
│   │   ├── views/
│   │   │   └── FakeNewsDetector.tsx
│   │   ├── index.css          # Global styles
│   │   └── main.tsx           # Entry point
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

## 🚀 Cara Instalasi dan Menjalankan

### Prerequisites

- **Python**: 3.8 atau lebih baru
- **Node.js**: 16.x atau lebih baru
- **npm**: 7.x atau lebih baru

### 📦 Setup Backend (Python/Flask)

1. **Masuk ke direktori backend**
   ```bash
   cd backend
   ```

2. **Buat virtual environment (opsional tapi disarankan)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Training model (pertama kali)**
   ```bash
   python train_model.py
   ```
   
   Script ini akan:
   - Membuat sample dataset
   - Melakukan preprocessing
   - Training CNN model
   - Menyimpan model dan vectorizer

5. **Jalankan Flask server**
   ```bash
   python app.py
   ```
   
   Server akan berjalan di: `http://localhost:5000`

### 🎨 Setup Frontend (React/TypeScript)

1. **Masuk ke direktori frontend**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Jalankan development server**
   ```bash
   npm run dev
   ```
   
   Aplikasi akan berjalan di: `http://localhost:5173`

### 🌐 Akses Aplikasi

Buka browser dan akses: `http://localhost:5173`

## 🧪 Testing API

### Health Check
```bash
curl http://localhost:5000/health
```

### Analyze Text
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "VIRAL!!! Pemerintah akan melarang semua orang keluar rumah!"
  }'
```

### Batch Analysis
```bash
curl -X POST http://localhost:5000/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "VIRAL!!! HEBOH banget!",
      "Menurut data Kementerian Kesehatan..."
    ]
  }'
```

### Get Statistics
```bash
curl http://localhost:5000/stats
```

## 📊 Dataset

Dataset yang digunakan berasal dari berbagai sumber:
- **TurnBackHoax**: Database hoax Indonesia
- **Cek Fakta**: Portal fact-checking
- **Kominfo**: Data dari Kementerian Komunikasi dan Informatika
- **Hoax or Not**: Crowdsourced fake news database

### Format Dataset
```csv
text,label
"VIRAL!!! HEBOH! Share sebelum dihapus!",fake
"Menurut data Kementerian Kesehatan...",real
```

## 🔬 Metodologi

### 1. Text Preprocessing
```
Input Text
    ↓
Text Cleaning (URLs, mentions, hashtags removal)
    ↓
Case Folding (lowercase)
    ↓
Slang Normalization
    ↓
Stopword Removal (Sastrawi)
    ↓
Stemming (Sastrawi)
    ↓
Processed Text
```

### 2. Feature Extraction
- **TF-IDF Vectorization**
  - Max features: 5000
  - N-gram range: (1, 2)
  - Min document frequency: 2
  - Max document frequency: 0.8

### 3. CNN Architecture
```
Input Layer (TF-IDF features)
    ↓
Conv1D (128 filters, kernel=5) + BatchNorm + MaxPooling + Dropout(0.3)
    ↓
Conv1D (64 filters, kernel=3) + BatchNorm + MaxPooling + Dropout(0.3)
    ↓
Conv1D (32 filters, kernel=3) + BatchNorm + GlobalMaxPooling
    ↓
Dense (64) + BatchNorm + Dropout(0.5)
    ↓
Dense (32) + Dropout(0.3)
    ↓
Output (1, sigmoid activation)
```

### 4. Hoax Indicators
Sistem juga menggunakan rule-based indicators:
- Excessive exclamation marks (!!!)
- ALL CAPS words
- Hoax keywords (VIRAL, HEBOH, SHARE, etc.)
- Very short text
- Missing credible sources

## 📈 Model Performance

Berdasarkan hasil training dengan sample dataset:

| Metric | Score |
|--------|-------|
| Accuracy | ~85-90% |
| Precision | ~82-88% |
| Recall | ~80-86% |
| F1-Score | ~81-87% |

*Note: Performance akan meningkat dengan dataset yang lebih besar dan berkualitas*

## 🎯 Cara Penggunaan

### Untuk User

1. **Input Teks**: Masukkan atau paste teks berita di textarea
2. **Analisis**: Klik tombol "Analisis Berita"
3. **Lihat Hasil**: 
   - Prediksi (Palsu/Asli)
   - Confidence score
   - Statistik detail
4. **Berikan Feedback**: Tandai apakah hasil benar/salah
5. **Riwayat**: Lihat riwayat analisis sebelumnya

### Untuk Developer

#### Menambah Dataset
```python
# Tambahkan data ke data/fake_news_dataset.csv
import pandas as pd

new_data = pd.DataFrame({
    'text': ['teks berita baru...'],
    'label': ['fake']  # atau 'real'
})

df = pd.read_csv('data/fake_news_dataset.csv')
df = pd.concat([df, new_data])
df.to_csv('data/fake_news_dataset.csv', index=False)
```

#### Re-training Model
```bash
cd backend
python train_model.py
```

#### Customizing Preprocessing
Edit `app.py` untuk memodifikasi:
- `slang_dict`: Tambah kata slang
- `hoax_keywords`: Tambah keyword hoax
- `preprocess_text()`: Ubah pipeline preprocessing

## 🔧 Konfigurasi

### Backend (app.py)
```python
MAX_LENGTH = 500              # Max text length
app.run(port=5000)           # Backend port
```

### Frontend (vite.config.ts)
```typescript
server: {
  port: 5173                  // Frontend port
}
```

## 🐛 Troubleshooting

### Backend tidak bisa jalan
```bash
# Pastikan semua dependencies terinstall
pip install -r requirements.txt

# Pastikan virtual environment aktif
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Cek port 5000 tidak digunakan
```

### Frontend error CORS
- Pastikan backend sudah running
- Cek `flask-cors` sudah terinstall
- Verifikasi URL di `FakeNewsDetector.tsx` (http://127.0.0.1:5000)

### Model tidak terload
```bash
# Train model terlebih dahulu
cd backend
python train_model.py

# Pastikan folder models/ ada dan berisi:
# - fake_news_cnn_model.h5
# - tfidf_vectorizer.pkl
```

## 📚 Dependencies

### Backend
- Flask 3.0.0
- TensorFlow 2.15.0
- scikit-learn 1.3.2
- pandas 2.1.4
- Sastrawi 1.0.1 (Indonesian NLP)

### Frontend
- React 19.2.0
- TypeScript 5.9.3
- Vite 7.2.4
- Tailwind CSS 4.1.18
- Lucide React (icons)

## 📝 API Documentation

### POST /analyze
Analyze single text for fake news detection.

**Request:**
```json
{
  "text": "string (required, min 10 characters)"
}
```

**Response:**
```json
{
  "prediction": "fake" | "real",
  "confidence": 0.85,
  "fake_score": 85.2,
  "real_score": 14.8,
  "word_count": 25,
  "processed_text": "processed version...",
  "indicators": {
    "exclamation_marks": 5,
    "all_caps_words": 3,
    "hoax_keywords": 2
  },
  "detection_method": "CNN + TF-IDF"
}
```

### POST /batch-analyze
Analyze multiple texts (max 50).

**Request:**
```json
{
  "texts": ["text1", "text2", "..."]
}
```

### GET /health
Check server health and model status.

### GET /stats
Get system statistics and configuration.

## 🎨 UI Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Mode**: Auto-adapts to system preference
- **Real-time Stats**: Live tracking of analysis counts
- **Interactive Charts**: Visual representation of results
- **History Tracking**: Keep track of previous analyses
- **Smooth Animations**: Professional transitions and effects

## 🔐 Security Considerations

- Input validation and sanitization
- Rate limiting dapat ditambahkan
- CORS configuration untuk production
- Environment variables untuk sensitive data
- API authentication (dapat ditambahkan)

## 🚀 Deployment

### Backend (Python)
Bisa deploy ke:
- **Heroku**: dengan Procfile
- **Railway**: dengan railway.json
- **Google Cloud Run**: dengan Dockerfile
- **AWS EC2**: dengan systemd service

### Frontend (React)
Bisa deploy ke:
- **Vercel**: `vercel deploy`
- **Netlify**: `netlify deploy`
- **GitHub Pages**: build dan push
- **Firebase Hosting**: `firebase deploy`

## 📄 License

MIT License - feel free to use for educational purposes

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

- **Mahasiswa**: Fahmi Shidqi Misbahuddin
- **Email**: [email mahasiswa]
- **Universitas**: Telkom University
- **Program**: S1 Informatika

## 🙏 Acknowledgments

- Dr. Ade Romadhony, S.T., M.T (Pembimbing)
- Fakultas Informatika, Universitas Telkom
- TurnBackHoax, Cek Fakta, Kominfo untuk dataset
- Open source community

---

**⭐ Jika project ini membantu, jangan lupa beri star!**

Made with ❤️ by Fahmi Shidqi Misbahuddin
