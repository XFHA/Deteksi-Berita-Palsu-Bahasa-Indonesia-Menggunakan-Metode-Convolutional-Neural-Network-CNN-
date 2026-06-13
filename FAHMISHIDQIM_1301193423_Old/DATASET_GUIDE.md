# Dataset untuk Training Model Fake News Detector

Dataset ini digunakan untuk melatih model CNN dalam mendeteksi berita palsu (hoax) berbahasa Indonesia.

## Format Dataset yang Didukung

### 1. CSV Format
File CSV dengan kolom:
- `text`: Teks berita
- `label`: Label (0 = real/asli, 1 = fake/palsu)

Contoh:
```csv
text,label
"Presiden meresmikan jalan tol baru sepanjang 100 km",0
"VIRAL!!! Pemerintah akan tutup semua toko besok!!!",1
```

Nama kolom alternatif yang didukung:
- Text: `text`, `content`, `news`, `article`, `berita`
- Label: `label`, `class`, `category`, `type`, `kategori`

Label value alternatif:
- Real: `0`, `real`, `true`, `asli`, `benar`, `valid`
- Fake: `1`, `fake`, `false`, `palsu`, `hoax`, `invalid`

### 2. TXT Format
File teks dengan setiap baris berformat:
```
teks_berita|label
```

Contoh:
```
Presiden meresmikan jalan tol baru sepanjang 100 km|0
VIRAL!!! Pemerintah akan tutup semua toko besok!!!|1
```

### 3. JSON Format
Array objek JSON dengan key `text` dan `label`:

```json
[
  {
    "text": "Presiden meresmikan jalan tol baru sepanjang 100 km",
    "label": 0
  },
  {
    "text": "VIRAL!!! Pemerintah akan tutup semua toko besok!!!",
    "label": 1
  }
]
```

## Cara Upload Dataset

### Melalui Web Interface:
1. Buka aplikasi web
2. Klik tab "Kelola Dataset"
3. Click area upload atau drag & drop file
4. File akan tersimpan di folder `backend/datasets/`

### Melalui API:
```bash
curl -X POST http://localhost:5000/upload-dataset \
  -F "file=@dataset.csv"
```

## Cara Training Model dengan Dataset Custom

### 1. Upload Dataset
Upload file dataset melalui web interface atau copy langsung ke folder `backend/datasets/`

### 2. Jalankan Training
```bash
cd backend
python train_model.py --dataset datasets/nama_file_dataset.csv
```

Atau tanpa argument untuk menggunakan sample dataset:
```bash
python train_model.py
```

## Rekomendasi Dataset

### Ukuran Dataset
- **Minimum**: 100 samples (50 fake + 50 real)
- **Rekomendasi**: 1000+ samples untuk akurasi lebih baik
- **Optimal**: 5000+ samples untuk produksi

### Kualitas Data
- Berita harus berbahasa Indonesia
- Label harus akurat dan terverifikasi
- Panjang teks minimal 50 karakter
- Hindari duplikasi data

### Balancing
Usahakan jumlah fake news dan real news seimbang:
- ✅ Good: 50% fake, 50% real
- ⚠️ OK: 40-60% fake
- ❌ Bad: <30% atau >70% fake

## Sumber Dataset Publik

### Dataset Bahasa Indonesia untuk Fake News Detection:
1. **Indonesian Fake News Dataset** (GitHub)
   - https://github.com/fake-news-detection-id

2. **Hoax News Dataset** (Kaggle)
   - https://www.kaggle.com/datasets/hoax-news-indonesia

3. **Manual Collection**
   - Kumpulkan dari situs fact-checking:
     - TurnBackHoax.id
     - Cekfakta.com
     - Medcom Cek Fakta

## Preprocessing yang Diterapkan

Model akan otomatis melakukan preprocessing:
1. **Text Cleaning**: Hapus URL, mention, hashtag
2. **Case Folding**: Konversi ke lowercase
3. **Slang Normalization**: Ganti kata gaul dengan kata baku
4. **Stopword Removal**: Hapus kata tidak penting
5. **Stemming**: Menggunakan Sastrawi stemmer

## Output Training

Setelah training selesai, akan dihasilkan:
- `models/fake_news_cnn_model.h5`: Model CNN terlatih
- `models/tfidf_vectorizer.pkl`: TF-IDF vectorizer
- `models/training_metadata.json`: Metadata training (accuracy, dll)

## Troubleshooting

### Error: "CSV must have 'text' and 'label' columns"
- Pastikan CSV memiliki kolom `text` dan `label`
- Atau gunakan nama kolom alternatif yang didukung

### Error: "Not enough data"
- Dataset minimal harus 40 samples untuk training
- Tambahkan lebih banyak data

### Error: "Label values must be 0 or 1"
- Periksa format label di dataset
- Gunakan nilai label yang didukung (lihat di atas)

## Contoh Dataset Sample

Lihat file `backend/train_model.py` untuk melihat contoh sample dataset yang sudah terintegras.

## Tips Meningkatkan Akurasi

1. **Tambah Data**: Lebih banyak data = lebih akurat
2. **Balance Data**: Pastikan jumlah fake dan real seimbang
3. **Kualitas Label**: Verifikasi label dengan sumber terpercaya
4. **Variasi Topik**: Gunakan berita dari berbagai topik
5. **Update Berkala**: Re-train model dengan data baru secara berkala
