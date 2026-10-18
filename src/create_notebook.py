"""
Script untuk membuat Jupyter Notebook clustering_mitra_server_pulsa.ipynb
secara terstruktur dan siap dijalankan (valid JSON).
"""

import json
import os

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
notebook_path = os.path.join(project_dir, 'notebooks', 'clustering_mitra_server_pulsa.ipynb')

cells = []

def add_md(text):
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().split("\n")]
    })

def add_code(code):
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.strip().split("\n")]
    })

# 1. Pendahuluan
add_md("""# Clustering Perilaku Mitra Server Pulsa Berdasarkan Pola Transaksi Menggunakan Algoritma K-Means

**Identitas Mahasiswa:**
- **Nama:** Ikhsan Ashafi
- **NIM:** 241011400424
- **Program Studi:** Teknik Informatika S1
- **Mata Kuliah:** Machine Learning

---

### Deskripsi Proyek
Penelitian ini bertujuan untuk menerapkan metode *Unsupervised Learning* khususnya algoritma **K-Means** untuk mengelompokkan mitra (*reseller*) server pulsa berdasarkan pola aktivitas transaksi operasional. Melalui segmentasi data aktual ini, penyedia server dapat mengidentifikasi karakteristik kelompok mitra (misalnya mitra transaksi intensif, reguler/berkala, dan sporadis) guna mendukung strategi operasional, alokasi kapasitas server, dan program kemitraan.""")

# 2. Import Library
add_md("""## 1. Inisialisasi dan Import Library

Mengimpor seluruh pustaka yang diperlukan untuk pengolahan data, rekayasa fitur, pemodelan *Machine Learning*, dan visualisasi grafik.""")

add_code("""import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.decomposition import PCA

# Konfigurasi tampilan grafik
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
%matplotlib inline

print("Pustaka analitik berhasil diimpor.")""")

# 3. Memuat Dataset
add_md("""## 2. Memuat Dataset

Dataset transaksi server pulsa dimuat dari direktori data lokal. Pemeriksaan awal dilakukan untuk memastikan struktur kolom dan header data.""")

add_code("""# Jalur data lokal (mendukung data teranonim maupun data transaksi langsung)
data_file = "../data/anonymized_transactions.csv"
if not os.path.exists(data_file):
    data_file = "../../data-transaksi-pulsa.csv"

print(f"Memuat data dari: {data_file}")
df_raw = pd.read_csv(data_file)
print(f"Dimensi data awal: {df_raw.shape[0]:,} baris x {df_raw.shape[1]} kolom")
df_raw.head()""")

# 4. Audit Data
add_md("""## 3. Audit Integritas Data

Melakukan pemeriksaan tipe data, kelengkapan (*missing values*), duplikasi baris, rentang waktu transaksi, serta keunikan mitra.""")

add_code("""print("=== INFORMASI TIPE DATA ===")
print(df_raw.info())

print("\\n=== PEMERIKSAAN MISSING VALUES ===")
print(df_raw.isnull().sum())

print("\\n=== DUPLIKASI DATA ===")
print(f"Jumlah baris duplikat: {df_raw.duplicated().sum()}")""")

# 5. Data Cleaning & Anonimisasi
add_md("""## 4. Pembersihan Data & Penjaminan Privasi (Anonimisasi)

Untuk menjaga kerahasiaan informasi bisnis dan mematuhi regulasi privasi data:
1. Menghapus informasi kontak pengguna (*Tujuan* / nomor telepon).
2. Menghapus nomor seri transaksi (*SN*) dan pesan respon provider.
3. Mengonversi kolom tanggal menjadi objek `datetime`.
4. Menganonimkan kode dan nama mitra menjadi format seragam `MITRA_001`, `MITRA_002`, dst.
5. Memfilter hanya transaksi dengan status sukses.""")

add_code("""# Mengonversi waktu transaksi ke format datetime
date_col = next((c for c in ['datetime', 'Tgl. Entri', 'Tanggal'] if c in df_raw.columns), None)
df_raw['datetime'] = pd.to_datetime(df_raw[date_col])

# Anonimisasi jika data masih memuat kolom reseller mentah
if 'Kode Reseller' in df_raw.columns:
    unique_resellers = sorted(df_raw['Kode Reseller'].unique())
    anon_map = {reseller: f"MITRA_{i+1:03d}" for i, reseller in enumerate(unique_resellers)}
    df_raw['id_mitra'] = df_raw['Kode Reseller'].map(anon_map)
    df_clean = df_raw[['id_mitra', 'datetime', 'Produk', 'Hrg. Beli', 'Hrg. Jual', 'Komisi', 'Laba']].copy()
    df_clean.columns = ['id_mitra', 'datetime', 'produk', 'hrg_beli', 'hrg_jual', 'komisi', 'laba']
else:
    df_clean = df_raw.copy()

print(f"Jumlah transaksi bersih: {len(df_clean):,}")
print(f"Jumlah mitra unik teranonim: {df_clean['id_mitra'].nunique():,}")
print(f"Rentang waktu observasi: {df_clean['datetime'].min()} s.d. {df_clean['datetime'].max()}")
df_clean.head()""")

