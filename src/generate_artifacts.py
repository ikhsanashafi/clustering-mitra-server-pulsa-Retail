"""
Script untuk memproses dataset, menghasilkan data teranonim,
menjalankan evaluasi clustering, dan mengekspor visualisasi akademik.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

base_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(base_dir, '..'))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from src.data_cleaning import load_raw_data, audit_raw_data, clean_and_anonymize_data
from src.feature_engineering import extract_partner_features, get_default_clustering_features
from src.clustering import PartnerClusteringPipeline
from src.visualization import (
    plot_hourly_activity,
    plot_top_products,
    plot_elbow_and_silhouette,
    plot_pca_clusters,
    plot_cluster_metrics_summary
)

def run():
    raw_path = os.path.abspath(os.path.join(project_dir, '..', 'data-transaksi-pulsa.csv'))
    print(f"Loading raw data from: {raw_path}")
    df_raw = load_raw_data(raw_path)

    # 1. Cleaning & Anonymization
    df_clean, clean_meta = clean_and_anonymize_data(df_raw)
    data_dir = os.path.join(project_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    anon_trx_path = os.path.join(data_dir, 'anonymized_transactions.csv')
    df_clean.to_csv(anon_trx_path, index=False)
    print(f"Saved anonymized transactions to {anon_trx_path}")

    # 2. Feature Engineering
    df_features, feat_meta = extract_partner_features(df_clean)
    mitra_feat_path = os.path.join(data_dir, 'mitra_features.csv')
    df_features.to_csv(mitra_feat_path, index=False)
    print(f"Saved partner features to {mitra_feat_path}")

    # 3. Clustering Pipeline
    feature_cols = get_default_clustering_features()
    pipeline = PartnerClusteringPipeline(use_log_transform=True, random_state=42)
    X_scaled = pipeline.prepare_features(df_features, feature_cols)

    # Evaluasi K=2..6
    eval_df = pipeline.evaluate_clusters(X_scaled, k_range=range(2, 7))
    eval_csv_path = os.path.join(project_dir, 'outputs', 'clustering_evaluation.csv')
    eval_df.to_csv(eval_csv_path, index=False)
    print("Clustering evaluation:\n", eval_df)

    # Fit K=3 (Optimal per Silhouette & Business interpretability)
    df_clustered = pipeline.fit_predict(df_features, feature_cols, n_clusters=3)
    clustered_csv_path = os.path.join(data_dir, 'mitra_clustered.csv')
    df_clustered.to_csv(clustered_csv_path, index=False)

    mean_prof, median_prof = pipeline.get_cluster_profiles(df_clustered)
    prof_path = os.path.join(project_dir, 'outputs', 'cluster_profiles_mean.csv')
    mean_prof.to_csv(prof_path, index=False)

    # 4. Generate Visualizations
    fig_dir = os.path.join(project_dir, 'outputs', 'figures')
    os.makedirs(fig_dir, exist_ok=True)

    print("Generating figures...")
    plot_hourly_activity(df_clean, save_path=os.path.join(fig_dir, 'eda_hourly.png'))
    plot_top_products(df_clean, top_n=10, save_path=os.path.join(fig_dir, 'eda_top_products.png'))
    plot_elbow_and_silhouette(eval_df, save_path=os.path.join(fig_dir, 'eval_elbow_silhouette.png'))
    plot_pca_clusters(df_clustered, save_path=os.path.join(fig_dir, 'pca_clusters_2d.png'))
    plot_cluster_metrics_summary(mean_prof, save_path=os.path.join(fig_dir, 'cluster_metrics_summary.png'))

    # Also generate feature distribution plot
    import matplotlib.pyplot as plt
    import seaborn as sns
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    sns.histplot(df_features['jumlah_transaksi'], bins=30, kde=True, ax=axes[0, 0], color='#1f77b4')
    axes[0, 0].set_title("Distribusi Jumlah Transaksi per Mitra", fontweight='bold')
    axes[0, 0].set_yscale('log')
    axes[0, 0].set_xlabel("Jumlah Transaksi (Skala Log)")

    sns.histplot(df_features['total_nilai_transaksi'] / 1e3, bins=30, kde=True, ax=axes[0, 1], color='#2ca02c')
    axes[0, 1].set_title("Distribusi Total Omset per Mitra (Ribu Rp)", fontweight='bold')
    axes[0, 1].set_yscale('log')
    axes[0, 1].set_xlabel("Omset (Ribu Rp, Skala Log)")

    sns.histplot(df_features['jumlah_produk_unik'], bins=15, discrete=True, ax=axes[1, 0], color='#ff7f0e')
    axes[1, 0].set_title("Distribusi Keragaman Produk per Mitra", fontweight='bold')
    axes[1, 0].set_xlabel("Jumlah Produk Unik")

    sns.histplot(df_features['rentang_aktif_menit'], bins=30, kde=True, ax=axes[1, 1], color='#9467bd')
    axes[1, 1].set_title("Distribusi Rentang Waktu Aktif (Menit)", fontweight='bold')
    axes[1, 1].set_xlabel("Rentang Aktif (Menit)")

    plt.tight_layout()
    fig.savefig(os.path.join(fig_dir, 'eda_feature_dist.png'), bbox_inches='tight')
    plt.close('all')

    print("All outputs generated successfully!")

if __name__ == '__main__':
    run()
