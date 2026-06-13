import os
import re
import argparse
import pickle
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout, Input
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import warnings

warnings.filterwarnings('ignore')

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def main():
    parser = argparse.ArgumentParser(description="Train CNN Fake News Model")
    parser.add_argument('--dataset', type=str, help='Path to dataset file (.csv or .xlsx)')
    args = parser.parse_args()

    os.makedirs('models', exist_ok=True)

    print("[*] Memuat dataset...")
    df = None
    if args.dataset and os.path.exists(args.dataset):
        if args.dataset.endswith('.csv'):
            df = pd.read_csv(args.dataset)
        elif args.dataset.endswith('.xlsx'):
            df = pd.read_excel(args.dataset)
        elif args.dataset.endswith('.json'):
            df = pd.read_json(args.dataset)
    else:
        print("[!] Dataset tidak ditemukan. Menggunakan dataset bawaan (dummy data untuk demonstrasi)...")
        # Generate dummy data
        data_text = [
            "Demokrat Pecat Wakil Ketua DPRD Solok Usai Terjerat Narkoba",
            "[SALAH] Jus Daun Pepaya untuk Obat Demam Berdarah",
            "NasDem Jawab Sindiran Hasto Soal Wacana Pertemuan",
            "[SALAH] Surat Permintaan Data Pensiunan PNS dari BKN",
            "Golkar Sindir Intervensi Parpol Koalisi soal Reshuffle"
        ]
        data_label = [0, 1, 0, 1, 0]
        df = pd.DataFrame({
            'text': data_text * 200,
            'label': data_label * 200
        })

    if df is not None:
        if 'text' not in df.columns or 'label' not in df.columns:
            if 'Title' in df.columns and 'FullText' in df.columns:
                df['text'] = df['Title'].fillna('') + " " + df['FullText'].fillna('')
            else:
                print("[!] Format dataset tidak dikenali. Harus mengandung kolom 'text' dan 'label'.")
                return

    print(f"[*] Total Data: {len(df)}")

    print("[*] Inisialisasi NLP Sastrawi (StopWord & Stemmer)...")
    stopword_factory = StopWordRemoverFactory()
    stopword = stopword_factory.create_stop_word_remover()
    stemmer_factory = StemmerFactory()
    stemmer = stemmer_factory.create_stemmer()

    def process_nlp(text):
        text = clean_text(text)
        text = stopword.remove(text)
        text = stemmer.stem(text)
        return text

    print("[*] Membersihkan teks (Preprocessing)...")
    df['cleaned_text'] = df['text'].apply(process_nlp)

    print("[*] Memulai Tokenisasi dan Padding...")
    max_features = 5000
    max_length = 50

    tokenizer = Tokenizer(num_words=max_features)
    tokenizer.fit_on_texts(df['cleaned_text'])

    X_seq = tokenizer.texts_to_sequences(df['cleaned_text'])
    X_pad = pad_sequences(X_seq, maxlen=max_length, padding='post')
    
    # Normalize labels (ensure they are 0 and 1)
    label_map = {'real': 0, 'true': 0, 'asli': 0, 'benar': 0, 'valid': 0, 0: 0,
                 'fake': 1, 'false': 1, 'palsu': 1, 'hoax': 1, 'invalid': 1, 1: 1}
    df['label'] = df['label'].map(lambda x: label_map.get(str(x).lower(), 0))
    y = df['label'].values

    X_train, X_test, y_train, y_test = train_test_split(X_pad, y, test_size=0.2, random_state=42)

    print("[*] Membangun arsitektur model CNN...")
    embedding_dim = 64
    model = Sequential([
        Input(shape=(max_length,)),
        Embedding(input_dim=max_features, output_dim=embedding_dim),
        Conv1D(filters=128, kernel_size=5, activation='relu'),
        GlobalMaxPooling1D(),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.summary()

    print("[*] Memulai proses Training...")
    epochs = 10
    batch_size = 16

    model.fit(
        X_train, y_train, 
        epochs=epochs, 
        batch_size=batch_size, 
        validation_data=(X_test, y_test)
    )

    print("[*] Menyimpan model dan tokenizer...")
    model.save('models/fake_news_cnn_model.h5')
    with open('models/tokenizer.pickle', 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    print("[+] Training Selesai dan berhasil disimpan ke folder 'models/'")

if __name__ == "__main__":
    main()