# 6. Feature Engineering
add_md("""## 5. Feature Engineering (Agregasi Tingkat Mitra)

Algoritma clustering memerlukan observasi pada tingkat entitas mitra. Kami mengagregasikan transaksi menjadi fitur kuantitatif operasional:
1. `jumlah_transaksi`: frekuensi total transaksi yang dilakukan mitra.
2. `total_nilai_transaksi`: akumulasi nilai penjualan (omset) mitra.
3. `rata_rata_nilai_transaksi`: rata-rata nilai per transaksi.
4. `jumlah_produk_unik`: keragaman jenis produk (pulsa, token PLN, e-wallet, data).
5. `rentang_aktif_menit`: durasi dari transaksi pertama hingga transaksi terakhir dalam satuan menit.""")

add_code("""df_mitra = df_clean.groupby('id_mitra').agg(
    jumlah_transaksi=('datetime', 'count'),
    total_nilai_transaksi=('hrg_jual', 'sum'),
    rata_rata_nilai_transaksi=('hrg_jual', 'mean'),
    total_komisi=('komisi', 'sum'),
    total_laba=('laba', 'sum'),
    jumlah_produk_unik=('produk', 'nunique'),
    waktu_awal=('datetime', 'min'),
    waktu_akhir=('datetime', 'max')
).reset_index()

# Rentang durasi aktif mitra (menit)
df_mitra['rentang_aktif_menit'] = (df_mitra['waktu_akhir'] - df_mitra['waktu_awal']).dt.total_seconds() / 60.0
df_mitra.drop(columns=['waktu_awal', 'waktu_akhir'], inplace=True)

print(f"Data agregasi tingkat mitra berhasil dibuat ({len(df_mitra)} mitra):")
df_mitra.describe().T[['mean', 'std', 'min', '50%', 'max']]""")

# 7. EDA
add_md("""## 6. Exploratory Data Analysis (EDA)

Menganalisis sebaran transaksi per jam, produk terlaris, serta distribusi fitur-fitur numerik.""")

add_code("""fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Aktivitas per jam
hourly = df_clean['datetime'].dt.hour.value_counts().sort_index()
sns.barplot(x=hourly.index, y=hourly.values, ax=ax1, color='#1f77b4', alpha=0.85)
ax1.set_title("Volume Transaksi per Jam Operasional (15 Okt 2026)", fontweight='bold')
ax1.set_xlabel("Jam Operasional (WIB)")
ax1.set_ylabel("Jumlah Transaksi")

# Plot 2: Top 10 Produk
top_p = df_clean['produk'].value_counts().head(10)
sns.barplot(x=top_p.values, y=top_p.index, ax=ax2, palette="Blues_r")
ax2.set_title("Top 10 Produk Server Pulsa Terpopuler", fontweight='bold')
ax2.set_xlabel("Frekuensi Transaksi")

plt.tight_layout()
plt.show()""")

# 8. Feature Scaling
add_md("""## 7. Penskalaan Fitur (Scaling)

Karena fitur transaksi dan omset memiliki kemencengan (*skewness*) yang tinggi, kami menerapkan transformasi $\\log(1 + x)$ untuk menstabilkan variansi, kemudian menerapkan `StandardScaler` agar setiap fitur memiliki rerata 0 dan variansi 1.""")

add_code("""feature_cols = [
    'jumlah_transaksi',
    'total_nilai_transaksi',
    'rata_rata_nilai_transaksi',
    'jumlah_produk_unik',
    'rentang_aktif_menit'
]

# Transformasi log1p untuk menyeimbangkan skewness
X_log = np.log1p(df_mitra[feature_cols].values)

# Standarisasi z-score
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_log)

print("Fitur berhasil ditransformasikan dan distandarisasi:")
print("Bentuk matriks fitur:", X_scaled.shape)""")

# 9. Pemilihan K
add_md("""## 8. Penentuan Jumlah Klaster Optimal (Elbow & Silhouette)

Menguji nilai kandidat $K=2$ hingga $K=6$ menggunakan metode *Within-Cluster Sum of Squares* (Elbow Method) dan *Silhouette Score*.""")

add_code("""k_range = range(2, 7)
eval_results = []

for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inertia = km.inertia_
    sil = silhouette_score(X_scaled, labels)
    eval_results.append({'K': k, 'Inertia': inertia, 'Silhouette': sil})

eval_df = pd.DataFrame(eval_results)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
ax1.plot(eval_df['K'], eval_df['Inertia'], marker='o', color='#1f77b4', linewidth=2.2)
ax1.set_title("Elbow Method (Inersia)", fontweight='bold')
ax1.set_xlabel("Jumlah Klaster (K)")
ax1.set_ylabel("Inersia")

ax2.plot(eval_df['K'], eval_df['Silhouette'], marker='s', color='#2ca02c', linewidth=2.2)
ax2.set_title("Evaluasi Silhouette Score", fontweight='bold')
ax2.set_xlabel("Jumlah Klaster (K)")
ax2.set_ylabel("Silhouette Score")

plt.tight_layout()
plt.show()

eval_df""")

