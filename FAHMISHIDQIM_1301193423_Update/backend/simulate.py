import pandas as pd
import numpy as np
import re
import warnings
warnings.filterwarnings('ignore')
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Suppress TF warnings

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, Dense, Dropout

print("1. Memuat Dataset...")
hoax_path = 'datasets/Indonesian Fact and Hoax Political News/Cleaned/dataset_turnbackhoax_10_cleaned.xlsx'
fakta_path = 'datasets/Indonesian Fact and Hoax Political News/Cleaned/dataset_cnn_10k_cleaned.xlsx'

df_hoax = pd.read_excel(hoax_path, nrows=500)
df_fakta = pd.read_excel(fakta_path, nrows=500)

df_hoax['label'] = 1
df_fakta['label'] = 0

df = pd.concat([df_hoax, df_fakta], ignore_index=True)
df['text'] = df['Title'].fillna('') + " " + df['FullText'].fillna('')
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
print(f"Total Data Simulasi: {len(df)} baris")

print("2. Pemrosesan Teks (Preprocessing)...")
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^a-z\s]', '', text)
    return text.strip()

df['cleaned_text'] = df['text'].apply(clean_text)

print("3. Tokenisasi dan Padding...")
max_features = 2000
max_length = 50

tokenizer = Tokenizer(num_words=max_features)
tokenizer.fit_on_texts(df['cleaned_text'])

X_seq = tokenizer.texts_to_sequences(df['cleaned_text'])
X_pad = pad_sequences(X_seq, maxlen=max_length, padding='post')
y = df['label'].values

X_train, X_test, y_train, y_test = train_test_split(X_pad, y, test_size=0.2, random_state=42)

print("4. Membangun dan Melatih Model CNN (3 Epochs)...")
model = Sequential([
    Embedding(input_dim=max_features, output_dim=32, input_length=max_length),
    Conv1D(filters=64, kernel_size=5, activation='relu'),
    GlobalMaxPooling1D(),
    Dense(16, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

model.fit(X_train, y_train, epochs=3, batch_size=16, validation_data=(X_test, y_test), verbose=1)

print("5. Evaluasi Model...")
y_pred_prob = model.predict(X_test, verbose=0)
y_pred = (y_pred_prob > 0.5).astype(int)
acc = accuracy_score(y_test, y_pred)
print(f"\n✅ Hasil Simulasi Akurasi Model CNN: {acc * 100:.2f}%\n")
print("Simulasi Selesai! Notebook asli juga sudah diperbarui dengan path dataset ini.")
