"""
Aplikasi Web Interaktif: Clustering Perilaku Mitra Server Pulsa
Menggunakan Algoritma K-Means & Streamlit
Disusun oleh:
- Nama: Ikhsan Ashafi
- NIM: 241011400424
- Program Studi: Teknik Informatika S1
- Mata Kuliah: Machine Learning
"""

import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Pastikan folder project ada di sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

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

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Clustering Mitra Server Pulsa | Ikhsan Ashafi",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling CSS untuk estetika modern, rapi, dan profesional
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(30, 58, 138, 0.15);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 1.85rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    
    .main-header p {
        color: #e0e7ff;
        font-size: 0.95rem;
        margin-bottom: 0;
    }
    
    .author-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-top: 10px;
    }
    
    .metric-card {
        background: white;
        padding: 18px 20px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    
    .metric-card .title {
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card .value {
        color: #0f172a;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 4px 0;
    }
    
    .metric-card .subtitle {
        color: #94a3b8;
        font-size: 0.78rem;
    }
    
    .cluster-card-0 {
        border-left: 5px solid #1f77b4;
        background: #f8fafc;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .cluster-card-1 {
        border-left: 5px solid #ff7f0e;
        background: #f8fafc;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .cluster-card-2 {
        border-left: 5px solid #2ca02c;
        background: #f8fafc;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_default_dataset():
    """Memuat dataset anonim bawaan yang tersimpan lokal secara aman."""
    data_path = os.path.join(BASE_DIR, 'data', 'anonymized_transactions.csv')
    if os.path.exists(data_path):
        df_clean = pd.read_csv(data_path)
        df_clean['datetime'] = pd.to_datetime(df_clean['datetime'])
        return df_clean
    
    # Fallback jika belum diekstrak: muat dari parent csv jika tersedia
    raw_path = os.path.abspath(os.path.join(BASE_DIR, '..', 'data-transaksi-pulsa.csv'))
    if os.path.exists(raw_path):
        df_raw = load_raw_data(raw_path)
        df_clean, _ = clean_and_anonymize_data(df_raw)
        return df_clean
    return None


def main():
    # Header Utama
    st.markdown("""
    <div class="main-header">
        <h1>⚡ Clustering Perilaku Mitra Server Pulsa</h1>
        <p>Analisis Segmentasi Mitra Berdasarkan Pola Transaksi Menggunakan Algoritma K-Means</p>
        <div class="author-badge">
            👤 <b>Ikhsan Ashafi</b> | NIM: 241011400424 | Teknik Informatika S1 | Machine Learning
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Kontrol
    st.sidebar.image("https://img.icons8.com/fluency/96/server.png", width=64)
    st.sidebar.title("Pengaturan Analisis")

    data_source_opt = st.sidebar.radio(
        "Sumber Data:",
        ["Dataset Penelitian Bawaan (451 Mitra)", "Unggah File Baru (.csv / .xlsx)"],
        index=0
    )

    df_clean = None

    if data_source_opt == "Dataset Penelitian Bawaan (451 Mitra)":
        df_clean = load_default_dataset()
        if df_clean is None:
            st.error("Dataset bawaan tidak ditemukan. Silakan unggah file CSV atau Excel.")
            return
        st.sidebar.success("✓ Dataset penelitian berhasil dimuat.")
    else:
        uploaded_file = st.sidebar.file_uploader(
            "Unggah Data Transaksi Server Pulsa",
            type=["csv", "xlsx", "xls"],
            help="File Anda akan langsung diproses di memori dan dianonimkan secara ketat tanpa menyimpan data sensitif."
        )
        if uploaded_file is not None:
            try:
                with st.spinner("Memproses dan menganonimkan data..."):
                    df_raw = load_raw_data(uploaded_file)
                    df_clean, meta_clean = clean_and_anonymize_data(df_raw)
                st.sidebar.success(f"✓ Berhasil memproses {meta_clean['clean_rows']} baris dari {meta_clean['total_unique_mitra']} mitra!")
            except Exception as e:
                st.sidebar.error(f"Gagal memproses file: {e}")
                return
        else:
            st.info("👋 Silakan unggah file Excel atau CSV transaksi pulsa pada sidebar, atau pilih opsi 'Dataset Penelitian Bawaan'.")
            return

    # Sidebar Hyperparameters
    st.sidebar.markdown("---")
    st.sidebar.subheader("Konfigurasi K-Means")
    k_clusters = st.sidebar.slider("Jumlah Klaster (K):", min_value=2, max_value=6, value=3, step=1)
    use_log = st.sidebar.checkbox("Gunakan Log-Transformation (log1p)", value=True, help="Menyeimbangkan sebaran fitur finansial & transaksi yang skewed")

    # Feature Engineering
    df_features, feat_meta = extract_partner_features(df_clean)
    feature_cols = get_default_clustering_features()

    # Model Execution
    pipeline = PartnerClusteringPipeline(use_log_transform=use_log, random_state=42)
    X_scaled = pipeline.prepare_features(df_features, feature_cols)
    eval_df = pipeline.evaluate_clusters(X_scaled, k_range=range(2, 7))
    df_clustered = pipeline.fit_predict(df_features, feature_cols, n_clusters=k_clusters)
    mean_prof, median_prof = pipeline.get_cluster_profiles(df_clustered)

    # Ringkasan KPI Utama di Atas
    c1, c2, c3, c4, c5 = st.columns(5)
    total_trx = len(df_clean)
    total_mitra = len(df_features)
    total_omset = df_clean['hrg_jual'].sum()
    rentang_jam = (df_clean['datetime'].max() - df_clean['datetime'].min()).total_seconds() / 3600.0

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="title">Total Mitra</div>
            <div class="value">{total_mitra:,}</div>
            <div class="subtitle">Entitas unik teranonim</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="title">Total Transaksi</div>
            <div class="value">{total_trx:,}</div>
            <div class="subtitle">100% Status Sukses</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="title">Total Omset</div>
            <div class="value">Rp {total_omset/1e6:.1f} Jt</div>
            <div class="subtitle">Perputaran finansial</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="title">Durasi Jendela</div>
            <div class="value">{rentang_jam:.1f} Jam</div>
            <div class="subtitle">{df_clean['datetime'].dt.strftime('%d-%m-%Y').iloc[0]}</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        sil_current = eval_df.loc[eval_df['K'] == k_clusters, 'Silhouette_Score'].values[0]
        st.markdown(f"""
        <div class="metric-card">
            <div class="title">Silhouette Score</div>
            <div class="value">{sil_current:.3f}</div>
            <div class="subtitle">Kualitas partisi K={k_clusters}</div>
        </div>
        """, unsafe_allow_html=True)

    # Tab Navigasi Aplikasi
    tab_eda, tab_eval, tab_clusters, tab_profiles, tab_data = st.tabs([
        "📊 Eksplorasi Data (EDA)",
        "📈 Evaluasi Model (Elbow & Silhouette)",
        "🎯 Visualisasi Klaster (PCA 2D)",
        "📋 Profil & Interpretasi Bisnis",
        "🔍 Data Mitra & Ekspor"
    ])

    # TAB 1: EDA
    with tab_eda:
        st.subheader("Eksplorasi Karakteristik Transaksi Mitra")
        col_eda1, col_eda2 = st.columns(2)
        with col_eda1:
            st.markdown("##### 🕒 Aktivitas Transaksi per Jam")
            fig_hourly = plot_hourly_activity(df_clean)
            st.pyplot(fig_hourly)
            plt.close(fig_hourly)
            st.caption("Pola transaksi meningkat tajam di malam hari dengan puncak pada pukul 21:00 WIB.")

        with col_eda2:
            st.markdown("##### 📱 10 Produk Server Pulsa Terpopuler")
            fig_prod = plot_top_products(df_clean, top_n=10)
            st.pyplot(fig_prod)
            plt.close(fig_prod)
            st.caption("Produk didominasi oleh voucher paket/e-wallet, token listrik PLN, dan pulsa reguler.")

        st.markdown("---")
        st.markdown("##### 📐 Distribusi Fitur Agregasi Mitra")
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            st.metric("Rerata Trx / Mitra", f"{df_features['jumlah_transaksi'].mean():.2f} trx", f"Median: {df_features['jumlah_transaksi'].median():.0f}")
        with f2:
            st.metric("Rerata Omset / Mitra", f"Rp {df_features['total_nilai_transaksi'].mean():,.0f}", f"Median: Rp {df_features['total_nilai_transaksi'].median():,.0f}")
        with f3:
            st.metric("Rerata Variasi Produk", f"{df_features['jumlah_produk_unik'].mean():.2f} jenis", f"Max: {df_features['jumlah_produk_unik'].max():.0f}")
        with f4:
            st.metric("Rerata Durasi Aktif", f"{df_features['rentang_aktif_menit'].mean():.1f} menit", f"Max: {df_features['rentang_aktif_menit'].max():.1f} m")

    # TAB 2: Evaluasi Model
    with tab_eval:
        st.subheader("Evaluasi Penentuan Jumlah Klaster Optimal")
        st.write("""
        Pemilihan nilai $K$ terbaik dievaluasi dengan menyeimbangkan **Elbow Method (Inersia)** dan **Silhouette Score** 
        pada rentang $K=2$ hingga $K=6$.
        """)

        fig_eval = plot_elbow_and_silhouette(eval_df)
        st.pyplot(fig_eval)
        plt.close(fig_eval)

        st.markdown("##### Tabel Metrik Kuantitatif Evaluasi Klaster")
        eval_display = eval_df.copy()
        eval_display.columns = ['Jumlah Klaster (K)', 'Inersia (Elbow)', 'Silhouette Score', 'Calinski-Harabasz', 'Davies-Bouldin']
        eval_display['Silhouette Score'] = eval_display['Silhouette Score'].round(4)
        eval_display['Calinski-Harabasz'] = eval_display['Calinski-Harabasz'].round(2)
        eval_display['Davies-Bouldin'] = eval_display['Davies-Bouldin'].round(4)
        eval_display['Inersia (Elbow)'] = eval_display['Inersia (Elbow)'].round(2)
        st.dataframe(eval_display, use_container_width=True)

        st.info("""
        💡 **Kesimpulan Pemilihan Model:**
        - **K=3** dipilih sebagai solusi partisi paling optimal karena memiliki nilai Silhouette Score yang stabil (**0.421**), 
          penurunan inersia yang mulai melandai pada Elbow Curve, serta pemisahan klaster yang sangat masuk akal secara operasional bisnis:
          kelompok transaksi sporadis, menengah berkala, dan mitra inti bervolume tinggi.
        """)

    # TAB 3: Visualisasi Klaster
    with tab_clusters:
        st.subheader("Peta Persebaran Segmen Mitra (Proyeksi 2D PCA)")
        var_ratio = pipeline.pca.explained_variance_ratio_ if pipeline.pca else [0, 0]
        st.write(f"""
        Visualisasi di bawah memproyeksikan matriks fitur 5-dimensi ke dalam bidang 2D menggunakan 
        *Principal Component Analysis (PCA)*. 
        PC1 mencakup **{var_ratio[0]*100:.1f}%** variansi data dan PC2 mencakup **{var_ratio[1]*100:.1f}%** variansi.
        """)

        fig_pca = plot_pca_clusters(df_clustered)
        st.pyplot(fig_pca)
        plt.close(fig_pca)

        st.markdown("---")
        st.subheader("Hubungan Antar-Fitur Kunci")
        col_biv1, col_biv2 = st.columns(2)
        with col_biv1:
            fig_biv1, ax_biv1 = plt.subplots(figsize=(8, 5))
            sns.scatterplot(
                data=df_clustered,
                x='jumlah_transaksi',
                y='total_nilai_transaksi',
                hue='nama_cluster',
                alpha=0.8,
                s=60,
                ax=ax_biv1
            )
            ax_biv1.set_xscale('log')
            ax_biv1.set_yscale('log')
            ax_biv1.set_title("Frekuensi Transaksi vs Total Omset (Skala Log)", fontweight='bold')
            ax_biv1.set_xlabel("Jumlah Transaksi (Log)")
            ax_biv1.set_ylabel("Total Omset (Log)")
            st.pyplot(fig_biv1)
            plt.close(fig_biv1)

        with col_biv2:
            fig_biv2, ax_biv2 = plt.subplots(figsize=(8, 5))
            sns.scatterplot(
                data=df_clustered,
                x='rentang_aktif_menit',
                y='total_nilai_transaksi',
                hue='nama_cluster',
                alpha=0.8,
                s=60,
                ax=ax_biv2
            )
            ax_biv2.set_yscale('log')
            ax_biv2.set_title("Durasi Aktif vs Total Omset", fontweight='bold')
            ax_biv2.set_xlabel("Rentang Aktif (Menit)")
            ax_biv2.set_ylabel("Total Omset (Log)")
            st.pyplot(fig_biv2)
            plt.close(fig_biv2)

    # TAB 4: Profil & Interpretasi
    with tab_profiles:
        st.subheader("Profil Karakteristik Segmen Mitra")

        fig_summary = plot_cluster_metrics_summary(mean_profile)
        st.pyplot(fig_summary)
        plt.close(fig_summary)

        st.markdown("##### Tabel Rata-rata Nilai Metrik per Segmen")
        display_mean = mean_profile.copy()
        display_mean['total_nilai_transaksi'] = display_mean['total_nilai_transaksi'].apply(lambda x: f"Rp {x:,.0f}")
        display_mean['rata_rata_nilai_transaksi'] = display_mean['rata_rata_nilai_transaksi'].apply(lambda x: f"Rp {x:,.0f}")
        display_mean['total_komisi'] = display_mean['total_komisi'].apply(lambda x: f"Rp {x:,.0f}")
        display_mean['total_laba'] = display_mean['total_laba'].apply(lambda x: f"Rp {x:,.2f}")
        display_mean['jumlah_transaksi'] = display_mean['jumlah_transaksi'].round(2)
        display_mean['jumlah_produk_unik'] = display_mean['jumlah_produk_unik'].round(2)
        display_mean['rentang_aktif_menit'] = display_mean['rentang_aktif_menit'].round(1)
        st.dataframe(display_mean, use_container_width=True)

        st.markdown("---")
        st.subheader("Interpretasi Bisnis & Rekomendasi Aksi")

        for _, row in mean_profile.iterrows():
            c_id = int(row['cluster'])
            c_name = row['nama_cluster']
            c_count = int(row['jumlah_mitra'])
            c_pct = row['persentase_mitra']
            c_trx = row['jumlah_transaksi']
            c_omset = row['total_nilai_transaksi']
            c_dur = row['rentang_aktif_menit']

            card_class = f"cluster-card-{c_id % 3}"
            if c_id == 0:
                karakter = "Mitra bertransaksi tunggal atau sangat sporadis, durasi operasional rata-rata di bawah 1 menit."
                rekomendasi = "Kirimkan promo notifikasi saldo atau cashback deposit kecil untuk mendorong transaksi berulang."
            elif c_id == 1:
                karakter = "Mitra ritel reguler bertransaksi secara berkala (rata-rata 3.5 transaksi) sepanjang sore hingga malam hari."
                rekomendasi = "Berikan skema poin loyalitas per transaksi dan pengingat stok produk terpopuler."
            else:
                karakter = "Mitra jangkar dengan frekuensi sangat tinggi (rata-rata 22 transaksi, omset jutaan rupiah) dan jam operasional panjang."
                rekomendasi = "Sediakan jalur koneksi khusus (dedicated host), prioritas respon server, dan diskon harga grosir."

            st.markdown(f"""
            <div class="{card_class}">
                <h4>🏷️ {c_name}</h4>
                <p><b>Jumlah Anggota:</b> {c_count} Mitra ({c_pct:.1f}% dari total) | <b>Rata-rata Trx:</b> {c_trx:.1f} trx | <b>Rata-rata Omset:</b> Rp {c_omset:,.0f} | <b>Durasi:</b> {c_dur:.1f} m</p>
                <p><b>Karakteristik:</b> {karakter}</p>
                <p><b>Rekomendasi Operasional:</b> {rekomendasi}</p>
            </div>
            """, unsafe_allow_html=True)

        st.warning("""
        ⚠️ **Batasan Penelitian Akademik:**
        Data yang dianalisis merupakan transaksi selama jendela observasi tanggal 15 Oktober 2026 (periode ~8.5 jam). 
        Oleh karena itu, hasil pengelompokan menggambarkan perilaku operasional mitra pada jendela pengamatan tersebut, 
        dan tidak boleh disimpulkan sebagai loyalitas jangka panjang atau kapasitas kredit tetap tanpa data historis multi-bulan.
        """)

    # TAB 5: Data Mitra & Ekspor
    with tab_data:
        st.subheader("Data Hasil Segmentasi Mitra")

        # Filter interaktif
        col_f1, col_f2 = st.columns([2, 3])
        with col_f1:
            selected_cluster = st.selectbox(
                "Filter Berdasarkan Klaster:",
                ["Semua Klaster"] + list(df_clustered['nama_cluster'].unique())
            )
        with col_f2:
            search_query = st.text_input("Cari ID Mitra (contoh: MITRA_001):", "")

        filtered_df = df_clustered.copy()
        if selected_cluster != "Semua Klaster":
            filtered_df = filtered_df[filtered_df['nama_cluster'] == selected_cluster]
        if search_query.strip():
            filtered_df = filtered_df[filtered_df['id_mitra'].str.contains(search_query.strip(), case=False)]

        st.write(f"Menampilkan **{len(filtered_df)}** mitra:")
        view_cols = [
            'id_mitra', 'nama_cluster', 'jumlah_transaksi', 'total_nilai_transaksi',
            'rata_rata_nilai_transaksi', 'jumlah_produk_unik', 'rentang_aktif_menit'
        ]
        st.dataframe(filtered_df[view_cols], use_container_width=True)

        # Tombol Unduh Hasil
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Data Hasil Klaster (.CSV)",
            data=csv_data,
            file_name="hasil_clustering_mitra_pulsa.csv",
            mime="text/csv"
        )


if __name__ == '__main__':
    main()
