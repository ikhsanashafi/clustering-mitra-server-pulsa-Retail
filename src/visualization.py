"""
Modul Visualisasi Data dan Hasil Clustering
Disusun oleh: Ikhsan Ashafi (NIM: 241011400424)
Tujuan: Menghasilkan grafik EDA, kurva evaluasi model, dan plot visualisasi klaster berkualitas akademik.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional

# Konfigurasi gaya visualisasi standar akademik
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300
sns.set_theme(style="whitegrid", palette="deep")


def plot_hourly_activity(df_clean: pd.DataFrame, save_path: Optional[str] = None) -> plt.Figure:
    """
    Grafik garis & batang distribusi transaksi per jam selama periode pengamatan.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    hourly_counts = df_clean['datetime'].dt.hour.value_counts().sort_index()

    sns.barplot(x=hourly_counts.index, y=hourly_counts.values, ax=ax, color='#1f77b4', alpha=0.85)
    sns.lineplot(x=range(len(hourly_counts)), y=hourly_counts.values, ax=ax, color='#d62728', marker='o', linewidth=2.2)

    ax.set_title("Distribusi Volume Transaksi per Jam (15 Oktober 2026)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Jam Operasional (WIB)", fontsize=11)
    ax.set_ylabel("Jumlah Transaksi", fontsize=11)
    ax.set_xticklabels([f"{h:02d}:00" for h in hourly_counts.index], rotation=0)

    for i, v in enumerate(hourly_counts.values):
        ax.text(i, v + 12, str(v), ha='center', va='bottom', fontsize=9, fontweight='semibold')

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches='tight')
    return fig


def plot_top_products(df_clean: pd.DataFrame, top_n: int = 10, save_path: Optional[str] = None) -> plt.Figure:
    """
    Grafik 10 produk server pulsa terpopuler berdasarkan frekuensi transaksi.
    """
    fig, ax = plt.subplots(figsize=(10, 5.5))
    top_prod = df_clean['produk'].value_counts().head(top_n)

    sns.barplot(x=top_prod.values, y=top_prod.index, ax=ax, palette="Blues_r")
    ax.set_title(f"Top {top_n} Produk Server Pulsa Terpopuler", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Frekuensi Transaksi", fontsize=11)
    ax.set_ylabel("Kode Produk", fontsize=11)

    for i, v in enumerate(top_prod.values):
        ax.text(v + 5, i, f"{v:,} trx", va='center', fontsize=9, fontweight='semibold')

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches='tight')
    return fig


