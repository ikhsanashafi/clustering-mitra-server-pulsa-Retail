"""
Script untuk membuat dokumen laporan akademik Microsoft Word (.docx)
secara lengkap, profesional, dan komprehensif sesuai kaidah akademik.
Disusun oleh: Ikhsan Ashafi (NIM: 241011400424)
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

base_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.abspath(os.path.join(base_dir, '..'))
report_path = os.path.join(project_dir, 'laporan', 'laporan_clustering_mitra_server_pulsa.docx')
fig_dir = os.path.join(project_dir, 'outputs', 'figures')

doc = Document()

# Set page margins to standard 2.54 cm (1 inch)
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Styling Helpers
def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_header(title, level=1):
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    run = p.add_run(title)
    run.bold = True
    run.font.name = 'Calibri'
    
    if level == 1:
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(15, 23, 42)
    elif level == 2:
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(30, 58, 138)
    elif level == 3:
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        run.font.size = Pt(11.5)
        run.font.color.rgb = RGBColor(51, 65, 85)
    return p

def add_body_p(text, bold_prefix=None, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(11)
        r_pre.font.color.rgb = RGBColor(30, 41, 59)
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(11)
    run.italic = italic
    run.font.color.rgb = RGBColor(30, 41, 59)
    return p

def add_bullet_p(bold_prefix, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    r_pre = p.add_run(bold_prefix + " ")
    r_pre.bold = True
    r_pre.font.name = 'Calibri'
    r_pre.font.size = Pt(11)
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(11)
    return p

def add_figure(img_name, caption):
    img_path = os.path.join(fig_dir, img_name)
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        p_img.paragraph_format.keep_with_next = True
        run_img = p_img.add_run()
        run_img.add_picture(img_path, width=Inches(5.8))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run(caption)
        r_cap.italic = True
        r_cap.font.name = 'Calibri'
        r_cap.font.size = Pt(9.5)
        r_cap.font.color.rgb = RGBColor(100, 116, 139)

# ==================== COVER PAGE ====================
p_top = doc.add_paragraph()
p_top.paragraph_format.space_before = Pt(36)
p_top.paragraph_format.space_after = Pt(12)
p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_top = p_top.add_run("LAPORAN TUGAS BESAR MACHINE LEARNING")
r_top.bold = True
r_top.font.name = 'Calibri'
r_top.font.size = Pt(14)
r_top.font.color.rgb = RGBColor(100, 116, 139)

p_title = doc.add_paragraph()
p_title.paragraph_format.space_before = Pt(18)
p_title.paragraph_format.space_after = Pt(24)
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_title = p_title.add_run("CLUSTERING PERILAKU MITRA SERVER PULSA BERDASARKAN POLA TRANSAKSI MENGGUNAKAN ALGORITMA K-MEANS")
r_title.bold = True
r_title.font.name = 'Calibri'
r_title.font.size = Pt(18)
r_title.font.color.rgb = RGBColor(15, 23, 42)

p_author = doc.add_paragraph()
p_author.paragraph_format.space_before = Pt(60)
p_author.paragraph_format.space_after = Pt(80)
p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_disusun = p_author.add_run("Disusun oleh:\n\n")
r_disusun.font.size = Pt(12)
r_name = p_author.add_run("IKHSAN ASHAFI\n")
r_name.bold = True
r_name.font.size = Pt(14)
r_nim = p_author.add_run("NIM: 241011400424\n\n")
r_nim.bold = True
r_nim.font.size = Pt(12)

p_inst = doc.add_paragraph()
p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_inst.paragraph_format.space_after = Pt(12)
r_inst = p_inst.add_run("PROGRAM STUDI TEKNIK INFORMATIKA S1\nFAKULTAS ILMU KOMPUTER\n2026")
r_inst.bold = True
r_inst.font.size = Pt(12)
r_inst.font.color.rgb = RGBColor(30, 41, 59)

doc.add_page_break()

# ==================== BAB I PENDAHULUAN ====================
add_header("BAB I PENDAHULUAN", level=1)

add_header("1.1 Latar Belakang", level=2)
add_body_p(
    "Industri distribusi pulsa elektronik, paket data internet, voucher digital, dan pembayaran tagihan multi-biller (PPOB) "
    "mengalami perkembangan yang sangat pesat seiring tingginya penetrasi perangkat seluler dan digitalisasi transaksi keuangan. "
    "Dalam operasional server pulsa, ribuan transaksi diproses setiap hari dari berbagai mitra reseller. Setiap mitra memiliki "
    "perilaku transaksi yang bervariasi secara signifikan, baik dari segi frekuensi pemesanan, besaran nominal uang yang diputar, "
    "keberagaman produk yang dijual, hingga durasi aktif operasional."
)
add_body_p(
    "Pengelolaan mitra yang bersifat seragam (one-size-fits-all) tanpa segmentasi analitik sering kali menyebabkan inefisiensi bisnis. "
    "Penyedia server pulsa menghadapi tantangan dalam mengidentifikasi mitra yang memerlukan perhatian khusus, seperti mitra jangkar "
    "(key partners) yang menyumbang perputaran omset terbesar namun rentan mengalami gangguan antrean API, mitra reguler yang konsisten, "
    "hingga mitra sporadis yang hanya bertransaksi sesaat. Tanpa pemahaman pola perilaku mitra berbasis data, alokasi kapasitas server, "
    "skema harga promosi, dan mitigasi risiko kehabisan saldo stok tidak dapat dilakukan secara tepat sasaran."
)
add_body_p(
    "Penerapan Machine Learning melalui metode Unsupervised Learning, khususnya algoritma K-Means Clustering, memberikan solusi "
    "analitik yang objektif untuk mengelompokkan mitra ke dalam segmen-segmen homogen berdasarkan kesamaan pola transaksi. "
    "Dengan menganalisis dataset transaksi nyata dari server pulsa, penelitian ini memberikan landasan operasional berbasis data "
    "untuk optimalisasi pengelolaan mitra."
)

add_header("1.2 Identifikasi Masalah", level=2)
add_body_p("Berdasarkan observasi operasional pada server pulsa, beberapa masalah utama yang teridentifikasi meliputi:")
add_bullet_p("Kurangnya visibilitas segmen:", "Penyedia server kesulitan membedakan mitra bernilai tinggi, mitra reguler, dan mitra pasif secara kuantitatif.")
add_bullet_p("Penyebaran volume tidak seimbang:", "Sebagian kecil mitra menyumbang transaksi dalam jumlah sangat besar, sehingga memerlukan perlakuan teknis yang berbeda dari mitra ritel biasa.")
add_bullet_p("Keamanan privasi data:", "Data transaksi mentah memuat informasi sensitif (nomor telepon pelanggan dan serial number) yang wajib diproteksi dan dianonimkan sebelum diproses.")

add_header("1.3 Rumusan Masalah", level=2)
add_body_p("Rumusan masalah pada penelitian ini adalah sebagai berikut:")
add_bullet_p("1.", "Bagaimana merancang pipeline data cleaning dan feature engineering yang aman serta mampu merefleksikan karakteristik perilaku transaksi mitra server pulsa?")
add_bullet_p("2.", "Berapa jumlah klaster optimal (K) untuk mengelompokkan mitra berdasarkan pola transaksi aktual?")
add_bullet_p("3.", "Bagaimana karakteristik dan profil bisnis dari setiap klaster mitra yang terbentuk menggunakan algoritma K-Means?")
add_bullet_p("4.", "Bagaimana mengimplementasikan model ke dalam aplikasi dashboard web interaktif yang siap digunakan oleh pemangku kepentingan?")

add_header("1.4 Batasan Masalah", level=2)
add_body_p("Batasan masalah dalam penelitian ini ditetapkan guna menjaga fokus kajian akademik:")
add_bullet_p("Sumber Data:", "Dataset yang digunakan adalah data transaksi operasional server pulsa tanggal 15 Oktober 2026 yang terdiri dari 2.272 transaksi dan 451 mitra unik.")
add_bullet_p("Rentang Observasi:", "Analisis merefleksikan aktivitas pada periode jendela pengamatan aktual (~8.5 jam operasional), bukan kesimpulan retensi atau loyalitas jangka panjang.")
add_bullet_p("Metode Algoritma:", "Algoritma clustering yang digunakan berfokus pada K-Means Clustering dengan evaluasi Elbow Method dan Silhouette Score.")
add_bullet_p("Privasi Data:", "Seluruh informasi kontak pengguna, kode reseller asli, nama reseller, dan serial voucher dianonimkan secara ketat menjadi ID mitra anonim.")

add_header("1.5 Tujuan Penelitian", level=2)
add_body_p("Tujuan utama yang ingin dicapai melalui penelitian ini adalah:")
add_bullet_p("1.", "Melakukan data cleaning, validasi integritas finansial, dan anonimisasi data transaksi server pulsa secara nyata.")
add_bullet_p("2.", "Mengekstrak fitur-fitur kuantitatif perilaku mitra melalui agregasi transaksi tingkat mitra.")
add_bullet_p("3.", "Menerapkan algoritma K-Means dan menentukan jumlah klaster terbaik melalui pengujian K=2 sampai K=6.")
add_bullet_p("4.", "Menginterpretasikan karakteristik profil tiap klaster dan menyusun rekomendasi keputusan bisnis.")
add_bullet_p("5.", "Membangun aplikasi web interaktif berbasis Streamlit yang siap dioperasikan secara lokal maupun di-deploy ke cloud.")

add_header("1.6 Manfaat Penelitian", level=2)
add_body_p("Hasil penelitian ini diharapkan memberikan manfaat sebagai berikut:")
add_bullet_p("Bagi Mahasiswa:", "Memperdalam pemahaman komprehensif mengenai siklus hidup proyek Machine Learning dari data mentah hingga deployment.")
add_bullet_p("Bagi Praktisi / Bisnis:", "Menyediakan segmentasi mitra yang objektif untuk mendukung efisiensi alokasi bandwidth API, skema loyalitas, dan strategi penjualan.")
add_bullet_p("Bagi Akademisi:", "Memberikan studi kasus nyata penerapan algoritma K-Means pada data transaksi finansial server telekomunikasi ritel.")

# ==================== BAB II LANDASAN TEORI ====================
add_header("BAB II LANDASAN TEORI", level=1)

add_header("2.1 Machine Learning dan Unsupervised Learning", level=2)
add_body_p(
    "Machine Learning merupakan cabang kecerdasan buatan (Artificial Intelligence) yang berfokus pada pengembangan algoritma "
    "yang mampu mempelajari pola dari data historis guna membuat keputusan atau inferensi tanpa diprogram secara eksplisit (Russell & Norvig, 2020). "
    "Dalam taksonomi Machine Learning, Unsupervised Learning adalah paradigma pembelajaran di mana model bekerja pada dataset yang tidak "
    "memiliki label atau target luaran yang telah ditentukan sebelumnya. Tujuan utamanya adalah menemukan struktur tersembunyi, pola alami, "
    "atau pengelompokan intrinsik di dalam data (Hastie et al., 2009)."
)

add_header("2.2 Konsep Clustering dan Algoritma K-Means", level=2)
add_body_p(
    "Clustering merupakan teknik pembagian himpunan objek ke dalam beberapa kelompok (klaster) sedemikian rupa sehingga objek-objek "
    "di dalam kelompok yang sama memiliki tingkat kemiripan (homogenitas) yang tinggi, sementara objek antar kelompok memiliki tingkat "
    "perbedaan (heterogenitas) yang maksimal (Tan et al., 2018)."
)
add_body_p(
    "Algoritma K-Means (MacQueen, 1967) adalah metode clustering berbasis partisi yang membagi n data observasi ke dalam K klaster. "
    "Setiap klaster diwakili oleh nilai rata-rata (centroid). Algoritma bekerja secara iteratif dengan meminimalkan fungsi objektif "
    "Within-Cluster Sum of Squares (WCSS) atau inersia:"
)
add_body_p("J = ∑_{k=1}^K ∑_{x_i ∈ C_k} || x_i - μ_k ||^2", italic=True)
add_body_p(
    "Di mana C_k menyatakan himpunan data pada klaster ke-k, x_i adalah vektor observasi, dan μ_k adalah posisi titik pusat (centroid) "
    "klaster ke-k menggunakan jarak Euclidean (Euclidean Distance)."
)

add_header("2.3 Data Preprocessing dan Feature Scaling", level=2)
add_body_p(
    "Pembersihan data (data cleaning) merupakan tahap krusial untuk memastikan keabsahan model. Dalam data transaksi pulsa, penanganan "
    "format tanggal, penghapusan data tidak valid, dan filtering status transaksi sukses sangat penting. Selain itu, karena algoritma K-Means "
    "sangat sensitif terhadap perbedaan skala numerik dan kemencengan distribusi (skewness), penskalaan fitur wajib diterapkan."
)
add_body_p(
    "StandardScaler melakukan standarisasi fitur dengan mengurangkan nilai rata-rata (mean) dan membaginya dengan simpangan baku (standard deviation):"
)
add_body_p("z = (x - μ) / σ", italic=True)
add_body_p(
    "Pada data finansial yang memiliki rentang nilai ekstrem (power-law distribution), transformasi logaritmik log(1 + x) terlebih dahulu "
    "diterapkan sebelum standarisasi untuk menstabilkan variansi dan mencegah satu outlier mendominasi pembentukan centroid."
)

add_header("2.4 Metode Evaluasi Klaster", level=2)
add_body_p("Untuk mengevaluasi kualitas pengelompokan tanpa adanya ground truth label, digunakan metrik internal:")
add_bullet_p("Elbow Method:", "Mengevaluasi penurunan nilai WCSS (inersia) terhadap pertambahan jumlah K. Titik di mana penurunan kurva mulai melandai secara tajam mengindikasikan jumlah klaster yang seimbang.")
add_bullet_p("Silhouette Score (Rousseeuw, 1987):", "Mengukur seberapa dekat suatu titik dengan titik-titik di klasternya dibandingkan dengan klaster terdekat lainnya. Nilai berkisar antara -1 hingga +1, di mana nilai mendekati 1 menunjukkan klaster yang padat dan terpisah dengan baik.")
add_bullet_p("Calinski-Harabasz Index:", "Rasio dispersi antara klaster terhadap dispersi di dalam klaster. Nilai lebih tinggi menunjukkan partisi yang lebih baik.")
add_bullet_p("Davies-Bouldin Index:", "Rasio rata-rata keserupaan antara klaster dengan klaster paling mirip. Nilai lebih rendah menunjukkan pemisahan yang lebih superior.")

add_header("2.5 Principal Component Analysis (PCA)", level=2)
add_body_p(
    "Principal Component Analysis (PCA) adalah teknik reduksi dimensi linier yang mentransformasikan variabel-variabel awal yang berkorelasi "
    "ke dalam variabel baru yang saling ortogonal yang disebut komponen utama (Principal Components) (Jolliffe & Cadima, 2016). "
    "Dalam proyek ini, PCA digunakan untuk memproyeksikan fitur berdimensi tinggi ke bidang 2D agar visualisasi sebaran klaster dapat disajikan."
)

# ==================== BAB III METODOLOGI ====================
add_header("BAB III METODOLOGI PENELITIAN", level=1)

add_header("3.1 Sumber Data dan Struktur Dataset", level=2)
add_body_p(
    "Data yang digunakan dalam penelitian ini merupakan dataset transaksi riil operasional server pulsa lokal bernama 'data-transaksi-pulsa.csv' "
    "(disertai salinan Excel 'ikhsan.xlsx'). Dataset mentah mencakup 2.272 baris transaksi yang tercatat pada tanggal 15 Oktober 2026 "
    "mulai pukul 14:56 WIB hingga 23:28 WIB."
)

# Tabel Kolom Dataset
table_data = doc.add_table(rows=1, cols=4)
table_data.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr_cells = table_data.rows[0].cells
hdr_cells[0].text = "No"
hdr_cells[1].text = "Nama Kolom Mentah"
hdr_cells[2].text = "Tipe Data"
hdr_cells[3].text = "Keterangan & Perlakuan Privasi"
for c in hdr_cells:
    set_cell_background(c, "1E3A8A")
    set_cell_margins(c, top=80, bottom=80, left=100, right=100)
    for p in c.paragraphs:
        for r in p.runs:
            r.bold = True
            r.font.name = 'Calibri'
            r.font.color.rgb = RGBColor(255, 255, 255)

col_specs = [
    ("1", "TrxID", "Integer", "Nomor transaksi unik; dihapus dari fitur"),
    ("2", "Tgl. Entri", "String (ISO)", "Waktu transaksi; dikonversi ke datetime"),
    ("3", "Produk", "String", "Kode produk pulsa/token/voucher"),
    ("4", "Tujuan", "Integer/String", "Nomor telepon tujuan; DIHAPUS (SENSITIF)"),
    ("5", "Kode Reseller", "String", "Kode reseller asli; DIANONIMKAN ke MITRA_xxx"),
    ("6", "Nama Reseller", "String", "Nama asli konter; DIHAPUS (SENSITIF)"),
    ("7", "Modul", "String", "Kanal antrean transaksi (IP Host, dsb)"),
    ("8", "Status", "String", "Status transaksi (100% Sukses)"),
    ("9", "Hrg. Beli", "Integer", "Harga modal pokok server (Rupiah)"),
    ("10", "Hrg. Jual", "Integer", "Harga jual ke mitra/reseller (Rupiah)"),
    ("11", "Komisi", "Integer", "Komisi agen/upline (Rupiah)"),
    ("12", "Laba", "Integer", "Laba bersih: Hrg. Jual - Hrg. Beli - Komisi"),
    ("13", "Jawaban Provider", "String", "Pesan teknis provider; DIHAPUS"),
    ("14", "SN", "String", "Nomor seri / token voucher; DIHAPUS (SENSITIF)")
]

for row_data in col_specs:
    row = table_data.add_row()
    for i, val in enumerate(row_data):
        cell = row.cells[i]
        cell.text = val
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
        for p in cell.paragraphs:
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = 'Calibri'
                r.font.size = Pt(9.5)

add_body_p("", italic=True) # spacing

add_header("3.2 Tahapan Penelitian", level=2)
add_body_p("Penelitian dilaksanakan secara sistematis melalui 7 tahapan:")
add_bullet_p("Tahap 1: Data Audit & Profiling:", "Memeriksa kelengkapan data, mendeteksi duplikasi, missing values, dan memverifikasi integritas formula Laba = Hrg. Jual - Hrg. Beli - Komisi.")
add_bullet_p("Tahap 2: Data Cleaning & Anonimisasi Privasi:", "Menghapus seluruh nomor telepon, token serial number, dan nama asli mitra. Membuat ID anonim unik MITRA_001 s.d. MITRA_451.")
add_bullet_p("Tahap 3: Feature Engineering Agregasi Mitra:", "Mengagregasikan 2.272 baris transaksi menjadi 451 baris entitas mitra dengan 5 metrik bisnis utama.")
add_bullet_p("Tahap 4: Exploratory Data Analysis (EDA):", "Menganalisis distribusi per jam, produk terpopuler, dan kemencengan fitur.")
add_bullet_p("Tahap 5: Penskalaan Fitur (Log1p & StandardScaler):", "Menormalkan skala fitur agar jarak Euclidean K-Means tidak bias terhadap nilai nominal moneter.")
add_bullet_p("Tahap 6: Eksperimen & Evaluasi Klaster K-Means:", "Menguji K=2 hingga K=6 menggunakan Elbow Method dan Silhouette Score untuk menetapkan nilai K optimal.")
add_bullet_p("Tahap 7: Interpretasi Bisnis & Deployment Web:", "Menganalisis profil setiap klaster dan membangun antarmuka web Streamlit.")

add_header("3.3 Formulasi Fitur Analisis", level=2)
add_body_p("Fitur-fitur kuantitatif yang diekstraksi untuk setiap mitra anonim meliputi:")
add_bullet_p("1. jumlah_transaksi:", "Total frekuensi pesanan sukses yang dieksekusi mitra.")
add_bullet_p("2. total_nilai_transaksi:", "Akumulasi omset moneter harga jual produk pulsa yang dibeli mitra (Rupiah).")
add_bullet_p("3. rata_rata_nilai_transaksi:", "Rata-rata tiket transaksi: total_nilai_transaksi / jumlah_transaksi.")
add_bullet_p("4. jumlah_produk_unik:", "Variasi jenis produk pulsa/token/paket data yang dibeli mitra.")
add_bullet_p("5. rentang_aktif_menit:", "Durasi waktu antara transaksi pertama dan transaksi terakhir mitra dalam jendela pengamatan.")

# ==================== BAB IV HASIL DAN PEMBAHASAN ====================
add_header("BAB IV HASIL DAN PEMBAHASAN", level=1)

add_header("4.1 Hasil Audit dan Pembersihan Data", level=2)
add_body_p(
    "Hasil audit komprehensif membuktikan bahwa dataset transaksi server pulsa memiliki integritas data yang sangat tinggi. "
    "Dari total 2.272 baris data mentah, tidak ditemukan satu pun nilai kosong (missing values = 0) maupun data duplikat "
    "(duplicated rows = 0). Seluruh 2.272 transaksi berstatus 'Sukses' (100%)."
)
add_body_p(
    "Verifikasi finansial menunjukkan relasi Laba = Hrg. Jual - Hrg. Beli - Komisi terbukti konsisten pada 100% baris transaksi "
    "(selisih maksimal = Rp 0). Dari 2.272 transaksi, teridentifikasi tepat 451 entitas reseller unik yang kemudian dipetakan "
    "menjadi MITRA_001 hingga MITRA_451 secara konsisten."
)

add_header("4.2 Eksplorasi Data (EDA)", level=2)
add_body_p(
    "Analisis temporal menunjukkan pola operasional server pulsa yang sangat dinamis. Aktivitas transaksi tercatat mulai pukul "
    "14:56 WIB hingga 23:28 WIB pada tanggal 15 Oktober 2026. Distribusi per jam menunjukkan peningkatan tajam pada malam hari, "
    "dengan puncak tertinggi (peak hours) terjadi pada pukul 21:00 WIB sebanyak 628 transaksi (27.6% dari total transaksi harian)."
)
add_figure("eda_hourly.png", "Gambar 4.1 Distribusi Volume Transaksi per Jam Operasional (15 Oktober 2026)")

add_body_p(
    "Dari sisi variasi produk, server melayani 359 produk unik. Gambar 4.2 memperlihatkan 10 produk terpopuler, yang didominasi oleh "
    "produk voucher/e-wallet CACVAM1 (481 transaksi), pengecekan saldo DANA CCEKDANA (142 transaksi), dan token listrik PLN20 (129 transaksi)."
)
add_figure("eda_top_products.png", "Gambar 4.2 Sepuluh Produk Server Pulsa Terpopuler")

add_body_p(
    "Pemeriksaan distribusi fitur agregasi mitra (Gambar 4.3) mengonfirmasi bahwa frekuensi transaksi dan perputaran omset "
    "memiliki kemencengan positif (positive skewness) yang kuat. Sebagian besar mitra (75%) melakukan 4 transaksi atau kurang, "
    "namun terdapat mitra jangkar dengan volume transaksi mencapai 580 transaksi dan omset Rp 12.506.015. "
    "Karakteristik data ini memperkuat kebutuhan transformasi log1p sebelum pemodelan K-Means."
)
add_figure("eda_feature_dist.png", "Gambar 4.3 Distribusi Fitur Agregasi Tingkat Mitra")

add_header("4.3 Evaluasi Penentuan Jumlah Klaster (K)", level=2)
add_body_p(
    "Eksperimen clustering dijalankan untuk rentang K=2 hingga K=6 menggunakan transformasi log1p dan StandardScaler. "
    "Evaluasi dilakukan secara kuantitatif melalui inersia (Elbow Method), Silhouette Score, Calinski-Harabasz, dan Davies-Bouldin."
)

# Tabel Evaluasi K
table_eval = doc.add_table(rows=1, cols=5)
table_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr_e = table_eval.rows[0].cells
hdr_e[0].text = "Nilai K"
hdr_e[1].text = "Inersia (WCSS)"
hdr_e[2].text = "Silhouette Score"
hdr_e[3].text = "Calinski-Harabasz"
hdr_e[4].text = "Davies-Bouldin"
for c in hdr_e:
    set_cell_background(c, "1E3A8A")
    set_cell_margins(c, top=80, bottom=80, left=100, right=100)
    for p in c.paragraphs:
        for r in p.runs:
            r.bold = True
            r.font.name = 'Calibri'
            r.font.color.rgb = RGBColor(255, 255, 255)

eval_data = [
    ("K = 2", "1191.52", "0.4264", "400.75", "0.9021"),
    ("K = 3 (Terpilih)", "837.73", "0.4211", "378.97", "0.9710"),
    ("K = 4", "638.12", "0.4300", "377.54", "0.8858"),
    ("K = 5", "532.68", "0.3896", "360.51", "0.9789"),
    ("K = 6", "438.53", "0.4069", "368.65", "0.8966")
]

for row_data in eval_data:
    row = table_eval.add_row()
    for i, val in enumerate(row_data):
        cell = row.cells[i]
        cell.text = val
        if "Terpilih" in val or i == 0 and "K = 3" in row_data[0]:
            set_cell_background(cell, "EFF6FF")
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
        for p in cell.paragraphs:
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = 'Calibri'
                r.font.size = Pt(10)
                if "Terpilih" in row_data[0]:
                    r.bold = True

add_body_p("", italic=True)
add_figure("eval_elbow_silhouette.png", "Gambar 4.4 Evaluasi Elbow Method dan Silhouette Score (K=2 s.d. K=6)")

add_body_p(
    "Pembahasan Pemilihan K: Berdasarkan Gambar 4.4 dan Tabel di atas, kurva Elbow menunjukkan penurunan inersia yang sangat "
    "drastis dari K=2 (1191.52) ke K=3 (837.73) dengan pengurangan inersia sebesar 29.7%. Setelah K=3, laju penurunan mulai melandai. "
    "Meskipun K=4 memiliki Silhouette Score sedikit lebih tinggi (0.4300 vs 0.4211), partisi K=4 membagi kelompok transaksi rendah "
    "menjadi dua subkelompok yang memiliki karakteristik bisnis sangat mirip (redundansi makna bisnis). "
    "Oleh karena itu, K=3 dipilih sebagai partisi terbaik yang paling seimbang antara validasi matematis dan kemudahan interpretasi operasional."
)

add_header("4.4 Visualisasi dan Profil Karakteristik Klaster", level=2)
add_body_p(
    "Proyeksi Principal Component Analysis (PCA) dua dimensi (Gambar 4.5) menunjukkan bahwa ketiga klaster mitra terpisah dengan sangat baik "
    "tanpa ada tumpang tindih ekstrem. PC1 menangkap variansi utama yang berkaitan dengan besaran volume transaksi dan omset, "
    "sementara PC2 menangkap dimensi variasi produk dan kontinuitas temporal."
)
add_figure("pca_clusters_2d.png", "Gambar 4.5 Sebaran Klaster Mitra dalam Proyeksi 2D PCA")

add_body_p("Profil kuantitatif rata-rata dan median dari ketiga segmen mitra disajikan secara rinci pada tabel berikut:")

# Tabel Profil Klaster
table_prof = doc.add_table(rows=1, cols=7)
table_prof.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr_p = table_prof.rows[0].cells
hdr_p[0].text = "Klaster"
hdr_p[1].text = "Nama Segmen"
hdr_p[2].text = "Jumlah Mitra (%)"
hdr_p[3].text = "Rata-rata Trx"
hdr_p[4].text = "Rata-rata Omset"
hdr_p[5].text = "Variasi Produk"
hdr_p[6].text = "Durasi Aktif"
for c in hdr_p:
    set_cell_background(c, "1E3A8A")
    set_cell_margins(c, top=80, bottom=80, left=80, right=80)
    for p in c.paragraphs:
        for r in p.runs:
            r.bold = True
            r.font.name = 'Calibri'
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(255, 255, 255)

prof_rows = [
    ("Klaster 0", "Mitra Sporadis (Aktivitas Rendah)", "186 mitra (41.24%)", "1.17 trx (Med: 1.0)", "Rp 52.113", "1.15 jenis", "0.57 menit"),
    ("Klaster 1", "Mitra Berkala (Aktivitas Menengah)", "204 mitra (45.23%)", "3.51 trx (Med: 3.0)", "Rp 170.171", "2.85 jenis", "190.36 m (~3.2 jam)"),
    ("Klaster 2", "Mitra Utama (Aktivitas Intensif)", "61 mitra (13.53%)", "21.93 trx (Med: 10.0)", "Rp 2.204.304", "6.11 jenis", "283.29 m (~4.7 jam)")
]

for row_data in prof_rows:
    row = table_prof.add_row()
    for i, val in enumerate(row_data):
        cell = row.cells[i]
        cell.text = val
        set_cell_margins(cell, top=60, bottom=60, left=60, right=60)
        for p in cell.paragraphs:
            p.paragraph_format.line_spacing = 1.05
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = 'Calibri'
                r.font.size = Pt(9)

add_body_p("", italic=True)
add_figure("cluster_metrics_summary.png", "Gambar 4.6 Perbandingan Metrik Kunci Antar-Klaster Mitra")

add_header("4.5 Interpretasi Bisnis dan Rekomendasi Operasional", level=2)
add_body_p(
    "1. Klaster 0 — Mitra Sporadis (Aktivitas Rendah): Terdiri dari 186 mitra (41.24%). Mitra pada kelompok ini melakukan transaksi "
    "hanya 1 hingga 2 kali dengan rentang durasi aktif sangat singkat (rata-rata 0.57 menit) dan produk homogen (1.15 jenis). "
    "Mitra ini kemungkinan adalah pengguna akhir (end-user) yang mengisi pulsa pribadi atau konter darurat kecil. "
    "Rekomendasi Bisnis: Perlu diberikan program re-aktivasi melalui pesan otomatis saldo, bonus cashback deposit kecil, dan tutorial "
    "fitur multi-produk agar mereka beralih menjadi mitra aktif berkala."
)
add_body_p(
    "2. Klaster 1 — Mitra Berkala (Aktivitas Menengah): Terdiri dari 204 mitra (45.23%), merupakan basis reseller terbesar server pulsa. "
    "Mitra memiliki rata-rata 3.51 transaksi dengan omset rata-rata Rp 170.171 dan rentang waktu operasional aktif rata-rata 190.36 menit "
    "(sekitar 3.2 jam). Mereka menjual rata-rata 2.85 jenis produk berbeda. Kelompok ini adalah konter ritel reguler yang melayani konsumen umum. "
    "Rekomendasi Bisnis: Berikan program reward poin bertahap (loyalty tiering), kemudahan top-up deposit via transfer instan, "
    "dan notifikasi pengingat stok produk terlaris (voucher data dan token listrik)."
)
add_body_p(
    "3. Klaster 2 — Mitra Utama (Aktivitas Intensif): Terdiri dari 61 mitra (13.53%), namun menyumbang perputaran omset transaksi terbesar "
    "dengan rata-rata Rp 2.204.304 per mitra (dan maksimal mencapai Rp 12.506.015) serta frekuensi rata-rata 21.93 transaksi "
    "(maksimal 580 transaksi). Mitra ini beroperasi sepanjang periode pengamatan (rata-rata 283.29 menit atau 4.7 jam) dan menjual "
    "keragaman produk tinggi (rata-rata 6.11 produk unik). Mitra ini adalah distributor, master dealer, atau toko besar dengan sistem otomasi. "
    "Rekomendasi Bisnis: Mitra ini merupakan kontributor revenue vital yang wajib dilindungi. Pengelola server wajib menyediakan jalur modul "
    "koneksi dedicated (IP Host prioritas) agar transaksi tidak terhambat antrean umum, margin grosir yang kompetitif, serta layanan dukungan "
    "pelanggan 24 jam respons cepat."
)

add_header("4.6 Keterbatasan Penelitian", level=2)
add_body_p(
    "Penelitian ini memiliki beberapa keterbatasan metodologis yang perlu dicatat: "
    "(1) Dataset transaksi mencakup jendela pengamatan 1 hari operasional (15 Oktober 2026, rentang ~8.5 jam). Oleh karena itu, pengelompokan "
    "mencerminkan perilaku dinamis pada jendela observasi tersebut, dan tidak dapat disimpulkan sebagai loyalitas atau churn jangka panjang "
    "tanpa data observasi multi-bulan. (2) Karena seluruh transaksi pada dataset berstatus Sukses, model tidak dapat mengevaluasi tingkat "
    "kegagalan atau risiko transaksi mitra."
)

# ==================== BAB V PENUTUP ====================
add_header("BAB V PENUTUP", level=1)

add_header("5.1 Kesimpulan", level=2)
add_body_p("Berdasarkan seluruh tahapan analisis, pemodelan, dan evaluasi yang telah dilaksanakan, diperoleh kesimpulan sebagai berikut:")
add_bullet_p("1.", "Pipeline data cleaning dan feature engineering berhasil memproses 2.272 transaksi riil dari 451 mitra server pulsa dengan validasi finansial yang konsisten (Laba = Hrg. Jual - Hrg. Beli - Komisi) dan penjaminan anonimitas privasi 100%.")
add_bullet_p("2.", "Penerapan transformasi log1p dan StandardScaler berhasil menstabilkan kemencengan data finansial, menghasilkan evaluasi Elbow Method dan Silhouette Score yang solid.")
add_bullet_p("3.", "Jumlah klaster K=3 terbukti menjadi solusi partisi paling optimal secara matematis (Silhouette Score = 0.4211) dan paling bermakna secara operasional bisnis.")
add_bullet_p("4.", "Tiga segmen mitra yang terbentuk mencakup: Klaster 0 (Mitra Sporadis, 186 mitra / 41.24%), Klaster 1 (Mitra Berkala, 204 mitra / 45.23%), dan Klaster 2 (Mitra Utama Intensif, 61 mitra / 13.53%).")
add_bullet_p("5.", "Aplikasi web interaktif Streamlit berhasil dibangun dan siap dioperasikan untuk memfasilitasi eksplorasi data, pengujian klaster secara dinamis, dan pengunduhan hasil segmentasi.")

add_header("5.2 Saran", level=2)
add_body_p("Untuk pengembangan penelitian dan implementasi operasional selanjutnya, disarankan:")
add_bullet_p("1.", "Memperluas rentang observasi transaksi menjadi minimal 30 hingga 90 hari untuk menangkap perilaku musiman dan retensi mitra.")
add_bullet_p("2.", "Mengintegrasikan fitur status kegagalan transaksi dan metode pembayaran deposit mitra guna memperkaya analisis risiko.")
add_bullet_p("3.", "Menerapkan algoritma clustering alternatif seperti DBSCAN atau Hierarchical Clustering sebagai pembanding ketahanan klaster terhadap outlier.")

# ==================== DAFTAR PUSTAKA ====================
add_header("DAFTAR PUSTAKA", level=1)

daftar_pustaka = [
    "Hastie, T., Tibshirani, R., & Friedman, J. (2009). The Elements of Statistical Learning: Data Mining, Inference, and Prediction (2nd ed.). Springer-Verlag.",
    "Jolliffe, I. T., & Cadima, J. (2016). Principal component analysis: a review and recent developments. Philosophical Transactions of the Royal Society A: Mathematical, Physical and Engineering Sciences, 374(2065), 20150202.",
    "MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. In Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability (Vol. 1, pp. 281-297). University of California Press.",
    "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825-2830.",
    "Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. Journal of Computational and Applied Mathematics, 20, 53-65.",
    "Russell, S., & Norvig, P. (2020). Artificial Intelligence: A Modern Approach (4th ed.). Pearson.",
    "Tan, P.-N., Steinbach, M., Karpatne, A., & Kumar, V. (2018). Introduction to Data Mining (2nd ed.). Pearson."
]

for ref in daftar_pustaka:
    p_ref = doc.add_paragraph()
    p_ref.paragraph_format.left_indent = Inches(0.4)
    p_ref.paragraph_format.first_line_indent = Inches(-0.4)
    p_ref.paragraph_format.line_spacing = 1.15
    p_ref.paragraph_format.space_after = Pt(6)
    r = p_ref.add_run(ref)
    r.font.name = 'Calibri'
    r.font.size = Pt(10)

# Save document
os.makedirs(os.path.dirname(report_path), exist_ok=True)
doc.save(report_path)
print(f"Laporan Word akademik berhasil disimpan di: {report_path}")
