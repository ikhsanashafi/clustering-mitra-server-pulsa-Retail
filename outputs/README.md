# Direktori Output Hasil Penelitian

Dokumen ini memuat daftar dan penjelasan hasil eksperimen Machine Learning untuk tugas:
**Clustering Perilaku Mitra Server Pulsa Berdasarkan Pola Transaksi Menggunakan Algoritma K-Means**
- Peneliti: Ikhsan Ashafi (NIM: 241011400424)
- Program Studi: Teknik Informatika S1

---

## 1. File Data & Evaluasi

1. **`clustering_evaluation.csv`**
   - Berisi hasil evaluasi pemilihan jumlah klaster $K=2$ hingga $K=6$.
   - Metrik evaluasi mencakup: *Inertia* (Elbow), *Silhouette Score*, *Calinski-Harabasz Index*, dan *Davies-Bouldin Index*.
   - Hasil menunjukkan $K=3$ memberikan partisi optimal dengan keseimbangan Silhouette Score yang stabil (0.421) serta pemaknaan segmen bisnis yang sangat tajam dan dapat diinterpretasikan secara operasional.

2. **`cluster_profiles_mean.csv`**
   - Ringkasan rata-rata metrik bisnis untuk 3 segmen klaster mitra:
     - **Klaster 0 (Mitra Sporadis / Aktivitas Rendah):** 186 mitra (41.24%), rerata 1.17 transaksi, omset Rp 52.113, durasi aktif 0.57 menit.
     - **Klaster 1 (Mitra Berkala / Aktivitas Menengah):** 204 mitra (45.23%), rerata 3.51 transaksi, omset Rp 170.171, durasi aktif 190.36 menit (~3.2 jam).
     - **Klaster 2 (Mitra Utama / Aktivitas Intensif):** 61 mitra (13.53%), rerata 21.93 transaksi, omset Rp 2.204.304, durasi aktif 283.29 menit (~4.7 jam).

---

## 2. Gambar dan Visualisasi (`figures/`)

1. **`eda_hourly.png`**
   - Distribusi frekuensi transaksi per jam pada tanggal 15 Oktober 2026.
   - Puncak aktivitas terjadi pada pukul 21:00 WIB (628 transaksi).

2. **`eda_top_products.png`**
   - Top 10 produk server pulsa terpopuler (voucher game/e-wallet CACVAM1, PLN token, DANA topup).

3. **`eda_feature_dist.png`**
   - Distribusi frekuensi jumlah transaksi, omset moneter, variasi produk, dan durasi aktif mitra.

4. **`eval_elbow_silhouette.png`**
   - Kurva inersia (Elbow Method) dan grafik Silhouette Score untuk seleksi jumlah klaster.

5. **`pca_clusters_2d.png`**
   - Proyeksi 2D Principal Component Analysis (PCA) yang memvisualisasikan keterpisahan ketiga klaster mitra tanpa tumpang tindih ekstrem.

6. **`cluster_metrics_summary.png`**
   - Perbandingan diagram batang metrik utama (frekuensi, omset total, dan rentang durasi aktif) antar segmen mitra.
