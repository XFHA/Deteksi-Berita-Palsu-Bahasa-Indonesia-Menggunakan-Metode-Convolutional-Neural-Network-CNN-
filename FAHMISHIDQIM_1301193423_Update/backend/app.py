import os
import re
import pickle
import threading
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import validators
from werkzeug.utils import secure_filename
import warnings

warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'datasets'
ALLOWED_EXTENSIONS = {'csv', 'txt', 'json', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs('datasets', exist_ok=True)
os.makedirs('models', exist_ok=True)

print("[*] Menginisialisasi Sastrawi NLP...")
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

stopword_factory = StopWordRemoverFactory()
stopword_remover = stopword_factory.create_stop_word_remover()

model = None
vectorizer = None

def load_resources():
    global model, vectorizer
    model_path = 'models/fake_news_cnn_model.h5'
    vectorizer_path = 'models/tokenizer.pickle'
    
    if os.path.exists(model_path):
        try:
            model = keras.models.load_model(model_path)
            print("[*] Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            model = None
            
    if os.path.exists(vectorizer_path):
        try:
            with open(vectorizer_path, 'rb') as f:
                vectorizer = pickle.load(f)
            print("[*] Tokenizer loaded successfully")
        except Exception as e:
            print(f"Error loading tokenizer: {e}")
            vectorizer = None

load_resources()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_text(text):
    text = clean_text(text)
    text = stopword_remover.remove(text)
    text = stemmer.stem(text)
    return text

def predict_fake_news(text):
    if model is None or vectorizer is None:
        return None
    
    analysis_steps = []
    
    # Text Cleaning
    step1_text = clean_text(text)
    analysis_steps.append({
        "step": "Text Cleaning & Case Folding",
        "status": "completed",
        "message": "Menghapus URL, karakter khusus, dan mengubah huruf kecil.",
        "details": {
            "before": text[:150] + ("..." if len(text) > 150 else ""),
            "after": step1_text[:150] + ("..." if len(step1_text) > 150 else "")
        }
    })
    
    # Stopword Removal
    step2_text = stopword_remover.remove(step1_text)
    analysis_steps.append({
        "step": "Stopword Removal (Sastrawi)",
        "status": "completed",
        "message": "Menghapus kata hubung/stopword.",
        "details": {
            "before": step1_text[:150] + ("..." if len(step1_text) > 150 else ""),
            "after": step2_text[:150] + ("..." if len(step2_text) > 150 else "")
        }
    })
    
    # Stemming
    step3_text = stemmer.stem(step2_text)
    analysis_steps.append({
        "step": "Stemming (Sastrawi)",
        "status": "completed",
        "message": "Mengubah kata berimbuhan menjadi kata dasar.",
        "details": {
            "before": step2_text[:150] + ("..." if len(step2_text) > 150 else ""),
            "after": step3_text[:150] + ("..." if len(step3_text) > 150 else "")
        }
    })

    processed_text = step3_text
    
    seq = vectorizer.texts_to_sequences([processed_text])
    padded_seq = pad_sequences(seq, maxlen=50, padding='post')
    
    prediction = model.predict(padded_seq, verbose=0)
    fake_confidence = float(prediction[0][0])
    real_confidence = 1.0 - fake_confidence
    
    analysis_steps.append({
        "step": "CNN Prediction",
        "status": "completed",
        "message": "Menggunakan TensorFlow Keras untuk ekstraksi fitur (Embedding, Conv1D, GlobalMaxPooling1D).",
        "details": None
    })
    
    return {
        'fake_confidence': fake_confidence,
        'real_confidence': real_confidence,
        'prediction': 'fake' if fake_confidence > 0.5 else 'real',
        'processed_text': processed_text,
        'word_count': len(text.split()),
        'analysis_steps': analysis_steps
    }

def scrape_url(url):
    try:
        article = Article(url, language='id')
        article.download()
        article.parse()
        if article.text and len(article.text) > 100:
            return {
                'success': True,
                'title': article.title,
                'text': article.text,
                'authors': article.authors,
                'publish_date': str(article.publish_date) if article.publish_date else None,
                'image_url': article.top_image,
                'method': 'newspaper3k'
            }
    except Exception:
        pass

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
        if len(text) > 100:
            return {
                'success': True,
                'title': soup.title.string if soup.title else 'No Title',
                'text': text,
                'authors': [],
                'publish_date': None,
                'image_url': None,
                'method': 'beautifulsoup'
            }
    except Exception as e:
        return {'error': str(e)}
        
    return {'error': 'Failed to scrape content'}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None,
        "detection_method": "CNN" if model else "Rule-based",
        "features": ["text_analysis", "url_scraping", "dataset_management"]
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    res = predict_fake_news(data['text'])
    if not res:
        return jsonify({'error': 'Model is not loaded. Train the model first.'}), 500
        
    return jsonify({
        "prediction": res['prediction'],
        "confidence": res['fake_confidence'] if res['prediction'] == 'fake' else res['real_confidence'],
        "fake_score": res['fake_confidence'] * 100,
        "real_score": res['real_confidence'] * 100,
        "word_count": res['word_count'],
        "processed_text": res['processed_text'],
        "indicators": {},
        "hoax_indicator_score": 0,
        "detection_method": "CNN",
        "source": "manual_text_input",
        "recommendations": [
            "Sangat disarankan untuk TIDAK menyebarkan berita ini" if res['prediction'] == 'fake' else "Berita tampak kredibel",
            "Cek sumber berita dari website resmi",
            "Verifikasi ke situs fact-checking seperti TurnBackHoax"
        ],
        "analysis_steps": res['analysis_steps']
    })

@app.route('/analyze-url', methods=['POST'])
def analyze_url():
    data = request.json
    if not data or 'url' not in data:
        return jsonify({'error': 'No url provided'}), 400
    
    scrape_res = scrape_url(data['url'])
    if 'error' in scrape_res:
        return jsonify({'error': scrape_res['error']}), 400
        
    combined_text = f"{scrape_res['title']} {scrape_res['text']}"
    res = predict_fake_news(combined_text)
    
    if not res:
        return jsonify({'error': 'Model is not loaded. Train the model first.'}), 500
        
    return jsonify({
        "prediction": res['prediction'],
        "confidence": res['fake_confidence'] if res['prediction'] == 'fake' else res['real_confidence'],
        "fake_score": res['fake_confidence'] * 100,
        "real_score": res['real_confidence'] * 100,
        "word_count": res['word_count'],
        "processed_text": res['processed_text'],
        "indicators": {},
        "hoax_indicator_score": 0,
        "detection_method": "CNN",
        "source": "url_scraping",
        "source_info": {
            "url": data['url'],
            "title": scrape_res['title'],
            "scraping_method": scrape_res['method'],
            "authors": scrape_res['authors'],
            "publish_date": scrape_res['publish_date'],
            "image_url": scrape_res['image_url'],
            "original_word_count": len(combined_text.split())
        },
        "recommendations": [
            "Sangat disarankan untuk TIDAK menyebarkan berita ini" if res['prediction'] == 'fake' else "Berita tampak kredibel",
            "Cek sumber berita dari website resmi",
            "Verifikasi ke situs fact-checking seperti TurnBackHoax"
        ],
        "analysis_steps": res['analysis_steps']
    })

@app.route('/upload-dataset', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({
            "success": True,
            "message": "Dataset uploaded successfully",
            "filename": filename,
            "size": os.path.getsize(filepath),
            "path": filepath
        })
    return jsonify({'error': 'Invalid file type. Allowed: csv, txt, json, xlsx'}), 400

@app.route('/datasets', methods=['GET'])
def list_datasets():
    datasets = []
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f)
        if os.path.isfile(filepath):
            datasets.append({
                "filename": f,
                "size": os.path.getsize(filepath),
                "upload_date": datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
                "original_filename": f.split('_', 2)[-1] if '_' in f else f
            })
    return jsonify({"datasets": datasets})

@app.route('/delete-dataset/<filename>', methods=['DELETE'])
def delete_dataset(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"success": True, "message": "Dataset deleted successfully"})
    return jsonify({"error": "Dataset not found"}), 404

@app.route('/batch-analyze', methods=['POST'])
def batch_analyze():
    data = request.json
    if not data or 'texts' not in data:
        return jsonify({'error': 'No texts provided'}), 400
        
    results = []
    for text in data['texts'][:50]:
        res = predict_fake_news(text)
        if res:
            results.append({
                "prediction": res['prediction'],
                "confidence": res['fake_confidence'] if res['prediction'] == 'fake' else res['real_confidence'],
                "fake_score": res['fake_confidence'] * 100,
                "real_score": res['real_confidence'] * 100
            })
    return jsonify({"results": results})

@app.route('/stats', methods=['GET'])
def get_stats():
    datasets_count = len(os.listdir(app.config['UPLOAD_FOLDER']))
    return jsonify({
        "model_type": "CNN (Convolutional Neural Network)",
        "feature_extraction": "Keras Tokenizer",
        "preprocessing_steps": [
            "Text Cleaning",
            "Case Folding",
            "Slang Normalization",
            "Stopword Removal",
            "Stemming (Sastrawi)"
        ],
        "supported_language": "Indonesian",
        "max_text_length": 50,
        "model_status": "loaded" if model else "not loaded",
        "features": {
            "text_analysis": True,
            "url_scraping": True,
            "dataset_management": True
        },
        "datasets_count": datasets_count
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
