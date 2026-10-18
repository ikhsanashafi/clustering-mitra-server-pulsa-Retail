"""
Unit Tests untuk Pipeline Clustering Mitra Server Pulsa
Disusun oleh: Ikhsan Ashafi (NIM: 241011400424)
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

# Tambahkan src ke path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(current_dir, '..'))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from src.data_cleaning import load_raw_data, audit_raw_data, clean_and_anonymize_data
from src.feature_engineering import extract_partner_features, get_default_clustering_features
from src.clustering import PartnerClusteringPipeline


class TestPulseClusteringPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Jalur file data uji mentah di folder dataset
        cls.raw_csv_path = os.path.abspath(os.path.join(project_dir, '..', 'data-transaksi-pulsa.csv'))
        if not os.path.exists(cls.raw_csv_path):
            raise FileNotFoundError(f"File dataset tidak ditemukan untuk pengujian: {cls.raw_csv_path}")
        cls.df_raw = load_raw_data(cls.raw_csv_path)

    def test_01_raw_data_integrity(self):
        """Memverifikasi struktur dan jumlah data aktual."""
        self.assertEqual(len(self.df_raw), 2272)
        self.assertIn('TrxID', self.df_raw.columns)
        self.assertIn('Kode Reseller', self.df_raw.columns)
        audit_res = audit_raw_data(self.df_raw)
        self.assertEqual(audit_res['total_rows'], 2272)
        self.assertEqual(audit_res['unique_resellers'], 451)

    def test_02_clean_and_anonymize_security(self):
        """Memverifikasi bahwa pembersihan data menghapus seluruh informasi kontak dan identitas sensitif."""
        df_clean, meta = clean_and_anonymize_data(self.df_raw)

        # Verifikasi tidak ada kolom sensitif
        forbidden_cols = ['Tujuan', 'SN', 'Jawaban Provider', 'Nama Reseller', 'Kode Reseller', 'TrxID']
        for col in forbidden_cols:
            self.assertNotIn(col, df_clean.columns, f"Kolom sensitif {col} masih ditemukan di data bersih!")

        # Verifikasi format id_mitra anonim
        self.assertTrue(df_clean['id_mitra'].str.startswith('MITRA_').all())
        self.assertEqual(meta['total_unique_mitra'], 451)
        self.assertEqual(len(df_clean), 2272)

    def test_03_feature_engineering(self):
        """Memverifikasi agregasi level mitra dan perhitungan metrik bisnis."""
        df_clean, _ = clean_and_anonymize_data(self.df_raw)
        df_features, meta = extract_partner_features(df_clean)

        self.assertEqual(len(df_features), 451)
        self.assertIn('id_mitra', df_features.columns)

        default_feats = get_default_clustering_features()
        for f in default_feats:
            self.assertIn(f, df_features.columns)
            self.assertFalse(df_features[f].isnull().any(), f"Fitur {f} mengandung nilai null!")

        # Pastikan tidak ada transaksi bernilai negatif
        self.assertTrue((df_features['jumlah_transaksi'] >= 1).all())
        self.assertTrue((df_features['rentang_aktif_menit'] >= 0).all())

    def test_04_clustering_pipeline(self):
        """Memverifikasi pelatihan K-Means, evaluasi Elbow/Silhouette, dan profil klaster."""
        df_clean, _ = clean_and_anonymize_data(self.df_raw)
        df_features, _ = extract_partner_features(df_clean)
        feature_cols = get_default_clustering_features()

        pipeline = PartnerClusteringPipeline(use_log_transform=True, random_state=42)
        X_scaled = pipeline.prepare_features(df_features, feature_cols)

        # Evaluasi K=2..4
        eval_df = pipeline.evaluate_clusters(X_scaled, k_range=range(2, 5))
        self.assertEqual(len(eval_df), 3)
        self.assertTrue(all(eval_df['Silhouette_Score'] > 0.35))

        # Pelatihan K=3
        df_clustered = pipeline.fit_predict(df_features, feature_cols, n_clusters=3)
        self.assertIn('cluster', df_clustered.columns)
        self.assertIn('nama_cluster', df_clustered.columns)
        self.assertIn('pca_1', df_clustered.columns)
        self.assertIn('pca_2', df_clustered.columns)

        # Profil klaster
        mean_prof, median_prof = pipeline.get_cluster_profiles(df_clustered)
        self.assertEqual(len(mean_prof), 3)
        self.assertEqual(mean_prof['jumlah_mitra'].sum(), 451)


if __name__ == '__main__':
    unittest.main()
