# Dataset Information

## Sumber Dataset

Dataset untuk sistem deteksi berita palsu ini dikumpulkan dari berbagai sumber terpercaya:

### 1. TurnBackHoax
- Website: https://turnbackhoax.id/
- Database hoax yang terverifikasi
- Dikurasi oleh Masyarakat Anti Fitnah Indonesia (MAFINDO)

### 2. Cek Fakta
- Portal fact-checking Indonesia
- Verifikasi berita dari berbagai media

### 3. Kominfo
- Data dari Kementerian Komunikasi dan Informatika
- Laporan hoax resmi

### 4. Hoax or Not
- Crowdsourced database
- Kontribusi dari masyarakat

## Format Dataset

Dataset disimpan dalam format CSV dengan struktur:

```csv
text,label
"VIRAL!!! HEBOH! Pemerintah akan...",fake
"Menurut data Kementerian Kesehatan...",real
```

### Kolom:
- **text**: Teks berita lengkap (string)
- **label**: Label klasifikasi (fake/real)

## Statistik Dataset

### Sample Dataset (default)
- Total: 30 berita
- Fake news: 15
- Real news: 15
- Balanced dataset

### Rekomendasi Dataset Production
- Minimal: 1000+ berita per kategori
- Ideal: 5000+ berita per kategori
- Balanced atau slightly imbalanced (60:40)

## Karakteristik Berita Palsu

### Indikator Umum:
1. **Judul Sensasional**
   - VIRAL!!!, HEBOH!!!, MENGEJUTKAN!!!
   - Penggunaan huruf kapital berlebihan
   
2. **Kata-kata Trigger**
   - "Share sebelum dihapus"
   - "Sebarkan ke semua grup"
   - "Jangan sampai terlambat"
   
3. **Tanpa Sumber Jelas**
   - Tidak menyebutkan sumber
   - Sumber tidak kredibel
   
4. **Informasi Tidak Lengkap**
   - Terlalu pendek
   - Tidak ada detail
   - Tanpa tanggal/lokasi

5. **Emosional**
   - Membangkitkan emosi (takut, marah)
   - Provokatif

## Karakteristik Berita Asli

### Ciri-ciri:
1. **Sumber Jelas**
   - Menyebutkan sumber resmi
   - Kutipan dari pejabat/ahli
   
2. **Informasi Lengkap**
   - Detail waktu dan tempat
   - Konteks yang jelas
   
3. **Bahasa Formal**
   - Tidak sensasional
   - Objektif
   
4. **Verifiable**
   - Bisa dicek dari sumber lain
   - Ada bukti pendukung

## Cara Menambah Dataset

### 1. Manual Entry
Tambahkan langsung ke `data/fake_news_dataset.csv`:

```csv
text,label
"Teks berita baru...",fake
"Teks berita lain...",real
```

### 2. Programmatically
```python
import pandas as pd

# Load existing dataset
df = pd.read_csv('data/fake_news_dataset.csv')

# Add new data
new_data = pd.DataFrame({
    'text': ['New fake news...', 'New real news...'],
    'label': ['fake', 'real']
})

# Combine
df = pd.concat([df, new_data], ignore_index=True)

# Save
df.to_csv('data/fake_news_dataset.csv', index=False)
```

### 3. Web Scraping (Advanced)
```python
# Contoh scraping dari TurnBackHoax
import requests
from bs4 import BeautifulSoup

# Implementasi web scraping
# Note: Pastikan mematuhi robots.txt dan terms of service
```

## Data Preprocessing

Setiap teks berita melalui preprocessing:

1. **Text Cleaning**
   - Hapus URL, mention, hashtag
   - Hapus special characters
   
2. **Case Folding**
   - Convert ke lowercase
   
3. **Slang Normalization**
   - gak → tidak
   - yg → yang
   - dll
   
4. **Stopword Removal**
   - Hapus kata umum (di, ke, dari, dll)
   
5. **Stemming**
   - berlari → lari
   - makanan → makan

## Data Splitting

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels,
    test_size=0.2,        # 80% train, 20% test
    random_state=42,      # Reproducible
    stratify=labels       # Balanced split
)
```

## Data Augmentation (Opsional)

### Teknik yang bisa digunakan:
1. **Synonym Replacement**
   - Ganti kata dengan sinonim
   
2. **Back Translation**
   - ID → EN → ID
   
3. **Random Insertion**
   - Insert kata-kata umum
   
4. **Random Swap**
   - Tukar posisi kata

## Best Practices

### DO:
✅ Gunakan dataset yang seimbang  
✅ Verifikasi label dengan manual  
✅ Update dataset secara berkala  
✅ Dokumentasikan sumber data  
✅ Bersihkan data duplikat  

### DON'T:
❌ Gunakan data tanpa verifikasi  
❌ Bias terhadap topik tertentu  
❌ Copy-paste dari satu sumber saja  
❌ Abaikan data privacy  
❌ Gunakan dataset terlalu kecil  

## Dataset Quality Metrics

### Checklist:
- [ ] Minimum 1000 samples
- [ ] Balanced classes (45-55%)
- [ ] No duplicates
- [ ] Verified labels
- [ ] Diverse topics
- [ ] Recent data (< 2 years)
- [ ] Clean text (no HTML, special chars)

## Resources untuk Dataset

### Websites:
- TurnBackHoax: https://turnbackhoax.id/
- Cek Fakta: https://cekfakta.com/
- Kominfo Hoax Buster: https://www.kominfo.go.id/
- Tempo Cek Fakta: https://cekfakta.tempo.co/

### Academic Datasets:
- Indonesian Fake News Dataset (Kaggle)
- Hoax News Dataset (GitHub)
- Social Media Fake News (Research papers)

## Update Dataset

Setelah menambah dataset:

```bash
cd backend
python train_model.py
```

Model akan di-retrain dengan dataset baru.

## Notes

- Dataset ini untuk keperluan **edukasi dan penelitian**
- Pastikan mematuhi copyright dan privacy
- Verifikasi manual sangat disarankan
- Update dataset secara berkala untuk akurasi terbaik

---

Last Updated: 2024
