"""
Modul Feature Engineering
Disusun oleh: Ikhsan Ashafi (NIM: 241011400424)
Tujuan: Melakukan agregasi tingkat mitra dan menyusun fitur numerik untuk algoritma clustering.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any


def extract_partner_features(df_clean: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Mengagregasikan data transaksi pada level mitra anonim (id_mitra).
    Menghitung fitur kuantitatif aktivitas bisnis mitra.
    """
    if 'id_mitra' not in df_clean.columns:
        raise KeyError("Kolom 'id_mitra' tidak ditemukan pada DataFrame yang dibersihkan.")

    # Agregasi dasar
    agg = df_clean.groupby('id_mitra').agg(
        jumlah_transaksi=('datetime', 'count'),
        total_nilai_transaksi=('hrg_jual', 'sum'),
        total_nilai_beli=('hrg_beli', 'sum'),
        rata_rata_nilai_transaksi=('hrg_jual', 'mean'),
        total_komisi=('komisi', 'sum'),
        total_laba=('laba', 'sum'),
        rata_rata_laba=('laba', 'mean'),
        jumlah_produk_unik=('produk', 'nunique'),
        waktu_awal=('datetime', 'min'),
        waktu_akhir=('datetime', 'max')
    ).reset_index()

    # Fitur temporal: rentang waktu aktivitas dalam satuan menit
    # Mengukur seberapa panjang periode mitra aktif bertransaksi pada jendela observasi
    durasi_detik = (agg['waktu_akhir'] - agg['waktu_awal']).dt.total_seconds()
    agg['rentang_aktif_menit'] = durasi_detik / 60.0

    # Fitur intensitas: rasio transaksi per jam aktif jika rentang aktif > 0
    # Untuk rentang 0 menit (transaksi tunggal), intensitas dinilai 1 trx
    agg['kecepatan_transaksi_per_jam'] = np.where(
        agg['rentang_aktif_menit'] > 0,
        (agg['jumlah_transaksi'] / (agg['rentang_aktif_menit'] / 60.0)),
        agg['jumlah_transaksi']
    )

    # Menghapus kolom waktu mentah dari matriks fitur analitik (disimpan hanya ID dan numerik)
    df_features = agg.drop(columns=['waktu_awal', 'waktu_akhir']).copy()

    meta = {
        "total_mitra": len(df_features),
        "mean_transaksi_per_mitra": float(df_features['jumlah_transaksi'].mean()),
        "median_transaksi_per_mitra": float(df_features['jumlah_transaksi'].median()),
        "max_transaksi_per_mitra": int(df_features['jumlah_transaksi'].max()),
        "mean_omset_per_mitra": float(df_features['total_nilai_transaksi'].mean()),
        "median_omset_per_mitra": float(df_features['total_nilai_transaksi'].median()),
        "feature_columns": [c for c in df_features.columns if c != 'id_mitra']
    }

    return df_features, meta


def get_default_clustering_features() -> List[str]:
    """
    Daftar fitur primer yang dipilih untuk input algoritma K-Means:
    1. jumlah_transaksi: frekuensi interaksi transaksi
    2. total_nilai_transaksi: total volume moneter (omset)
    3. rata_rata_nilai_transaksi: tiket rata-rata per transaksi
    4. jumlah_produk_unik: keragaman portofolio produk pulsa/tagihan
    5. rentang_aktif_menit: kontinuitas rentang operasional mitra
    """
    return [
        'jumlah_transaksi',
        'total_nilai_transaksi',
        'rata_rata_nilai_transaksi',
        'jumlah_produk_unik',
        'rentang_aktif_menit'
    ]
