import json

with open('CNN_FakeNews_Detection.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# The 5th cell is the dataset loading code (index 4)
new_dataset_code = """import pandas as pd
import os

print("Membaca Dataset...")
# Menggunakan dataset Indonesian Fact and Hoax Political News
hoax_path = 'datasets/Indonesian Fact and Hoax Political News/Cleaned/dataset_turnbackhoax_10_cleaned.xlsx'
fakta_path = 'datasets/Indonesian Fact and Hoax Political News/Cleaned/dataset_cnn_10k_cleaned.xlsx'

# Membaca dataset (kita ambil 1000 data pertama dari masing-masing agar cepat diproses sebagai contoh)
df_hoax = pd.read_excel(hoax_path, nrows=1000)
df_fakta = pd.read_excel(fakta_path, nrows=1000)

# Pastikan label sesuai (1 untuk hoax, 0 untuk fakta)
df_hoax['label'] = 1
df_fakta['label'] = 0

# Menggabungkan kedua dataframe
df = pd.concat([df_hoax, df_fakta], ignore_index=True)

# Memilih kolom Teks (menggunakan 'Title' atau 'FullText'). Kita gunakan 'Title' untuk contoh yang lebih cepat,
# atau gabungan Title dan FullText jika tersedia.
df['text'] = df['Title'].fillna('') + " " + df['FullText'].fillna('')

# Mengacak urutan data (shuffle)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print("Total Data:", len(df))
display(df[['text', 'label']].head())
"""

notebook['cells'][4]['source'] = [line + '\n' for line in new_dataset_code.split('\n')]

with open('CNN_FakeNews_Detection.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1)

print("Notebook updated!")
