# 📊 Project Structure

## Overview
```
fake-news-detector/
├── 📄 README.md                 # Main documentation
├── 📄 QUICKSTART.md            # Quick start guide
├── 📄 .gitignore               # Git ignore rules
├── 🚀 setup.bat                # Setup script (Windows)
├── 🚀 start.bat                # Start both servers (Windows)
├── 🚀 train.bat                # Train model (Windows)
│
├── 🔧 backend/                 # Python Flask Backend
│   ├── 📄 app.py              # Main Flask application
│   ├── 📄 train_model.py      # Model training script
│   ├── 📄 requirements.txt    # Python dependencies
│   ├── 📄 API.md              # API documentation
│   ├── 📄 DATASET.md          # Dataset information
│   │
│   ├── 📁 models/             # Trained models
│   │   ├── fake_news_cnn_model.h5      # CNN model
│   │   └── tfidf_vectorizer.pkl        # TF-IDF vectorizer
│   │
│   ├── 📁 data/               # Dataset
│   │   └── fake_news_dataset.csv       # Training data
│   │
│   └── 📁 venv/               # Python virtual environment
│
└── 🎨 frontend/               # React TypeScript Frontend
    ├── 📄 package.json        # Node dependencies
    ├── 📄 vite.config.ts      # Vite configuration
    ├── 📄 tsconfig.json       # TypeScript config
    ├── 📄 tailwind.config.js  # Tailwind CSS config
    ├── 📄 index.html          # HTML entry point
    │
    ├── 📁 src/                # Source code
    │   ├── 📄 main.tsx        # Application entry
    │   ├── 📄 App.tsx         # Main app component
    │   ├── 📄 index.css       # Global styles
    │   │
    │   ├── 📁 views/          # View components
    │   │   └── FakeNewsDetector.tsx    # Main detector page
    │   │
    │   └── 📁 assets/         # Static assets
    │
    ├── 📁 public/             # Public assets
    │
    └── 📁 node_modules/       # Node dependencies
```

## File Descriptions

### Root Level

#### 📄 README.md
Complete documentation including:
- Project overview
- Features
- Installation guide
- Architecture
- Methodology
- API documentation
- Deployment guide

#### 📄 QUICKSTART.md
Quick start guide for:
- Fast setup
- Running the app
- Testing
- Troubleshooting

#### 📄 .gitignore
Ignore patterns for:
- Python cache files
- Virtual environments
- Node modules
- Build artifacts
- IDE files

#### 🚀 setup.bat
Windows batch script to:
- Check Python & Node.js
- Create virtual environment
- Install dependencies
- Setup project

#### 🚀 start.bat
Windows batch script to:
- Start backend server
- Start frontend server
- Open browser

#### 🚀 train.bat
Windows batch script to:
- Train/retrain CNN model
- Save model files

---

### Backend Files

#### 📄 app.py (Main Backend)
```python
# Flask application
# Endpoints:
- GET  /health          # Health check
- POST /analyze         # Analyze text
- POST /batch-analyze   # Batch analysis
- GET  /stats           # System stats
```

**Key Components:**
- Text preprocessing functions
- CNN model loading
- TF-IDF vectorizer
- Hoax indicator detection
- API endpoints

#### 📄 train_model.py
```python
# Model training script
# Functions:
- Load/create dataset
- Preprocess texts
- TF-IDF vectorization
- Build CNN model
- Train and evaluate
- Save model files
```

**Outputs:**
- `models/fake_news_cnn_model.h5`
- `models/tfidf_vectorizer.pkl`

#### 📄 requirements.txt
```
Flask==3.0.0
flask-cors==4.0.0
tensorflow==2.15.0
scikit-learn==1.3.2
pandas==2.1.4
numpy==1.26.2
Sastrawi==1.0.1
Werkzeug==3.0.1
```

#### 📄 API.md
Complete API documentation:
- Endpoint descriptions
- Request/response formats
- Examples (cURL, Python, JavaScript)
- Error handling
- Best practices

#### 📄 DATASET.md
Dataset documentation:
- Data sources
- Format specification
- Characteristics
- How to add data
- Preprocessing pipeline

#### 📁 models/
Stores trained models:
- `fake_news_cnn_model.h5`: CNN model weights
- `tfidf_vectorizer.pkl`: TF-IDF vectorizer

#### 📁 data/
Stores datasets:
- `fake_news_dataset.csv`: Training data

---

### Frontend Files

