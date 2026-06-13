# 📘 Panduan Penggunaan Lengkap - Fake News Detector

## 🎯 Daftar Isi
1. [Instalasi](#instalasi)
2. [Menjalankan Aplikasi](#menjalankan-aplikasi)
3. [Fitur-Fitur Utama](#fitur-fitur-utama)
4. [Analisis Teks Manual](#analisis-teks-manual)
5. [Analisis dari URL](#analisis-dari-url)
6. [Kelola Dataset](#kelola-dataset)
7. [Training Model](#training-model)
8. [Tips & Troubleshooting](#tips--troubleshooting)

---

## 🔧 Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd fake-news-detector
```

### 2. Setup Backend
```bash
cd backend

# Buat virtual environment
python -m venv venv

# Aktifkan venv (Windows)
venv\Scripts\activate

# Aktifkan venv (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Frontend
```bash
cd ../frontend

# Install dependencies
npm install
```

---

## 🚀 Menjalankan Aplikasi

### Cara 1: Manual

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```
Server akan berjalan di: http://127.0.0.1:5000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend akan berjalan di: http://localhost:5173

### Cara 2: Menggunakan Batch Scripts (Windows)

**Pertama kali:**
```bash
setup.bat
```

**Jalankan aplikasi:**
```bash
start.bat
```

**Training model:**
```bash
train.bat
```

---

## 🎨 Fitur-Fitur Utama

### 1. 📝 Analisis Teks Manual
- Input teks berita secara langsung
- Deteksi real-time
- Hasil dengan confidence score
- Rekomendasi tindakan

### 2. 🔗 Analisis dari URL
- Scraping otomatis dari website berita
- Ekstraksi judul, konten, penulis
- Analisis lengkap dengan metadata
- Support berbagai situs berita Indonesia

### 3. 📊 Kelola Dataset
- Upload dataset (CSV, TXT, JSON)
- Lihat daftar dataset
- Hapus dataset
- Training model dengan dataset custom

### 4. 📈 Dashboard Statistik
- Total analisis
- Jumlah berita palsu
- Jumlah berita asli
- Riwayat analisis

---

## 📝 Analisis Teks Manual

### Langkah-langkah:

1. **Buka tab "Analisis Teks"**
   - Klik tab pertama (icon FileText)

2. **Input teks berita**
   - Ketik atau paste teks di textarea
   - Minimal 10 karakter

3. **Gunakan contoh (opsional)**
   - Klik salah satu contoh untuk auto-fill

4. **Klik "Analisis Sekarang"**
   - Tunggu beberapa detik
   - Hasil akan muncul di bawah

### Hasil Analisis:
- ✅ **Status**: Palsu atau Asli
- 📊 **Confidence**: Tingkat keyakinan (%)
- 📈 **Score Bars**: Visualisasi skor fake vs real
- 📝 **Detail**: Jumlah kata, indikator hoax
- 💡 **Rekomendasi**: Saran tindakan

### Contoh Penggunaan:

**Berita Palsu:**
```
VIRAL!!! HEBOH! Pemerintah akan melarang semua orang 
keluar rumah mulai besok! SEGERA SHARE sebelum dihapus!!!
```

**Berita Asli:**
```
Menurut data Kementerian Kesehatan, tingkat vaksinasi 
COVID-19 di Indonesia telah mencapai 70% dari target 
populasi berdasarkan laporan resmi yang dirilis hari ini.
```

---

## 🔗 Analisis dari URL

### Langkah-langkah:

1. **Buka tab "Analisis URL"**
   - Klik tab kedua (icon Link)

2. **Input URL berita**
   - Paste URL lengkap berita
   - Format: https://...

3. **Klik "Analisis Sekarang"**
   - Sistem akan scraping konten
   - Proses 5-15 detik

4. **Lihat hasil**
   - Sama dengan analisis teks
   - Plus informasi sumber

### Informasi Sumber yang Ditampilkan:
- 📰 **Judul berita**
- 🔗 **URL asli**
- ✍️ **Penulis** (jika ada)
- 📅 **Tanggal publikasi** (jika ada)
- 🖼️ **Gambar utama** (jika ada)

### Contoh URL yang Didukung:
- Detik.com
- Kompas.com
- Tempo.co
- CNN Indonesia
- Dan situs berita Indonesia lainnya

### Tips:
- ✅ Pastikan URL valid dan accessible
- ✅ Gunakan URL artikel, bukan homepage
- ⚠️ Beberapa situs mungkin memblokir scraping
- ⚠️ Konten di balik paywall tidak bisa di-scrape

---

## 📊 Kelola Dataset

### Upload Dataset

#### Langkah-langkah:

1. **Buka tab "Kelola Dataset"**
   - Klik tab ketiga (icon Database)

2. **Klik area upload**
   - Atau drag & drop file

3. **Pilih file**
   - Format: CSV, TXT, atau JSON
   - Max 50MB

4. **Tunggu upload selesai**
   - Notifikasi akan muncul

### Format Dataset

#### CSV Format:
```csv
text,label
"Presiden meresmikan jalan tol baru",0
"VIRAL!!! Bank akan tutup besok!!!",1
```

**Kolom yang didukung:**
- Text: `text`, `content`, `news`, `article`, `berita`
- Label: `label`, `class`, `category`, `type`, `kategori`

#### TXT Format:
```
Presiden meresmikan jalan tol baru|0
VIRAL!!! Bank akan tutup besok!!!|1
```

#### JSON Format:
```json
[
  {
    "text": "Presiden meresmikan jalan tol baru",
    "label": 0
  },
  {
    "text": "VIRAL!!! Bank akan tutup besok!!!",
    "label": 1
  }
]
```

### Label Values:
- **Real (0)**: `0`, `real`, `true`, `asli`, `benar`, `valid`
- **Fake (1)**: `1`, `fake`, `false`, `palsu`, `hoax`, `invalid`

### Lihat Dataset

Setelah upload, dataset akan muncul di list dengan info:
- 📄 Nama file asli
- 💾 Ukuran file
- 📅 Tanggal upload
- 🎯 Tombol training
- 🗑️ Tombol hapus

### Hapus Dataset

1. Klik icon 🗑️ (Trash) di dataset yang ingin dihapus
2. Konfirmasi penghapusan
3. Dataset terhapus dari server

---

## 🎓 Training Model

### Menggunakan Dataset Custom

#### Via Web Interface:
1. Upload dataset ke tab "Kelola Dataset"
2. Klik icon 🏆 (Award) pada dataset
3. Akan muncul instruksi untuk menjalankan training

#### Via Terminal:
```bash
cd backend

# Training dengan dataset custom
python train_model.py --dataset datasets/nama_file.csv

# Training dengan sample dataset
python train_model.py
```

### Proses Training:

1. **Loading dataset**
   - Membaca dan validasi data
   - Menampilkan statistik

2. **Preprocessing**
   - Text cleaning
   - Stopword removal
   - Stemming

3. **Feature extraction**
   - TF-IDF vectorization
   - 5000 features max

4. **Model training**
   - CNN dengan 3 Conv1D layers
   - Batch size: 16
   - Max epochs: 50
   - Early stopping

5. **Evaluation**
   - Test accuracy
   - Classification report
   - Confusion matrix

6. **Saving**
   - Model: `models/fake_news_cnn_model.h5`
   - Vectorizer: `models/tfidf_vectorizer.pkl`
   - Metadata: `models/training_metadata.json`

### Waktu Training:
- **Sample dataset (40 berita)**: ~2-5 menit
- **1000 berita**: ~10-20 menit
- **5000+ berita**: ~30-60 menit

### Setelah Training:

1. **Restart server**
   ```bash
   # Stop server (Ctrl+C)
   python app.py
   ```

2. **Model baru akan loaded otomatis**
   - Check di /health endpoint
   - `model_loaded: true`

3. **Test dengan analisis**
   - Analisis berita baru
   - Compare akurasi

---

## 💡 Tips & Troubleshooting

### Tips Umum

#### Meningkatkan Akurasi:
1. **Gunakan dataset lebih besar**
   - Min 1000 samples
   - Optimal 5000+ samples

2. **Balance data**
   - 50% fake, 50% real
   - Hindari imbalance >70%

3. **Kualitas label**
   - Verifikasi dengan fact-checker
   - Pastikan label akurat

4. **Re-train berkala**
   - Update dengan data baru
   - Adapt dengan tren hoax baru

#### Optimasi Performa:
- Gunakan GPU untuk training (jika ada)
- Batch size lebih besar untuk dataset besar
- Reduce features jika OOM

### Troubleshooting

#### ❌ Server tidak bisa diakses

**Solusi:**
```bash
# Check apakah server running
curl http://127.0.0.1:5000/health

# Restart server
# Terminal backend: Ctrl+C
python app.py
```

#### ❌ CORS Error di browser

**Solusi:**
- Pastikan backend dan frontend running
- Check port: Backend=5000, Frontend=5173
- Clear browser cache

#### ❌ Scraping gagal

**Penyebab umum:**
- URL tidak valid
- Situs memblokir scraping
- Konten di balik paywall
- Network error

**Solusi:**
- Coba URL lain
- Check koneksi internet
- Gunakan input teks manual

#### ❌ Upload dataset gagal

**Penyebab:**
- File terlalu besar (>50MB)
- Format tidak sesuai
- Kolom tidak ditemukan

**Solusi:**
- Compress dataset jika >50MB
- Check format CSV/TXT/JSON
- Pastikan ada kolom text & label

#### ❌ Training error

**Penyebab:**
- Dataset terlalu kecil
- Memory insufficient
- Label tidak valid

**Solusi:**
```bash
# Check dataset format
python train_model.py --dataset datasets/file.csv

# Jika error, coba sample dataset dulu
python train_model.py
```

#### ❌ Model akurasi rendah

**Penyebab:**
- Dataset terlalu kecil
- Data imbalance
- Label tidak akurat

**Solusi:**
1. Tambah data hingga min 1000 samples
2. Balance fake:real ratio ke ~50:50
3. Verifikasi ulang label
4. Re-train dengan data baru

#### ❌ Frontend tidak muncul hasil

**Check:**
1. Backend running? → Check terminal
2. CORS enabled? → Check console
3. Network request success? → Check DevTools
4. Response valid? → Check response JSON

**Debug:**
```javascript
// Di browser console
fetch('http://127.0.0.1:5000/health')
  .then(r => r.json())
  .then(d => console.log(d))
```

---

## 📞 Support

Jika menemui masalah:

1. **Check dokumentasi** di README.md
2. **Check API docs** di API_DOCUMENTATION.md
3. **Check dataset guide** di DATASET_GUIDE.md
4. **Check terminal output** untuk error messages
5. **Open issue** di repository (jika menggunakan Git)

---

## 📚 Referensi

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
- [TensorFlow Keras](https://www.tensorflow.org/guide/keras)
- [Scikit-learn](https://scikit-learn.org/)
- [Sastrawi](https://github.com/sastrawi/sastrawi)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

---

**Happy Detecting! 🛡️**

Lindungi diri dan orang lain dari berita palsu dengan sistem deteksi AI yang akurat.
