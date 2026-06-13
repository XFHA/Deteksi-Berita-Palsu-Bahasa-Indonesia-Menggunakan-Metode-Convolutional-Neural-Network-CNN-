"""
Training script for CNN-based Fake News Detector
This script trains a CNN model with TF-IDF features for Indonesian fake news detection
Supports custom dataset upload
"""

import pandas as pd
import numpy as np
import pickle
import os
import re
import sys
import json
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Conv1D, GlobalMaxPooling1D, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import warnings
warnings.filterwarnings('ignore')

# Initialize Indonesian NLP tools
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

stopword_factory = StopWordRemoverFactory()
stopword_remover = stopword_factory.create_stop_word_remover()

# Load slang dictionary from external file
def load_slang_dictionary():
    """Load slang dictionary from CSV file"""
    slang_dict = {}
    slang_file = os.path.join(os.path.dirname(__file__), 'data', 'slang_dictionary.csv')
    
    if os.path.exists(slang_file):
        try:
            import csv
            with open(slang_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        slang_dict[row[0]] = row[1]
            print(f"✓ Loaded {len(slang_dict)} slang words from {slang_file}")
        except Exception as e:
            print(f"Warning: Could not load slang dictionary: {e}")
            print("Using fallback slang dictionary")
            slang_dict = {
                'gak': 'tidak', 'ga': 'tidak', 'gk': 'tidak',
                'yg': 'yang', 'dgn': 'dengan', 'bgt': 'banget'
            }
    else:
        print(f"Warning: Slang dictionary file not found at {slang_file}")
        print("Using fallback slang dictionary")
        slang_dict = {
            'gak': 'tidak', 'ga': 'tidak', 'gk': 'tidak',
            'yg': 'yang', 'dgn': 'dengan', 'bgt': 'banget'
        }
    
    return slang_dict

# Load slang dictionary from external CSV file
slang_dict = load_slang_dictionary()

def preprocess_text(text):
    """Indonesian text preprocessing"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove mentions and hashtags
    text = re.sub(r'@\w+|#\w+', '', text)
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Replace slang words
    words = text.split()
    words = [slang_dict.get(word, word) for word in words]
    text = ' '.join(words)
    
    # Remove stopwords
    text = stopword_remover.remove(text)
    
    # Stemming
    text = stemmer.stem(text)
    
    return text

def load_dataset_from_file(filepath):
    """
    Load dataset from various file formats (CSV, TXT, JSON)
    Expected format:
    - CSV: columns 'text' and 'label' (0=real, 1=fake)
    - TXT: each line: text|label
    - JSON: array of objects with 'text' and 'label' keys
    """
    file_ext = os.path.splitext(filepath)[1].lower()
    
    try:
        if file_ext == '.csv':
            df = pd.read_csv(filepath)
            
            # Check for required columns
            if 'text' not in df.columns or 'label' not in df.columns:
                # Try alternative column names
                text_col = None
                label_col = None
                
                # Common text column names
                for col in ['text', 'content', 'news', 'article', 'berita']:
                    if col in df.columns:
                        text_col = col
                        break
                
                # Common label column names
                for col in ['label', 'class', 'category', 'type', 'kategori']:
                    if col in df.columns:
                        label_col = col
                        break
                
                if not text_col or not label_col:
                    raise ValueError(f"CSV must have 'text' and 'label' columns. Found: {df.columns.tolist()}")
                
                df = df.rename(columns={text_col: 'text', label_col: 'label'})
            
            # Convert labels to 0/1 if they're strings
            if df['label'].dtype == 'object':
                # Map common label values
                label_map = {
                    'real': 0, 'fake': 1,
                    'true': 0, 'false': 1,
                    'asli': 0, 'palsu': 1,
                    'benar': 0, 'hoax': 1,
                    'valid': 0, 'invalid': 1,
                    0: 0, 1: 1, '0': 0, '1': 1
                }
                df['label'] = df['label'].str.lower().map(label_map)
            
            return df['text'].tolist(), df['label'].tolist()
        
        elif file_ext == '.txt':
            texts = []
            labels = []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Expected format: text|label
                    if '|' in line:
                        parts = line.rsplit('|', 1)
                        text = parts[0].strip()
                        label = parts[1].strip()
                        
                        # Convert label to 0/1
                        if label.lower() in ['fake', 'palsu', 'hoax', '1', 'false']:
                            label = 1
                        else:
                            label = 0
                        
                        texts.append(text)
                        labels.append(label)
            
            return texts, labels
        
        elif file_ext == '.json':
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("JSON must be an array of objects")
            
            texts = []
            labels = []
            
            for item in data:
                if 'text' not in item or 'label' not in item:
                    continue
                
                text = item['text']
                label = item['label']
                
                # Convert label to 0/1
                if isinstance(label, str):
                    if label.lower() in ['fake', 'palsu', 'hoax', 'false']:
                        label = 1
                    else:
                        label = 0
                
                texts.append(text)
                labels.append(int(label))
            
            return texts, labels
        
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    except Exception as e:
        print(f"Error loading dataset: {e}")
        raise

def create_sample_dataset():
    """
    Create a sample dataset for demonstration
    Only used when no custom dataset is provided
    """
    fake_news = [
        "VIRAL!!! HEBOH! Pemerintah akan melarang semua orang keluar rumah mulai besok! SEGERA SHARE sebelum dihapus!!!",
        "BAHAYA! Vaksin COVID mengandung chip pelacak! Jangan divaksin! Sebarkan ke semua grup!",
        "MENGEJUTKAN! Ditemukan obat COVID gratis di pasar! Ambil sebelum habis! Share segera!",
        "WASPADA! Air minum kemasan mengandung racun! Cek sekarang juga!",
        "BERITA PENTING! Besok seluruh Indonesia akan blackout total! Siapkan lilin!",
        "VIRAL! Menteri kesehatan mengundurkan diri! Pemerintah bohong soal pandemi!",
        "HEBOH! Ditemukan cara mudah kaya dalam semalam! Klik link ini!",
        "AWAS! Makanan ini menyebabkan kanker! Jangan dimakan! Share!",
        "MENGEJUTKAN! Presiden akan mengundurkan diri besok! Negara akan kacau!",
        "VIRAL BANGET! Semua HP akan disadap pemerintah! Matikan sekarang juga!",
        "BERITA TERKINI! Bank akan tutup semua ATM mulai besok! Ambil uang sekarang!",
        "BAHAYA! WhatsApp akan berbayar mulai besok! Share ke semua kontak!",
        "HEBOH DI SOSMED! Artis terkenal tertangkap polisi karena narkoba!",
        "BREAKING NEWS! Indonesia akan perang dengan negara tetangga! Waspada!",
        "VIRAL! Ditemukan makhluk aneh di laut Indonesia! Lihat fotonya!",
        "AWAS! Semua bank akan bangkrut besok pagi! Ambil uang Anda sekarang!",
        "VIRAL! Ditemukan cara hack WiFi tetangga dengan mudah! Download sekarang!",
        "BAHAYA! Minum air putih bisa menyebabkan kematian! Jangan minum!",
        "HEBOH! Semua smartphone akan meledak besok! Matikan sekarang!",
        "MENGEJUTKAN! Alien ditemukan di Indonesia! Lihat videonya sebelum dihapus!",
    ]
    
    real_news = [
        "Presiden Joko Widodo meresmikan jalan tol Trans Jawa sepanjang 1.000 kilometer pada hari Senin.",
        "Kementerian Kesehatan melaporkan tingkat vaksinasi COVID-19 telah mencapai 70 persen dari target populasi.",
        "Bank Indonesia mempertahankan suku bunga acuan di level 3.5 persen untuk menjaga stabilitas ekonomi.",
        "Menteri Pendidikan mengumumkan kurikulum baru akan diterapkan mulai tahun ajaran mendatang.",
        "Pertumbuhan ekonomi Indonesia kuartal pertama tercatat 5.2 persen year-on-year menurut BPS.",
        "DPR mengesahkan Undang-Undang tentang Perlindungan Data Pribadi setelah pembahasan panjang.",
        "Pemerintah mengalokasikan anggaran Rp 500 triliun untuk program bantuan sosial tahun ini.",
        "Tim sepak bola nasional Indonesia berhasil lolos ke putaran final Piala AFF 2023.",
        "Badan Meteorologi melaporkan cuaca cerah di sebagian besar wilayah Indonesia hari ini.",
        "Kurs rupiah ditutup menguat ke level Rp 14.500 per dolar AS di pasar spot.",
        "Menteri Pertanian meluncurkan program swasembada pangan untuk meningkatkan produksi beras nasional.",
        "Komisi Pemberantasan Korupsi menangkap seorang pejabat tinggi terkait kasus suap proyek infrastruktur.",
        "Bursa Efek Indonesia mencatat rekor transaksi harian tertinggi senilai Rp 15 triliun.",
        "Pemerintah menaikkan harga BBM bersubsidi untuk menjaga kesinambungan subsidi energi.",
        "Universitas Indonesia masuk dalam 300 besar universitas terbaik dunia versi QS World Rankings.",
        "Kementerian Perhubungan mengumumkan pembangunan MRT fase 2 akan dimulai tahun depan.",
        "Mahkamah Konstitusi menolak gugatan hasil pemilihan umum karena tidak memenuhi syarat.",
        "BMKG memperingatkan potensi cuaca ekstrem di beberapa wilayah Indonesia minggu ini.",
        "Menteri BUMN melaporkan kinerja BUMN meningkat dengan laba bersih naik 15 persen.",
        "Kementerian Kesehatan membuka layanan telemedicine gratis untuk masyarakat di daerah terpencil.",
    ]
    
    # Combine data
    texts = fake_news + real_news
    labels = [1] * len(fake_news) + [0] * len(real_news)
    
    return texts, labels

def build_cnn_model(max_length, max_features, embedding_dim=64):
    """
    Build CNN model architecture for text classification
    """
    from tensorflow.keras.layers import Input, Embedding
    model = Sequential([
        Input(shape=(max_length,)),
        Embedding(input_dim=max_features, output_dim=embedding_dim),
        Conv1D(filters=128, kernel_size=5, activation='relu'),
        GlobalMaxPooling1D(),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    
    return model

def train_model(dataset_path=None):
    """
    Train the CNN model
    """
    print("=" * 70)
    print("FAKE NEWS DETECTOR - MODEL TRAINING")
    print("=" * 70)
    
    # Load dataset
    if dataset_path and os.path.exists(dataset_path):
        print(f"\n📁 Loading custom dataset from: {dataset_path}")
        try:
            texts, labels = load_dataset_from_file(dataset_path)
            print(f"✓ Dataset loaded successfully")
        except Exception as e:
            print(f"✗ Failed to load dataset: {e}")
            print("  Using sample dataset instead...")
            texts, labels = create_sample_dataset()
    else:
        print("\n📝 No custom dataset provided, using sample dataset")
        print("   For production, provide your own dataset using:")
        print("   python train_model.py --dataset path/to/dataset.csv")
        texts, labels = create_sample_dataset()
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total samples: {len(texts)}")
    print(f"   Fake news: {sum(labels)} ({sum(labels)/len(labels)*100:.1f}%)")
    print(f"   Real news: {len(labels)-sum(labels)} ({(len(labels)-sum(labels))/len(labels)*100:.1f}%)")
    
    # Preprocess texts
    print("\n🔄 Preprocessing texts...")
    processed_texts = [preprocess_text(text) for text in texts]
    print(f"✓ Preprocessing completed")
    
    # Create Tokenizer and Pad Sequences
    print("\n🔢 Tokenizing and padding sequences...")
    max_features = 5000
    max_length = 50
    tokenizer = Tokenizer(num_words=max_features)
    tokenizer.fit_on_texts(processed_texts)
    
    vocab_size = len(tokenizer.word_index) + 1
    
    X_seq = tokenizer.texts_to_sequences(processed_texts)
    X = pad_sequences(X_seq, maxlen=max_length, padding='post')
    
    print(f"✓ Tokenization completed")
    print(f"   Shape of Data Tensor: {X.shape}")
    
    y = np.array(labels)
    
    # Split data
    print("\n📊 Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"✓ Train set: {len(X_train)} samples")
    print(f"✓ Test set: {len(X_test)} samples")
    
    # Build model
    print("\n🏗️ Building CNN model...")
    model = build_cnn_model(max_length=max_length, max_features=max_features)
    print("✓ Model architecture created")
    
    # Model summary
    print("\n📋 Model Summary:")
    model.summary()
    
    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            'models/fake_news_cnn_model.h5',
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=0.00001,
            verbose=1
        )
    ]
    
    # Train model
    print("\n🎯 Training model...")
    print("-" * 70)
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=50,
        batch_size=16,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate model
    print("\n" + "=" * 70)
    print("MODEL EVALUATION")
    print("=" * 70)
    
    # Predictions
    y_pred_prob = model.predict(X_test, verbose=0)
    y_pred = (y_pred_prob > 0.5).astype(int).flatten()
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n🎯 Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    print("\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Real', 'Fake']))
    
    print("\n📈 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    print(f"\nTrue Negatives (Real as Real): {cm[0][0]}")
    print(f"False Positives (Real as Fake): {cm[0][1]}")
    print(f"False Negatives (Fake as Real): {cm[1][0]}")
    print(f"True Positives (Fake as Fake): {cm[1][1]}")
    
    # Save model and vectorizer
    print("\n💾 Saving model and vectorizer...")
    os.makedirs('models', exist_ok=True)
    
    model.save('models/fake_news_cnn_model.h5')
    print("✓ Model saved: models/fake_news_cnn_model.h5")
    
    with open('models/tokenizer.pkl', 'wb') as f:
        pickle.dump(tokenizer, f)
    print("✓ Tokenizer saved: models/tokenizer.pkl")
    
    # Save training metadata
    metadata = {
        'accuracy': float(accuracy),
        'total_samples': len(texts),
        'fake_count': int(sum(labels)),
        'real_count': int(len(labels) - sum(labels)),
        'feature_dim': int(max_length),
        'dataset_path': dataset_path if dataset_path else 'sample_dataset',
        'trained_at': pd.Timestamp.now().isoformat()
    }
    
    with open('models/training_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print("✓ Metadata saved: models/training_metadata.json")
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\n🚀 You can now start the Flask server with: python app.py")
    
    return model, tokenizer, history

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Fake News Detection Model')
    parser.add_argument('--dataset', type=str, help='Path to custom dataset file (CSV, TXT, or JSON)', default=None)
    args = parser.parse_args()
    
    # Train model
    train_model(dataset_path=args.dataset)
