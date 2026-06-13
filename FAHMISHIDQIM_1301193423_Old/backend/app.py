import os
import re
import pickle
import numpy as np
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.feature_extraction.text import TfidfVectorizer
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import requests
from bs4 import BeautifulSoup
import validators
from newspaper import Article
from werkzeug.utils import secure_filename
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'datasets'
ALLOWED_EXTENSIONS = {'csv', 'txt', 'json'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create necessary directories
os.makedirs('datasets', exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Initialize Indonesian NLP tools
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

stopword_factory = StopWordRemoverFactory()
stopword_remover = stopword_factory.create_stop_word_remover()

# Load slang dictionary from CSV file
def load_slang_dictionary():
    """Load Indonesian slang dictionary from CSV file"""
    slang_dict = {}
    slang_file = 'data/slang_dictionary.csv'
    
    if os.path.exists(slang_file):
        try:
            import csv
            with open(slang_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 2:
                        slang_dict[row[0]] = row[1]
            print(f"✓ Loaded {len(slang_dict)} slang words from {slang_file}")
        except Exception as e:
            print(f"⚠ Error loading slang dictionary: {e}")
    else:
        print(f"⚠ Slang dictionary not found at {slang_file}")
    
    return slang_dict

# Load hoax keywords from CSV file
def load_hoax_keywords():
    """Load hoax indicator keywords from CSV file"""
    keywords = []
    keywords_file = 'data/hoax_keywords.csv'
    
    if os.path.exists(keywords_file):
        try:
            with open(keywords_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                keywords = [kw.strip() for kw in content.split(',')]
            print(f"✓ Loaded {len(keywords)} hoax keywords from {keywords_file}")
        except Exception as e:
            print(f"⚠ Error loading hoax keywords: {e}")
    else:
        print(f"⚠ Hoax keywords not found at {keywords_file}")
    
    return keywords

# Load example news from CSV file
def load_example_news():
    """Load example news from CSV file"""
    examples = []
    examples_file = 'data/example_news.csv'
    
    if os.path.exists(examples_file):
        try:
            import pandas as pd
            df = pd.read_csv(examples_file)
            for _, row in df.iterrows():
                examples.append({
                    'text': row['text'],
                    'label': 'fake' if row['label'] == 1 else 'real',
                    'source': row.get('source', 'unknown')
                })
            print(f"✓ Loaded {len(examples)} example news from {examples_file}")
        except Exception as e:
            print(f"⚠ Error loading example news: {e}")
    else:
        print(f"⚠ Example news not found at {examples_file}")
    
    return examples

# Load data from files
slang_dict = load_slang_dictionary()
hoax_keywords = load_hoax_keywords()
example_news = load_example_news()

# Global variables for model and tokenizer
model = None
tokenizer = None
MAX_LENGTH = 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def scrape_article_from_url(url):
    """
    Scrape article content from URL with multi-page support
    """
    try:
        # Validate URL
        if not validators.url(url):
            return {'error': 'Invalid URL format'}
        
        # Try to force single-page view for known portals
        single_page_url = url
        if 'kompas.com' in url.lower() and '?page=' not in url:
            single_page_url = url.split('?')[0] + '?page=all'
        elif 'tribunnews.com' in url.lower() and '?page=' not in url:
            single_page_url = url + '?page=all' if '?' not in url else url + '&page=all'
        
        # Try newspaper3k first (best for news articles)
        try:
            article = Article(single_page_url, language='id')
            article.download()
            article.parse()
            
            # Validate article content (relaxed to 150 chars)
            if article.text and len(article.text) > 150:
                # Remove common junk content
                text = article.text
                
                # Filter out common non-article content
                junk_phrases = [
                    'detiknetwork adalah bagian dari',
                    'untuk bantuan daftar dan masuk',
                    'buat akun mpc',
                    'satu akun mpc untuk',
                    'ct corp',
                    'klik di sini untuk',
                    'tonton video lainnya',
                    'scroll to continue',
                    'baca juga:',
                    'lihat juga:',
                    'halaman selanjutnya'
                ]
                
                text_lower = text.lower()
                # Only filter if there's significant junk (more than 3 phrases)
                junk_count = sum(1 for junk in junk_phrases if junk in text_lower)
                if junk_count > 3:
                    # Try to extract only main content paragraphs
                    lines = text.split('\n')
                    filtered_lines = []
                    for line in lines:
                        line_lower = line.lower()
                        if not any(junk in line_lower for junk in junk_phrases) and len(line) > 40:
                            filtered_lines.append(line)
                    
                    text = '\n'.join(filtered_lines)
                
                # Final validation (150 chars minimum)
                if len(text) > 150:
                    return {
                        'success': True,
                        'title': article.title or 'No title found',
                        'text': text,
                        'authors': article.authors,
                        'publish_date': str(article.publish_date) if article.publish_date else None,
                        'url': url,
                        'method': 'newspaper3k',
                        'image_url': article.top_image or None,
                        'word_count': len(text.split())
                    }
        except Exception as e:
            print(f"Newspaper3k failed: {e}")
        
        # Fallback to BeautifulSoup with multi-page support
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Try single-page URL first for BeautifulSoup
        all_content = []
        current_url = single_page_url
        max_pages = 5  # Limit to prevent infinite loop
        pages_scraped = 0
        
        while pages_scraped < max_pages:
            try:
                response = requests.get(current_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    script.decompose()
                
                # Try to find article title (only on first page)
                if pages_scraped == 0:
                    title = None
                    title_tags = soup.find_all(['h1', 'title'])
                    if title_tags:
                        title = title_tags[0].get_text().strip()
                
                # Try to find main content
                content = ''
                
                # Common article container classes/ids
                article_selectors = [
                    {'class': ['article-content', 'post-content', 'entry-content', 'content', 'main-content', 'article__content', 'read__content']},
                    {'id': ['article', 'content', 'main', 'post']},
                    ['article', 'main']
                ]
                
                for selector in article_selectors:
                    if isinstance(selector, dict):
                        if 'class' in selector:
                            for class_name in selector['class']:
                                element = soup.find(class_=class_name)
                                if element:
                                    content = element.get_text(separator='\n', strip=True)
                                    break
                        elif 'id' in selector:
                            for id_name in selector['id']:
                                element = soup.find(id=id_name)
                                if element:
                                    content = element.get_text(separator='\n', strip=True)
                                    break
                    else:
                        for tag in selector:
                            element = soup.find(tag)
                            if element:
                                content = element.get_text(separator='\n', strip=True)
                                break
                    
                    if len(content) > 100:
                        break
                
                # If still no content, get all paragraphs
                if len(content) < 100:
                    paragraphs = soup.find_all('p')
                    content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
                
                if content:
                    all_content.append(content)
                
                # Check for pagination - look for next page link
                next_page = None
                
                # Common pagination patterns
                pagination_links = soup.find_all('a', href=True)
                for link in pagination_links:
                    link_text = link.get_text().lower().strip()
                    link_href = link.get('href', '')
                    
                    # Check for next page indicators
                    if any(indicator in link_text for indicator in ['selanjutnya', 'next', 'berikutnya', '›', '»']):
                        if link_href.startswith('/'):
                            from urllib.parse import urljoin
                            next_page = urljoin(url, link_href)
                        elif link_href.startswith('http'):
                            next_page = link_href
                        break
                    
                    # Check for page number links (e.g., ?page=2, ?page=3)
                    if 'page=' in link_href or '/page/' in link_href:
                        # Only follow if it's the next sequential page
                        if pages_scraped == 0:  # On first page, look for page 2
                            if 'page=2' in link_href or '/page/2' in link_href:
                                if link_href.startswith('/'):
                                    from urllib.parse import urljoin
                                    next_page = urljoin(url, link_href)
                                elif link_href.startswith('http'):
                                    next_page = link_href
                                break
                
                pages_scraped += 1
                
                # If no next page or already got page=all, stop
                if not next_page or 'page=all' in current_url:
                    break
                    
                current_url = next_page
                
            except Exception as e:
                print(f"Error scraping page {pages_scraped + 1}: {e}")
                break
        
        # Combine all content from multiple pages
        combined_content = '\n\n'.join(all_content)
        
        if len(combined_content) < 50:
            return {'error': 'Could not extract sufficient content from URL'}
        
        if pages_scraped > 1:
            print(f"✓ Scraped {pages_scraped} pages from article")
        
        return {
            'success': True,
            'title': title or 'No title found',
            'text': combined_content,
            'url': url,
            'method': f'beautifulsoup ({pages_scraped} pages)',
            'word_count': len(combined_content.split())
        }
        
    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to fetch URL: {str(e)}'}
    except Exception as e:
        return {'error': f'Error scraping article: {str(e)}'}

def preprocess_text(text, track_steps=False):
    """
    Comprehensive Indonesian text preprocessing with optional step tracking
    """
    steps = [] if track_steps else None
    original_text = text
    
    # Step 1: Convert to lowercase
    text = text.lower()
    if track_steps:
        steps.append({
            'step': 1,
            'name': 'Case Folding',
            'description': 'Mengubah semua huruf menjadi lowercase',
            'before': original_text[:100],
            'after': text[:100],
            'changes_count': sum(1 for a, b in zip(original_text, text) if a != b)
        })
    
    # Step 2: Remove URLs
    before = text
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    if track_steps:
        url_count = len(re.findall(r'http\S+|www\S+|https\S+', before))
        steps.append({
            'step': 2,
            'name': 'Remove URLs',
            'description': 'Menghapus semua URL dari teks',
            'removed_count': url_count,
            'after': text[:100]
        })
    
    # Step 3: Remove mentions and hashtags
    before = text
    text = re.sub(r'@\w+|#\w+', '', text)
    if track_steps:
        mention_count = len(re.findall(r'@\w+|#\w+', before))
        steps.append({
            'step': 3,
            'name': 'Remove Mentions & Hashtags',
            'description': 'Menghapus @mentions dan #hashtags',
            'removed_count': mention_count,
            'after': text[:100]
        })
    
    # Step 4: Remove special characters and numbers
    before = text
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    if track_steps:
        special_count = len(re.findall(r'[^a-zA-Z\s]', before))
        steps.append({
            'step': 4,
            'name': 'Remove Special Characters',
            'description': 'Menghapus karakter spesial, angka, dan tanda baca',
            'removed_count': special_count,
            'after': text[:100]
        })
    
    # Step 5: Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Step 6: Replace slang words
    words = text.split()
    original_words = words.copy()
    words = [slang_dict.get(word, word) for word in words]
    text = ' '.join(words)
    if track_steps:
        slang_replaced = sum(1 for a, b in zip(original_words, words) if a != b)
        steps.append({
            'step': 5,
            'name': 'Slang Normalization',
            'description': 'Mengganti kata slang dengan kata baku',
            'replaced_count': slang_replaced,
            'examples': [f"{original_words[i]} → {words[i]}" for i in range(len(words)) if original_words[i] != words[i]][:5],
            'after': text[:100]
        })
    
    # Step 7: Remove stopwords
    before = text
    before_words = len(text.split())
    text = stopword_remover.remove(text)
    if track_steps:
        after_words = len(text.split())
        steps.append({
            'step': 6,
            'name': 'Stopword Removal',
            'description': 'Menghapus kata-kata umum yang tidak penting',
            'before_word_count': before_words,
            'after_word_count': after_words,
            'removed_count': before_words - after_words,
            'after': text[:100]
        })
    
    # Step 8: Stemming
    before = text
    text = stemmer.stem(text)
    if track_steps:
        steps.append({
            'step': 7,
            'name': 'Stemming',
            'description': 'Mengubah kata ke bentuk dasar (root word)',
            'before': before[:100],
            'after': text[:100]
        })
    
    if track_steps:
        return text, steps
    return text

def calculate_hoax_indicators(original_text):
    """
    Calculate various hoax indicators from the original text
    """
    # Find which hoax keywords are present
    found_keywords = [keyword for keyword in hoax_keywords if keyword.lower() in original_text.lower()]
    
    indicators = {
        'exclamation_marks': original_text.count('!'),
        'all_caps_words': len([w for w in original_text.split() if w.isupper() and len(w) > 2]),
        'hoax_keywords': len(found_keywords),
        'keywords_found': found_keywords,
        'question_marks': original_text.count('?'),
        'url_count': len(re.findall(r'http\S+|www\S+', original_text)),
    }
    
    # Calculate hoax score based on indicators
    hoax_score = (
        indicators['exclamation_marks'] * 2 +
        indicators['all_caps_words'] * 3 +
        indicators['hoax_keywords'] * 5 +
        indicators['question_marks'] * 1 +
        indicators['url_count'] * -2  # URLs might indicate credible sources
    )
    
    return indicators, max(0, min(100, hoax_score))

def load_model_and_vectorizer():
    """
    Load pre-trained model and tokenizer
    """
    global model, tokenizer
    
    model_path = 'models/fake_news_cnn_model.h5'
    vectorizer_path = 'models/tokenizer.pkl'
    
    # Check if model exists
    if os.path.exists(model_path):
        try:
            model = keras.models.load_model(model_path)
            print("✓ Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            model = None
    else:
        print(f"⚠ Model not found at {model_path}")
        print("⚠ Using rule-based detection")
        model = None
    
    # Check if tokenizer exists
    if os.path.exists(vectorizer_path):
        try:
            with open(vectorizer_path, 'rb') as f:
                tokenizer = pickle.load(f)
            print("✓ Tokenizer loaded successfully")
        except Exception as e:
            print(f"Error loading tokenizer: {e}")
            tokenizer = None
    else:
        print(f"⚠ Tokenizer not found at {vectorizer_path}")
        tokenizer = None

def predict_with_cnn(text):
    """
    Predict using CNN model with Word Embedding features
    """
    if model is None or tokenizer is None:
        return None
    
    try:
        # Preprocess text
        processed_text = preprocess_text(text)
        
        # Transform using Tokenizer and pad sequences
        seq = tokenizer.texts_to_sequences([processed_text])
        padded_seq = pad_sequences(seq, maxlen=50, padding='post')
        
        # Make prediction
        prediction = model.predict(padded_seq, verbose=0)
        
        # Get confidence scores
        fake_confidence = float(prediction[0][0])
        real_confidence = 1.0 - fake_confidence
        
        return {
            'fake_confidence': fake_confidence,
            'real_confidence': real_confidence,
            'prediction': 'fake' if fake_confidence > 0.5 else 'real'
        }
    except Exception as e:
        print(f"Error in CNN prediction: {e}")
        return None

def rule_based_prediction(text, hoax_score):
    """
    Rule-based prediction as fallback
    """
    processed_text = preprocess_text(text)
    word_count = len(processed_text.split())
    
    # Calculate fake probability based on various factors
    fake_probability = 0.5
    
    # Very short text is suspicious
    if word_count < 10:
        fake_probability += 0.2
    
    # Hoax score influence
    fake_probability += (hoax_score / 100) * 0.3
    
    # Check for hoax keywords in original text
    text_lower = text.lower()
    keyword_count = sum([1 for keyword in hoax_keywords if keyword in text_lower])
    if keyword_count > 2:
        fake_probability += 0.15
    
    # Multiple exclamation marks
    if text.count('!') > 3:
        fake_probability += 0.1
    
    # All caps words
    all_caps_count = len([w for w in text.split() if w.isupper() and len(w) > 2])
    if all_caps_count > 2:
        fake_probability += 0.1
    
    # Cap the probability
    fake_probability = min(0.95, max(0.05, fake_probability))
    
    return {
        'fake_confidence': fake_probability,
        'real_confidence': 1.0 - fake_probability,
        'prediction': 'fake' if fake_probability > 0.5 else 'real'
    }

def get_recommendations(prediction, confidence):
    """
    Provide recommendations based on prediction
    """
    if prediction == 'fake':
        if confidence > 0.8:
            return [
                "Sangat disarankan untuk TIDAK menyebarkan berita ini",
                "Cek sumber berita dari website resmi",
                "Verifikasi ke situs fact-checking seperti TurnBackHoax",
                "Laporkan jika terbukti hoax"
            ]
        else:
            return [
                "Berita ini berpotensi palsu, cek sumbernya",
                "Verifikasi dari beberapa sumber terpercaya",
                "Jangan langsung menyebarkan"
            ]
    else:
        if confidence > 0.8:
            return [
                "Berita tampak kredibel",
                "Tetap cek sumber aslinya",
                "Perhatikan tanggal publikasi"
            ]
        else:
            return [
                "Berita mungkin asli tapi tetap perlu verifikasi",
                "Cek dari beberapa sumber media terpercaya",
                "Pastikan informasinya up-to-date"
            ]

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'model_loaded': model is not None,
        'tokenizer_loaded': tokenizer is not None,
        'detection_method': 'CNN + Word Embedding' if model else 'Rule-based',
        'features': ['text_analysis', 'url_scraping', 'dataset_management']
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Main endpoint for fake news analysis (text input)
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        original_text = data['text']
        
        if len(original_text.strip()) < 10:
            return jsonify({'error': 'Text too short (minimum 10 characters)'}), 400
        
        # Track analysis steps
        analysis_steps = []
        
        # Step 1: Text preprocessing with step tracking
        processed_text, preprocessing_steps = preprocess_text(original_text, track_steps=True)
        word_count = len(processed_text.split())
        analysis_steps.append({
            'step': 'preprocessing',
            'status': 'completed',
            'message': f'Preprocessing selesai - {word_count} kata tersisa',
            'details': {'substeps': preprocessing_steps}
        })
        
        # Step 2: Calculate hoax indicators
        indicators, hoax_score = calculate_hoax_indicators(original_text)
        analysis_steps.append({
            'step': 'indicators',
            'status': 'completed',
            'message': f'Ditemukan {indicators["hoax_keywords"]} kata kunci hoax',
            'details': indicators
        })
        
        # Step 3: Model prediction
        
        # Try CNN prediction first
        cnn_result = predict_with_cnn(original_text)
        
        if cnn_result:
            prediction_result = cnn_result
            method = 'CNN + Word Embedding'
            analysis_steps.append({
                'step': 'prediction',
                'status': 'completed',
                'message': 'Prediksi menggunakan CNN model',
                'method': method
            })
        else:
            # Fallback to rule-based
            prediction_result = rule_based_prediction(original_text, hoax_score)
            method = 'Rule-based'
            analysis_steps.append({
                'step': 'prediction',
                'status': 'completed',
                'message': 'Prediksi menggunakan rule-based (model belum di-train)',
                'method': method
            })
        
        # Prepare response
        response = {
            'prediction': prediction_result['prediction'],
            'confidence': prediction_result['fake_confidence'] if prediction_result['prediction'] == 'fake' else prediction_result['real_confidence'],
            'fake_score': round(prediction_result['fake_confidence'] * 100, 2),
            'real_score': round(prediction_result['real_confidence'] * 100, 2),
            'word_count': word_count,
            'processed_text': processed_text[:200] + ('...' if len(processed_text) > 200 else ''),
            'indicators': indicators,
            'hoax_indicator_score': hoax_score,
            'detection_method': method,
            'source': 'manual_text_input',
            'analysis_steps': analysis_steps,  # Include detailed steps
            'recommendations': get_recommendations(prediction_result['prediction'], prediction_result['fake_confidence'])
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error in analyze: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-url', methods=['POST'])
def analyze_url():
    """
    Analyze fake news from URL (scrape and analyze)
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        url = data['url'].strip()
        
        # Track analysis steps
        analysis_steps = []
        
        # Step 1: Scrape article
        
        scrape_result = scrape_article_from_url(url)
        
        if 'error' in scrape_result:
            return jsonify(scrape_result), 400
        
        # Get the scraped text
        original_text = scrape_result['text']
        title = scrape_result.get('title', '')
        
        analysis_steps.append({
            'step': 'scraping',
            'status': 'completed',
            'message': f'Artikel berhasil diambil - {scrape_result.get("word_count", 0)} kata',
            'details': {
                'title': title,
                'method': scrape_result.get('method'),
                'word_count': scrape_result.get('word_count', len(original_text.split()))
            }
        })
        
        # Combine title and text for analysis
        full_text = f"{title} {original_text}"
        
        if len(full_text.strip()) < 10:
            return jsonify({'error': 'Scraped content too short'}), 400
        
        # Step 2: Preprocess text
        processed_text, preprocessing_steps = preprocess_text(full_text, track_steps=True)
        word_count = len(processed_text.split())
        analysis_steps.append({
            'step': 'preprocessing',
            'status': 'completed',
            'message': f'Preprocessing selesai - {word_count} kata tersisa',
            'details': {'substeps': preprocessing_steps}
        })
        
        # Step 3: Calculate hoax indicators
        indicators, hoax_score = calculate_hoax_indicators(full_text)
        analysis_steps.append({
            'step': 'indicators',
            'status': 'completed',
            'message': f'Ditemukan {indicators["hoax_keywords"]} kata kunci hoax',
            'details': indicators
        })
        
        # Step 4: Model prediction
        
        # Try CNN prediction first
        cnn_result = predict_with_cnn(full_text)
        
        if cnn_result:
            prediction_result = cnn_result
            method = 'CNN + Word Embedding'
            analysis_steps.append({
                'step': 'prediction',
                'status': 'completed',
                'message': 'Prediksi menggunakan CNN model',
                'method': method
            })
        else:
            # Fallback to rule-based
            prediction_result = rule_based_prediction(full_text, hoax_score)
            method = 'Rule-based'
            analysis_steps.append({
                'step': 'prediction',
                'status': 'completed',
                'message': 'Prediksi menggunakan rule-based (model belum di-train)',
                'method': method
            })
        
        # Prepare response with source information
        response = {
            'prediction': prediction_result['prediction'],
            'confidence': prediction_result['fake_confidence'] if prediction_result['prediction'] == 'fake' else prediction_result['real_confidence'],
            'fake_score': round(prediction_result['fake_confidence'] * 100, 2),
            'real_score': round(prediction_result['real_confidence'] * 100, 2),
            'word_count': word_count,
            'processed_text': processed_text[:200] + ('...' if len(processed_text) > 200 else ''),
            'indicators': indicators,
            'hoax_indicator_score': hoax_score,
            'detection_method': method,
            'source': 'url_scraping',
            'source_info': {
                'url': url,
                'title': title,
                'scraping_method': scrape_result.get('method'),
                'authors': scrape_result.get('authors', []),
                'publish_date': scrape_result.get('publish_date'),
                'image_url': scrape_result.get('image_url'),
                'original_word_count': scrape_result.get('word_count', len(original_text.split()))
            },
            'analysis_steps': analysis_steps,
            'recommendations': get_recommendations(prediction_result['prediction'], prediction_result['fake_confidence'])
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error in analyze-url: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload-dataset', methods=['POST'])
def upload_dataset():
    """
    Upload dataset for training
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get file info
        file_size = os.path.getsize(filepath)
        
        # Save metadata
        metadata = {
            'filename': filename,
            'original_filename': file.filename,
            'upload_date': datetime.now().isoformat(),
            'size': file_size,
            'path': filepath
        }
        
        metadata_path = filepath + '.meta.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Dataset uploaded successfully',
            'filename': filename,
            'size': file_size,
            'path': filepath
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/datasets', methods=['GET'])
def list_datasets():
    """
    List all uploaded datasets
    """
    try:
        datasets = []
        
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            return jsonify({'datasets': []})
        
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.endswith('.meta.json'):
                continue
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            metadata_path = filepath + '.meta.json'
            
            if os.path.isfile(filepath):
                # Try to load metadata
                metadata = {}
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                    except:
                        pass
                
                dataset_info = {
                    'filename': filename,
                    'size': os.path.getsize(filepath),
                    'upload_date': metadata.get('upload_date', 'Unknown'),
                    'original_filename': metadata.get('original_filename', filename)
                }
                
                datasets.append(dataset_info)
        
        # Sort by upload date (newest first)
        datasets.sort(key=lambda x: x['upload_date'], reverse=True)
        
        return jsonify({'datasets': datasets})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete-dataset/<filename>', methods=['DELETE'])
def delete_dataset(filename):
    """
    Delete a dataset file
    """
    try:
        # Secure the filename
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        metadata_path = filepath + '.meta.json'
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Delete file and metadata
        os.remove(filepath)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        
        return jsonify({
            'success': True,
            'message': 'Dataset deleted successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch-analyze', methods=['POST'])
def batch_analyze():
    """
    Analyze multiple texts at once
    """
    try:
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({'error': 'No texts provided'}), 400
        
        texts = data['texts']
        
        if not isinstance(texts, list):
            return jsonify({'error': 'texts must be a list'}), 400
        
        if len(texts) > 50:
            return jsonify({'error': 'Maximum 50 texts per batch'}), 400
        
        results = []
        for text in texts:
            if len(text.strip()) < 10:
                results.append({'error': 'Text too short'})
                continue
            
            # Analyze each text
            processed_text = preprocess_text(text)
            indicators, hoax_score = calculate_hoax_indicators(text)
            
            cnn_result = predict_with_cnn(text)
            if cnn_result:
                prediction_result = cnn_result
            else:
                prediction_result = rule_based_prediction(text, hoax_score)
            
            results.append({
                'prediction': prediction_result['prediction'],
                'confidence': prediction_result['fake_confidence'] if prediction_result['prediction'] == 'fake' else prediction_result['real_confidence'],
                'fake_score': round(prediction_result['fake_confidence'] * 100, 2),
                'real_score': round(prediction_result['real_confidence'] * 100, 2)
            })
        
        return jsonify({'results': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """
    Get system statistics
    """
    # Count datasets
    dataset_count = 0
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        dataset_count = len([f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                           if not f.endswith('.meta.json') and os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))])
    
    return jsonify({
        'model_type': 'CNN (Convolutional Neural Network)',
        'feature_extraction': 'TF-IDF Vectorization',
        'preprocessing_steps': [
            'Text Cleaning',
            'Case Folding',
            'Slang Normalization',
            'Stopword Removal',
            'Stemming (Sastrawi)'
        ],
        'supported_language': 'Indonesian',
        'max_text_length': MAX_LENGTH,
        'model_status': 'loaded' if model else 'not loaded',
        'features': {
            'text_analysis': True,
            'url_scraping': True,
            'dataset_management': True
        },
        'datasets_count': dataset_count,
        'slang_words_count': len(slang_dict),
        'hoax_keywords_count': len(hoax_keywords)
    })

@app.route('/examples', methods=['GET'])
def get_examples():
    """
    Get example news for testing
    """
    return jsonify({
        'examples': example_news,
        'count': len(example_news)
    })

@app.route('/scrape-portal', methods=['POST'])
def scrape_portal():
    """
    Scrape multiple articles from news portal(s) for dataset creation
    """
    try:
        data = request.get_json()
        portal_urls = data.get('portal_urls', [])  # List of portal URLs
        max_articles = data.get('max_articles', 10)  # Max articles per portal
        
        if not portal_urls:
            return jsonify({'error': 'At least one portal URL is required'}), 400
        
        scraped_articles = []
        errors = []
        
        for portal_url in portal_urls:
            try:
                # Scrape articles from portal
                articles = scrape_articles_from_portal(portal_url, max_articles)
                scraped_articles.extend(articles)
            except Exception as e:
                errors.append({
                    'portal': portal_url,
                    'error': str(e)
                })
        
        if not scraped_articles and errors:
            return jsonify({
                'error': 'Failed to scrape articles from all portals',
                'details': errors
            }), 400
        
        # Save as dataset CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'scraped_dataset_{timestamp}.csv'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Create CSV
        import csv
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['text', 'label', 'source', 'url', 'title'])
            for article in scraped_articles:
                writer.writerow([
                    article['text'],
                    'unknown',  # User will label manually
                    article['source'],
                    article['url'],
                    article['title']
                ])
        
        # Get file stats
        file_stats = os.stat(filepath)
        
        return jsonify({
            'message': 'Articles scraped successfully',
            'filename': filename,
            'total_articles': len(scraped_articles),
            'file_size': file_stats.st_size,
            'errors': errors if errors else None,
            'dataset': {
                'filename': filename,
                'original_filename': filename,
                'size': file_stats.st_size,
                'upload_date': datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def scrape_articles_from_portal(portal_url, max_articles=10):
    """
    Scrape multiple article links from a news portal and extract their content
    Uses smarter link detection and content validation
    """
    articles = []
    
    try:
        from urllib.parse import urljoin, urlparse
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Try to get sitemap or RSS first for better article links
        portal_domain = urlparse(portal_url).netloc
        sitemap_urls = [
            f"https://{portal_domain}/sitemap.xml",
            f"https://{portal_domain}/sitemap_index.xml",
            f"https://{portal_domain}/rss",
            f"https://{portal_domain}/feed"
        ]
        
        article_links = []
        
        # Try sitemap/RSS first
        for sitemap_url in sitemap_urls:
            try:
                resp = requests.get(sitemap_url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.content, 'xml')
                    # Get URLs from sitemap
                    urls = soup.find_all(['loc'])
                    for url_tag in urls:
                        url_text = url_tag.get_text().strip()
                        if url_text and validators.url(url_text):
                            # Exclude XML/sitemap files themselves
                            if '.xml' in url_text.lower() or 'sitemap' in url_text.lower():
                                continue
                            # Filter article URLs
                            if any(kw in url_text.lower() for kw in [
                                '/berita/', '/news/', '/artikel/', '/article/', '/read/', '-d-',
                                '/nasional/', '/politik/', '/ekonomi/', '/olahraga/', '/teknologi/'
                            ]):
                                article_links.append(url_text)
                        if len(article_links) >= max_articles * 2:
                            break
                    if article_links:
                        print(f"✓ Found {len(article_links)} links from sitemap")
                        break
            except:
                continue
        
        # If sitemap fails, scrape from main page and category pages
        if not article_links:
            # Try common category pages for more article links
            category_paths = [
                '/', '/berita/', '/news/', '/nasional/', '/politik/', '/ekonomi/', 
                '/olahraga/', '/teknologi/', '/lifestyle/', '/entertainment/'
            ]
            
            for path in category_paths:
                if len(article_links) >= max_articles * 3:
                    break
                    
                try:
                    category_url = urljoin(portal_url, path)
                    response = requests.get(category_url, headers=headers, timeout=5)
                    if response.status_code != 200:
                        continue
                        
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find article links with relaxed filtering
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        
                        # Make absolute URL
                        if href.startswith('/'):
                            href = urljoin(portal_url, href)
                        elif not href.startswith('http'):
                            continue
                        
                        # Check if it's a valid URL from same domain
                        if not validators.url(href) or href in article_links:
                            continue
                        
                        href_lower = href.lower()
                        
                        # Exclude non-article pages and XML files
                        if any(excl in href_lower for excl in [
                            'login', 'register', 'profile', 'tag/', 'kategori/', 'category/', 
                            'author/', 'penulis/', 'search', 'index.html', 'javascript:', '#',
                            '.xml', 'sitemap', 'rss', 'feed', '/video/', '/foto/', '/galeri/'
                        ]):
                            continue
                        
                        # Generic article patterns (not just Detik-specific)
                        has_article_indicator = any(kw in href_lower for kw in [
                            '/berita/', '/news/', '/artikel/', '/article/', '/read/', '-d-', 
                            '/nasional/', '/politik/', '/ekonomi/', '/olahraga/', '/teknologi/',
                            '/entertainment/', '/lifestyle/', '/otomotif/', '/bisnis/', '/edukasi/',
                            '/internasional/', '/daerah/', '/metro/', '/nusantara/'
                        ])
                        has_year = any(year in href for year in ['2020', '2021', '2022', '2023', '2024', '2025'])
                        
                        # Accept if has article indicator OR has year in URL
                        if has_article_indicator or has_year:
                            article_links.append(href)
                        
                        if len(article_links) >= max_articles * 3:
                            break
                except:
                    continue
        
        if not article_links:
            raise Exception("No article links found on portal page")
        
        print(f"✓ Found {len(article_links)} potential article links, will scrape up to {max_articles}")
        
        # Scrape each article with validation
        junk_phrases = [
            'detiknetwork adalah bagian dari',
            'untuk bantuan daftar dan masuk',
            'buat akun mpc',
            'satu akun mpc untuk',
            'klik di sini untuk',
            'tonton video lainnya',
            'scroll to continue with content',
            'advertisement'
        ]
        
        scraped_count = 0
        failed_count = 0
        
        for article_url in article_links:
            if scraped_count >= max_articles:
                break
                
            try:
                print(f"Scraping {scraped_count+1}/{max_articles}: {article_url[:80]}...")
                
                article = Article(article_url, language='id')
                article.download()
                article.parse()
                
                # Validate article has sufficient content
                if article.text and len(article.text) > 150:
                    text = article.text
                    text_lower = text.lower()
                    
                    # Skip if mostly junk content (relaxed from >2 to >3)
                    junk_count = sum(1 for junk in junk_phrases if junk in text_lower)
                    if junk_count > 3:
                        print(f"  ✗ Skipped: too much junk content ({junk_count} junk phrases)")
                        failed_count += 1
                        continue
                    
                    # Clean junk lines but be more lenient
                    lines = text.split('\n')
                    filtered_lines = []
                    for line in lines:
                        line_lower = line.lower()
                        # Only skip lines that are pure junk
                        if not any(junk in line_lower for junk in junk_phrases) and len(line.strip()) > 20:
                            filtered_lines.append(line)
                    
                    clean_text = '\n'.join(filtered_lines)
                    
                    # Relaxed validation: 150 chars instead of 200
                    if len(clean_text) >= 150:
                        articles.append({
                            'text': clean_text[:5000],  # Limit text length
                            'title': article.title or 'No title',
                            'url': article_url,
                            'source': portal_url,
                            'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                            'word_count': len(clean_text.split())
                        })
                        scraped_count += 1
                        print(f"  ✓ Success: {article.title[:60]}... ({len(clean_text)} chars, {len(clean_text.split())} words)")
                    else:
                        print(f"  ✗ Skipped: insufficient content after cleaning ({len(clean_text)} chars)")
                        failed_count += 1
                else:
                    print(f"  ✗ Skipped: article too short ({len(article.text) if article.text else 0} chars)")
                    failed_count += 1
                        
            except Exception as e:
                print(f"  ✗ Failed: {str(e)[:100]}")
                failed_count += 1
                continue
        
        print(f"\n{'='*60}")
        print(f"Scraping completed: {scraped_count} articles scraped, {failed_count} failed")
        print(f"{'='*60}\n")
    
    except Exception as e:
        raise Exception(f"Failed to access portal {portal_url}: {str(e)}")
    
    return articles

@app.route('/train', methods=['POST'])
def train_model():
    """
    Train model with a specific dataset
    """
    try:
        data = request.get_json()
        dataset_filename = data.get('dataset_filename')
        
        if not dataset_filename:
            return jsonify({'error': 'Dataset filename is required'}), 400
        
        dataset_path = os.path.join(app.config['UPLOAD_FOLDER'], dataset_filename)
        
        if not os.path.exists(dataset_path):
            return jsonify({'error': 'Dataset file not found'}), 404
        
        # Import training module
        import subprocess
        import sys
        
        # Start training in background process
        train_script = os.path.join(os.path.dirname(__file__), 'train_model.py')
        
        if not os.path.exists(train_script):
            return jsonify({'error': 'Training script not found'}), 404
        
        # Run training script with dataset parameter
        process = subprocess.Popen(
            [sys.executable, train_script, '--dataset', dataset_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return jsonify({
            'message': 'Training started successfully',
            'dataset': dataset_filename,
            'note': 'Training is running in background. Check terminal for progress.'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load model and vectorizer
    print("=" * 50)
    print("Starting Fake News Detection Server")
    print("=" * 50)
    load_model_and_vectorizer()
    print("=" * 50)
    print("Server is ready!")
    print("Server features:")
    print("  ✓ Text Analysis")
    print("  ✓ URL Scraping & Analysis")
    print("  ✓ Dataset Management")
    print("=" * 50)
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
