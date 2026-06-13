# 🚀 Quick Start Guide

## Instalasi Cepat

### 1. Clone Repository
```bash
git clone <repository-url>
cd fake-news-detector
```

### 2. Setup Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
python train_model.py          # Training model (pertama kali)
python app.py                  # Start server
```

### 3. Setup Frontend (Terminal Baru)
```bash
cd frontend
npm install
npm run dev
```

### 4. Akses Aplikasi
Buka browser: `http://localhost:5173`

## Testing

### Test Backend API
```bash
# Health check
curl http://localhost:5000/health

# Test analisis
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "VIRAL!!! HEBOH banget! Share sebelum dihapus!!!"}'
```

### Test Frontend
1. Buka `http://localhost:5173`
2. Paste contoh teks berita
3. Klik "Analisis Berita"
4. Lihat hasil

## Troubleshooting

**Backend tidak jalan:**
- Pastikan Python 3.8+
- Aktifkan virtual environment
- Install semua dependencies
- Train model terlebih dahulu

**Frontend tidak jalan:**
- Pastikan Node.js 16+
- Hapus `node_modules` dan `npm install` lagi
- Clear cache: `npm cache clean --force`

**CORS Error:**
- Pastikan backend sudah running di port 5000
- Check `flask-cors` terinstall

## Development Mode

### Backend dengan auto-reload
```bash
cd backend
$env:FLASK_ENV="development"  # Windows PowerShell
python app.py
```

### Frontend dengan hot-reload
```bash
cd frontend
npm run dev
```

## Build untuk Production

### Backend
```bash
cd backend
# Setup production server (gunicorn, etc)
gunicorn app:app
```

### Frontend
```bash
cd frontend
npm run build
# Output di folder dist/
```

## Next Steps

1. ✅ Tambah dataset lebih banyak
2. ✅ Re-train model dengan dataset baru
3. ✅ Deploy ke production
4. ✅ Setup monitoring
5. ✅ Add user authentication (optional)

## Useful Commands

```bash
# Backend
pip list                       # List installed packages
pip freeze > requirements.txt  # Update requirements
python train_model.py          # Retrain model

# Frontend
npm run build                  # Build for production
npm run preview               # Preview production build
npm run lint                   # Run linter
```

## Resources

- 📖 [Full Documentation](README.md)
- 🐛 [Report Issues](issues)
- 💬 [Discussions](discussions)
- 📧 Contact: [your-email]
