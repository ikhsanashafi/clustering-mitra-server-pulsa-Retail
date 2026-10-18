"""
Modul Machine Learning & Clustering K-Means
Disusun oleh: Ikhsan Ashafi (NIM: 241011400424)
Tujuan: Melakukan penskalaan fitur, evaluasi jumlah klaster (Elbow & Silhouette),
pelatihan model K-Means, reduksi dimensi PCA, dan pemrofilan segmen mitra.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.decomposition import PCA


class PartnerClusteringPipeline:
    """
    Pipeline lengkap pembelajaran mesin untuk clustering mitra server pulsa.
    """

    def __init__(self, use_log_transform: bool = True, random_state: int = 42):
        self.use_log_transform = use_log_transform
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.kmeans: Optional[KMeans] = None
        self.pca: Optional[PCA] = None
        self.feature_names: List[str] = []
        self.cluster_names: Dict[int, str] = {}

    def prepare_features(self, df_features: pd.DataFrame, feature_cols: List[str]) -> np.ndarray:
        """
        Melakukan transformasi data (log1p jika diaktifkan) dan standarisasi (StandardScaler).
        """
        self.feature_names = feature_cols
        X_raw = df_features[feature_cols].values.astype(float)

        if self.use_log_transform:
            # log1p aman untuk data bernilai >= 0 (frekuensi, omset, durasi)
            # Clip nilai negatif minimal ke 0 untuk mencegah NaN
            X_clean = np.clip(X_raw, a_min=0, a_max=None)
            X_trans = np.log1p(X_clean)
        else:
            X_trans = X_raw

        X_scaled = self.scaler.fit_transform(X_trans)
        return X_scaled

    def evaluate_clusters(self, X_scaled: np.ndarray, k_range: range = range(2, 7)) -> pd.DataFrame:
        """
        Menghitung metrik evaluasi Elbow (Inertia), Silhouette Score,
        Calinski-Harabasz, dan Davies-Bouldin untuk rentang nilai K.
        """
        results = []
        for k in k_range:
            km = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            labels = km.fit_predict(X_scaled)
            inertia = float(km.inertia_)
            sil = float(silhouette_score(X_scaled, labels))
            ch = float(calinski_harabasz_score(X_scaled, labels))
            db = float(davies_bouldin_score(X_scaled, labels))

            results.append({
                'K': k,
                'Inertia': inertia,
                'Silhouette_Score': sil,
                'Calinski_Harabasz': ch,
                'Davies_Bouldin': db
            })

        return pd.DataFrame(results)

    def fit_predict(self, df_features: pd.DataFrame, feature_cols: List[str], n_clusters: int = 3) -> pd.DataFrame:
        """
        Melatih K-Means pada data fitur dan memetakan label klaster secara terurut logis.
        Label diurutkan berdasarkan rata-rata volume transaksi mitra (0 = Rendah, 1 = Menengah, 2 = Tinggi).
        """
        X_scaled = self.prepare_features(df_features, feature_cols)
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=self.random_state, n_init=10)
        raw_labels = self.kmeans.fit_predict(X_scaled)

        # Mengurutkan label klaster secara konsisten berdasarkan rata-rata jumlah transaksi
        df_result = df_features.copy()
        df_result['raw_cluster'] = raw_labels

        mean_trx_per_cluster = df_result.groupby('raw_cluster')['jumlah_transaksi'].mean().sort_values()
        label_mapping = {old_label: new_label for new_label, old_label in enumerate(mean_trx_per_cluster.index)}
        df_result['cluster'] = df_result['raw_cluster'].map(label_mapping)
        df_result.drop(columns=['raw_cluster'], inplace=True)

        # Penamaan segmen bisnis berdasarkan peringkat aktivitas
        if n_clusters == 3:
            self.cluster_names = {
                0: "Mitra Sporadis (Aktivitas Rendah)",
                1: "Mitra Berkala (Aktivitas Menengah)",
                2: "Mitra Utama (Aktivitas Intensif)"
            }
        elif n_clusters == 4:
            self.cluster_names = {
                0: "Mitra Sangat Rendah",
                1: "Mitra Ringan",
                2: "Mitra Menengah",
                3: "Mitra Intensif"
            }
        else:
            self.cluster_names = {i: f"Cluster {i+1}" for i in range(n_clusters)}

        df_result['nama_cluster'] = df_result['cluster'].map(self.cluster_names)

        # Menghitung proyeksi PCA 2D
        self.pca = PCA(n_components=2, random_state=self.random_state)
        pca_coords = self.pca.fit_transform(X_scaled)
        df_result['pca_1'] = pca_coords[:, 0]
        df_result['pca_2'] = pca_coords[:, 1]

        return df_result

    def get_cluster_profiles(self, df_clustered: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Membuat ringkasan profil statistik deskriptif (rata-rata dan median) untuk setiap klaster.
        """
        metric_cols = [
            'jumlah_transaksi',
            'total_nilai_transaksi',
            'rata_rata_nilai_transaksi',
            'total_komisi',
            'total_laba',
            'jumlah_produk_unik',
            'rentang_aktif_menit'
        ]
        # Hanya gunakan kolom yang tersedia
        valid_metrics = [c for c in metric_cols if c in df_clustered.columns]

        mean_profile = df_clustered.groupby(['cluster', 'nama_cluster'])[valid_metrics].mean().reset_index()
        median_profile = df_clustered.groupby(['cluster', 'nama_cluster'])[valid_metrics].median().reset_index()

        # Tambahkan jumlah anggota dan persentase
        cluster_counts = df_clustered.groupby('cluster').size()
        total_mitra = len(df_clustered)
        mean_profile['jumlah_mitra'] = mean_profile['cluster'].map(cluster_counts)
        mean_profile['persentase_mitra'] = (mean_profile['jumlah_mitra'] / total_mitra * 100).round(2)

        return mean_profile, median_profile