#### 📄 package.json
Node.js dependencies and scripts:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.2.0",
    "lucide-react": "^0.562.0"
  }
}
```

#### 📄 vite.config.ts
Vite configuration:
- React plugin
- Build settings
- Server configuration

#### 📄 tsconfig.json
TypeScript compiler options:
- Target: ES2020
- Module: ESNext
- JSX: react-jsx
- Strict mode enabled

#### 📄 tailwind.config.js
Tailwind CSS configuration:
- Custom colors
- Custom utilities
- Plugin settings

#### 📄 index.html
HTML entry point:
- Root div
- Script imports
- Meta tags

#### 📄 src/main.tsx
Application entry point:
```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

#### 📄 src/App.tsx
Main app component:
```tsx
import FakeNewsDetector from './views/FakeNewsDetector'

function App() {
  return <FakeNewsDetector />
}
```

#### 📄 src/index.css
Global styles:
- Tailwind imports
- Custom animations
- Scrollbar styles
- Utility classes

#### 📄 src/views/FakeNewsDetector.tsx
Main detector page (500+ lines):
- State management
- API integration
- UI components
- Statistics tracking
- Analysis history
- Feedback system

**Components:**
1. Statistics Bar (Total/Fake/Real counts)
2. Header Section
3. Input Section (textarea + examples)
4. Result Section (prediction + details)
5. Sidebar:
   - Analysis History
   - System Information
   - Hoax Indicators
   - Training Data/Feedback

---

## Data Flow

```
User Input (Frontend)
    ↓
POST /analyze (API Request)
    ↓
Flask Backend (app.py)
    ↓
Text Preprocessing
    ↓
TF-IDF Vectorization
    ↓
CNN Model Prediction
    ↓
Hoax Indicators Calculation
    ↓
Response (JSON)
    ↓
Display Results (Frontend)
```

---

## Development Workflow

### 1. Initial Setup
```bash
# Run setup script
setup.bat

# Or manual:
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd ..\frontend
npm install
```

### 2. Train Model (First Time)
```bash
# Run train script
train.bat

# Or manual:
cd backend
venv\Scripts\activate
python train_model.py
```

### 3. Development
```bash
# Start both servers
start.bat

# Or manual:
# Terminal 1 (Backend):
cd backend
venv\Scripts\activate
python app.py

# Terminal 2 (Frontend):
cd frontend
npm run dev
```

### 4. Testing
```bash
# Test backend
curl http://localhost:5000/health

# Test frontend
# Open http://localhost:5173
```

### 5. Build for Production
```bash
# Backend: Use gunicorn or similar
pip install gunicorn
gunicorn app:app

# Frontend:
cd frontend
npm run build
# Output in dist/
```

---

## Key Technologies

### Backend
- **Flask**: Web framework
- **TensorFlow/Keras**: Deep learning
- **scikit-learn**: ML utilities, TF-IDF
- **Sastrawi**: Indonesian NLP
- **pandas**: Data manipulation
- **NumPy**: Numerical computing

### Frontend
- **React 19**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Lucide React**: Icons

---

## Environment Variables

### Backend (.env)
```env
FLASK_ENV=development
FLASK_DEBUG=1
MODEL_PATH=models/fake_news_cnn_model.h5
VECTORIZER_PATH=models/tfidf_vectorizer.pkl
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000
```

---

## Database Schema (Optional)

For storing analysis results:

```sql
CREATE TABLE analyses (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    prediction VARCHAR(10) NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE feedback (
    id INTEGER PRIMARY KEY,
    analysis_id INTEGER,
    user_feedback VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);
```

---

## Performance Considerations

### Backend
- Model loading time: ~2-3 seconds (first request)
- Analysis time: ~50-200ms per text
- Memory usage: ~500MB (with model loaded)

### Frontend
- Initial load: ~1-2 seconds
- Bundle size: ~500KB (gzipped)
- Lighthouse score: 90+ (all metrics)

---

## Security Checklist

- [ ] Input validation
- [ ] XSS protection
- [ ] CORS configuration
- [ ] Rate limiting
- [ ] API authentication
- [ ] HTTPS in production
- [ ] Environment variables
- [ ] SQL injection prevention (if using DB)
- [ ] File upload restrictions
- [ ] Error message sanitization

---

## Maintenance

### Regular Tasks
1. Update dependencies monthly
2. Retrain model quarterly
3. Add new hoax patterns
4. Update dataset
5. Monitor performance
6. Review user feedback
7. Update documentation

### Backup
- Model files
- Dataset
- Configuration files
- Analysis logs (if any)

---

## Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check Python version (3.8+)
   - Verify virtual environment activated
   - Install dependencies
   - Check port 5000 availability

2. **Model not loading**
   - Run `train.bat` first
   - Check models/ directory exists
   - Verify file permissions

3. **Frontend errors**
   - Check Node.js version (16+)
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check backend is running

4. **CORS errors**
   - Verify flask-cors installed
   - Check backend CORS configuration
   - Verify API URL in frontend

---

## License

MIT License - See LICENSE file

---

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

**Last Updated:** December 2024