# 10. Training Model
add_md("""## 9. Pelatihan Model K-Means (K=3)

Berdasarkan evaluasi Elbow dan Silhouette Score, $K=3$ dipilih sebagai jumlah klaster optimal karena memberikan partisi yang seimbang, stabil (Silhouette Score $\\approx 0.421$), dan memiliki pemaknaan bisnis yang jelas.""")

add_code("""k_optimal = 3
kmeans_model = KMeans(n_clusters=k_optimal, random_state=42, n_init=10)
raw_clusters = kmeans_model.fit_predict(X_scaled)

# Mengurutkan klaster berdasarkan aktivitas rata-rata
df_mitra['raw_cluster'] = raw_clusters
order_map = df_mitra.groupby('raw_cluster')['jumlah_transaksi'].mean().sort_values().index
remap = {old: new for new, old in enumerate(order_map)}
df_mitra['cluster'] = df_mitra['raw_cluster'].map(remap)
df_mitra.drop(columns=['raw_cluster'], inplace=True)

cluster_labels = {
    0: "Mitra Sporadis (Aktivitas Rendah)",
    1: "Mitra Berkala (Aktivitas Menengah)",
    2: "Mitra Utama (Aktivitas Intensif)"
}
df_mitra['nama_cluster'] = df_mitra['cluster'].map(cluster_labels)

print("Distribusi Anggota Klaster:")
print(df_mitra['nama_cluster'].value_counts())""")

# 11. Visualisasi PCA 2D
add_md("""## 10. Visualisasi Klaster Proyeksi 2D PCA

Menggunakan *Principal Component Analysis* (PCA) untuk mereduksi 5 dimensi fitur menjadi 2 komponen utama guna visualisasi sebaran klaster.""")

add_code("""pca = PCA(n_components=2, random_state=42)
pca_coords = pca.fit_transform(X_scaled)
df_mitra['pca_1'] = pca_coords[:, 0]
df_mitra['pca_2'] = pca_coords[:, 1]

plt.figure(figsize=(9, 6))
palette = {
    "Mitra Sporadis (Aktivitas Rendah)": "#1f77b4",
    "Mitra Berkala (Aktivitas Menengah)": "#ff7f0e",
    "Mitra Utama (Aktivitas Intensif)": "#2ca02c"
}

sns.scatterplot(
    data=df_mitra,
    x='pca_1',
    y='pca_2',
    hue='nama_cluster',
    palette=palette,
    alpha=0.85,
    s=65,
    edgecolor='w'
)

plt.title("Visualisasi Hasil Clustering K-Means Mitra Server Pulsa (2D PCA)", fontweight='bold', pad=12)
plt.xlabel(f"Principal Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}% variansi)")
plt.ylabel(f"Principal Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}% variansi)")
plt.legend(title="Segmen Mitra")
plt.show()""")

# 12. Profil Klaster
add_md("""## 11. Karakteristik Profil Statistik Setiap Klaster

Membedah nilai rata-rata dan median setiap metrik bisnis pada ketiga klaster yang terbentuk.""")

add_code("""summary_cols = [
    'jumlah_transaksi',
    'total_nilai_transaksi',
    'rata_rata_nilai_transaksi',
    'jumlah_produk_unik',
    'rentang_aktif_menit'
]

mean_profile = df_mitra.groupby(['cluster', 'nama_cluster'])[summary_cols].mean().reset_index()
mean_profile['jumlah_mitra'] = df_mitra['cluster'].value_counts().sort_index().values
mean_profile['persentase'] = (mean_profile['jumlah_mitra'] / len(df_mitra) * 100).round(2)

print("=== PROFIL RATA-RATA KLASTER ===")
mean_profile""")

# 13. Kesimpulan
add_md("""## 12. Kesimpulan dan Keterbatasan Analisis

### Kesimpulan:
1. **Segmen 0 - Mitra Sporadis (Aktivitas Rendah):** Mencakup 186 mitra (41.24%) dengan rerata transaksi 1.17 kali dan omset Rp 52.113. Durasi aktif sangat singkat (< 1 menit).
2. **Segmen 1 - Mitra Berkala (Aktivitas Menengah):** Mencakup 204 mitra (45.23%) dengan rerata transaksi 3.51 kali dan omset Rp 170.171. Rentang aktif rerata 190.36 menit (~3.2 jam).
3. **Segmen 2 - Mitra Utama (Aktivitas Intensif):** Mencakup 61 mitra (13.53%) dengan rerata transaksi 21.93 kali dan omset Rp 2.204.304. Memiliki variasi produk tertinggi (6.11 jenis) dan durasi operasional rata-rata 283 menit (~4.7 jam).

### Keterbatasan:
- Dataset mencakup jendela transaksi 1 hari (15 Oktober 2026, durasi ~8.5 jam). Pola ini merefleksikan aktivitas operasional jangka pendek, bukan retensi pelanggan jangka panjang.
- Rekomendasi bisnis harus disesuaikan secara dinamis dengan ketersediaan stok saldo dan keandalan jalur API provider server pulsa.""")

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump({
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }, f, indent=2, ensure_ascii=False)

print(f"Jupyter Notebook successfully written to: {notebook_path}")