def plot_elbow_and_silhouette(eval_df: pd.DataFrame, save_path: Optional[str] = None) -> plt.Figure:
    """
    Grafik ganda: Kurva Elbow (Inertia) dan Kurva Silhouette Score untuk K=2 hingga K=6.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # Plot 1: Elbow Curve
    ax1.plot(eval_df['K'], eval_df['Inertia'], marker='o', color='#1f77b4', linewidth=2.2, markersize=8)
    ax1.set_title("Evaluasi Elbow Method (Inersia)", fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlabel("Jumlah Klaster (K)", fontsize=10)
    ax1.set_ylabel("Within-Cluster Sum of Squares (Inersia)", fontsize=10)
    ax1.set_xticks(eval_df['K'])
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Plot 2: Silhouette Score
    ax2.plot(eval_df['K'], eval_df['Silhouette_Score'], marker='s', color='#2ca02c', linewidth=2.2, markersize=8)
    ax2.set_title("Evaluasi Silhouette Score", fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlabel("Jumlah Klaster (K)", fontsize=10)
    ax2.set_ylabel("Nilai Rata-rata Silhouette", fontsize=10)
    ax2.set_xticks(eval_df['K'])
    ax2.grid(True, linestyle='--', alpha=0.6)

    # Menandai titik K terpilih (K=3)
    k_opt = 3
    if k_opt in eval_df['K'].values:
        sil_opt = eval_df.loc[eval_df['K'] == k_opt, 'Silhouette_Score'].values[0]
        ax2.annotate(f"K={k_opt} Terpilih\n(Skor: {sil_opt:.3f})",
                     xy=(k_opt, sil_opt),
                     xytext=(k_opt + 0.3, sil_opt - 0.02),
                     arrowprops=dict(facecolor='black', shrink=0.08, width=1.5, headwidth=6),
                     fontweight='bold', fontsize=9)

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches='tight')
    return fig


def plot_pca_clusters(df_clustered: pd.DataFrame, save_path: Optional[str] = None) -> plt.Figure:
    """
    Visualisasi sebaran klaster mitra dalam ruang proyeksi 2D PCA.
    """
    fig, ax = plt.subplots(figsize=(10, 6.5))

    palette = {
        "Mitra Sporadis (Aktivitas Rendah)": "#1f77b4",
        "Mitra Berkala (Aktivitas Menengah)": "#ff7f0e",
        "Mitra Utama (Aktivitas Intensif)": "#2ca02c"
    }

    # Jika nama klaster berbeda, gunakan palet dinamis
    hue_col = 'nama_cluster' if 'nama_cluster' in df_clustered.columns else 'cluster'
    unique_hues = df_clustered[hue_col].unique()
    custom_palette = [palette.get(h, sns.color_palette("deep")[i % 10]) for i, h in enumerate(unique_hues)]

    sns.scatterplot(
        data=df_clustered,
        x='pca_1',
        y='pca_2',
        hue=hue_col,
        palette=palette if all(h in palette for h in unique_hues) else 'deep',
        alpha=0.85,
        s=65,
        edgecolor='w',
        linewidth=0.5,
        ax=ax
    )

    ax.set_title("Visualisasi Hasil Clustering Mitra Server Pulsa (Proyeksi 2D PCA)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Principal Component 1 (Dimensi Dominan Aktivitas)", fontsize=11)
    ax.set_ylabel("Principal Component 2 (Dimensi Pola/Variasi)", fontsize=11)
    ax.legend(title="Segmen Mitra", title_fontsize='10', loc='best', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches='tight')
    return fig


def plot_cluster_metrics_summary(mean_profile: pd.DataFrame, save_path: Optional[str] = None) -> plt.Figure:
    """
    Perbandingan karakteristik metrik utama antar-klaster (Frekuensi Transaksi, Omset, Durasi Aktif).
    """
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.8))

    cluster_labels = mean_profile['nama_cluster'].apply(lambda x: x.split(' (')[0])
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    # Subplot 1: Rata-rata Jumlah Transaksi
    sns.barplot(x=cluster_labels, y=mean_profile['jumlah_transaksi'], ax=ax1, palette=colors)
    ax1.set_title("Rata-rata Transaksi (Trx)", fontweight='bold', fontsize=11)
    ax1.set_ylabel("Jumlah Transaksi")
    ax1.set_xlabel("")
    for i, v in enumerate(mean_profile['jumlah_transaksi']):
        ax1.text(i, v + (0.05 * v if v > 0 else 0.5), f"{v:.1f}", ha='center', fontweight='bold', fontsize=9)

    # Subplot 2: Rata-rata Omset Total
    sns.barplot(x=cluster_labels, y=mean_profile['total_nilai_transaksi'] / 1e3, ax=ax2, palette=colors)
    ax2.set_title("Rata-rata Omset Total (Ribu Rp)", fontweight='bold', fontsize=11)
    ax2.set_ylabel("Ribuan Rupiah")
    ax2.set_xlabel("")
    for i, v in enumerate(mean_profile['total_nilai_transaksi'] / 1e3):
        ax2.text(i, v + (0.05 * v), f"{v:,.0f}k", ha='center', fontweight='bold', fontsize=9)

    # Subplot 3: Rata-rata Rentang Aktif
    sns.barplot(x=cluster_labels, y=mean_profile['rentang_aktif_menit'], ax=ax3, palette=colors)
    ax3.set_title("Rata-rata Rentang Aktif (Menit)", fontweight='bold', fontsize=11)
    ax3.set_ylabel("Menit")
    ax3.set_xlabel("")
    for i, v in enumerate(mean_profile['rentang_aktif_menit']):
        ax3.text(i, v + 6, f"{v:.1f} m", ha='center', fontweight='bold', fontsize=9)

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches='tight')
    return fig
