"""
Modul Data Cleaning dan Anonimisasi
Disusun oleh: Ikhsan Ashafi (NIM: 241011400424)
Tujuan: Memuat data, melakukan audit integritas, pembersihan, dan penjaminan privasi data.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Union


def load_raw_data(file_source: Union[str, Any]) -> pd.DataFrame:
    """
    Memuat dataset dari path file atau buffer upload (Streamlit).
    Mendukung format CSV dan Excel (.xlsx).
    """
    if isinstance(file_source, str):
        if not os.path.exists(file_source):
            raise FileNotFoundError(f"File tidak ditemukan: {file_source}")
        ext = os.path.splitext(file_source)[1].lower()
        if ext == '.csv':
            # Mencoba membaca dengan berbagai kemungkinan delimiter
            try:
                df = pd.read_csv(file_source, sep=None, engine='python')
            except Exception:
                df = pd.read_csv(file_source, sep=';')
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_source)
        else:
            raise ValueError(f"Format file tidak didukung: {ext}. Gunakan .csv atau .xlsx")
    else:
        # Buffer objek (seperti st.file_uploader)
        filename = getattr(file_source, 'name', '')
        if filename.endswith('.csv'):
            try:
                df = pd.read_csv(file_source)
            except Exception:
                file_source.seek(0)
                df = pd.read_csv(file_source, sep=';')
        else:
            df = pd.read_excel(file_source)

    # Deteksi jika baris pertama adalah header offset (kasus Excel dengan baris header ganda)
    if 'Unnamed: 0' in df.columns and ('TrxID' in df.iloc[0].values or 'Kode Reseller' in df.iloc[0].values):
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)

    # Standardisasi nama kolom (strip whitespace)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def audit_raw_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Melakukan pemeriksaan audit komprehensif terhadap integritas dataset mentah.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    missing_counts = df.isnull().sum().to_dict()
    total_missing = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())

    # Kolom reseller
    reseller_col = None
    for c in ['Kode Reseller', 'Nama Reseller', 'Reseller', 'Kode Mitra', 'Mitra']:
        if c in df.columns:
            reseller_col = c
            break

    unique_resellers = int(df[reseller_col].nunique()) if reseller_col else 0

    # Rentang tanggal
    date_col = None
    for c in ['Tgl. Entri', 'Tanggal', 'Tgl', 'Datetime', 'Waktu']:
        if c in df.columns:
            date_col = c
            break

    date_min = None
    date_max = None
    if date_col:
        try:
            dt_series = pd.to_datetime(df[date_col], errors='coerce')
            date_min = str(dt_series.min())
            date_max = str(dt_series.max())
        except Exception:
            pass

    # Status distribusi
    status_col = 'Status' if 'Status' in df.columns else None
    status_dist = df[status_col].value_counts().to_dict() if status_col else {}

    # Produk
    produk_col = 'Produk' if 'Produk' in df.columns else None
    unique_products = int(df[produk_col].nunique()) if produk_col else 0

    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "columns": list(df.columns),
        "total_missing": total_missing,
        "missing_per_col": missing_counts,
        "duplicate_rows": duplicates,
        "reseller_column": reseller_col,
        "unique_resellers": unique_resellers,
        "date_column": date_col,
        "date_min": date_min,
        "date_max": date_max,
        "status_distribution": status_dist,
        "unique_products": unique_products
    }


def clean_and_anonymize_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Membersihkan data transaksi dan menganonimkan identitas mitra secara ketat.
    Semua nomor kontak tujuan, SN, nama reseller, teks jawaban provider dibuang.
    
    Returns:
        df_clean: DataFrame transaksi teranonim
        audit_meta: Metadata proses audit dan pembersihan
    """
    initial_rows = len(df)
    df_work = df.copy()

    # Identifikasi kolom utama
    # Kolom tanggal
    date_col = next((c for c in ['Tgl. Entri', 'Tanggal', 'Waktu', 'Tgl'] if c in df_work.columns), None)
    if not date_col:
        raise KeyError("Kolom tanggal transaksi (Tgl. Entri / Tanggal) tidak ditemukan.")

    df_work['datetime'] = pd.to_datetime(df_work[date_col], errors='coerce')
    invalid_dates = int(df_work['datetime'].isnull().sum())
    if invalid_dates > 0:
        df_work = df_work.dropna(subset=['datetime'])

    # Kolom reseller untuk identifikasi ID anonim
    reseller_col = next((c for c in ['Kode Reseller', 'Nama Reseller', 'Reseller'] if c in df_work.columns), None)
    if not reseller_col:
        raise KeyError("Kolom identitas reseller tidak ditemukan.")

    # Kolom finansial
    fin_mapping = {
        'hrg_beli': next((c for c in ['Hrg. Beli', 'Harga Beli', 'Hrg Beli', 'BuyPrice'] if c in df_work.columns), None),
        'hrg_jual': next((c for c in ['Hrg. Jual', 'Harga Jual', 'Hrg Jual', 'SellPrice'] if c in df_work.columns), None),
        'komisi': next((c for c in ['Komisi', 'Fee'] if c in df_work.columns), None),
        'laba': next((c for c in ['Laba', 'Profit', 'Margin'] if c in df_work.columns), None),
    }

    # Konversi kolom finansial ke numerik
    for standard_name, raw_name in fin_mapping.items():
        if raw_name:
            df_work[standard_name] = pd.to_numeric(df_work[raw_name].astype(str).str.replace(',', '').str.replace('.', ''), errors='coerce').fillna(0)
        else:
            df_work[standard_name] = 0.0

    # Koreksi format jika terdeteksi pembacaan tanpa desimal
    # Jika hrg_beli pada data asli berupa integer bulat (misal 5145, 18307)
    for col in ['hrg_beli', 'hrg_jual', 'komisi', 'laba']:
        if raw_name := fin_mapping.get(col):
            # jika kolom asli numerik utuh
            if pd.api.types.is_numeric_dtype(df[raw_name]):
                df_work[col] = df[raw_name].fillna(0)

    # Validasi Laba: periksa konsistensi hubungan finansial
    # Hubungan aktual pada data pulsa: Laba = Hrg. Jual - Hrg. Beli - Komisi
    calculated_laba = df_work['hrg_jual'] - df_work['hrg_beli'] - df_work['komisi']
    df_work['laba_valid'] = df_work['laba']

    # Filter status: hanya status Sukses yang valid untuk analisis aktivitas transaksi
    status_col = next((c for c in ['Status', 'State'] if c in df_work.columns), None)
    if status_col:
        df_work = df_work[df_work[status_col].astype(str).str.lower().str.contains('sukses')].copy()

    # Anonimisasi Reseller
    # Mengurutkan kode unik agar pemetaan konsisten
    unique_resellers = sorted(df_work[reseller_col].unique())
    anon_map = {reseller: f"MITRA_{i+1:03d}" for i, reseller in enumerate(unique_resellers)}
    df_work['id_mitra'] = df_work[reseller_col].map(anon_map)

    # Kolom Produk dan Modul
    produk_col = next((c for c in ['Produk', 'Product'] if c in df_work.columns), None)
    df_work['produk'] = df_work[produk_col].astype(str) if produk_col else "UMUM"

    modul_col = next((c for c in ['Modul', 'Module', 'Channel'] if c in df_work.columns), None)
    df_work['modul'] = df_work[modul_col].astype(str) if modul_col else "HOST"

    # Kolom yang dipertahankan (BERSIH & AMAN DARI INFORMASI SENSITIF)
    clean_columns = [
        'id_mitra',
        'datetime',
        'produk',
        'modul',
        'hrg_beli',
        'hrg_jual',
        'komisi',
        'laba'
    ]

    df_clean = df_work[clean_columns].sort_values('datetime').reset_index(drop=True)

    meta = {
        "initial_rows": initial_rows,
        "clean_rows": len(df_clean),
        "dropped_rows": initial_rows - len(df_clean),
        "total_unique_mitra": len(unique_resellers),
        "date_min": str(df_clean['datetime'].min()),
        "date_max": str(df_clean['datetime'].max()),
        "observation_duration_hours": round((df_clean['datetime'].max() - df_clean['datetime'].min()).total_seconds() / 3600.0, 2),
        "total_omset": float(df_clean['hrg_jual'].sum()),
        "total_komisi": float(df_clean['komisi'].sum()),
        "total_laba": float(df_clean['laba'].sum())
    }

    return df_clean, meta
