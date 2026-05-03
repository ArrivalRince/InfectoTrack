import streamlit as st

def show():
    st.header("📘 Metodologi")
    st.write("Penjelasan mengenai tahapan analitik yang digunakan dalam aplikasi ini.")

    st.markdown("""
    ### 1. Sumber Data
    Data yang digunakan adalah *dataset simulasi* yang merepresentasikan indikator penyakit menular dari 34 Provinsi di Indonesia (berdasarkan format BPS 2025). Terdapat 6 fitur utama: `TBC_CDR`, `TBC_SR`, `AIDS`, `Kusta`, `Malaria`, dan `DBD`.

    ### 2. Preprocessing
    Sebelum dimasukkan ke dalam model pembelajaran mesin (Machine Learning), data diseragamkan rentang nilainya menggunakan **StandardScaler**. Hal ini penting agar variabel dengan skala besar (seperti Kasus DBD) tidak mendominasi variabel dengan skala persentase (seperti TBC_CDR).

    ### 3. K-Means Clustering
    Algoritma K-Means digunakan untuk mengelompokkan data provinsi ke dalam 3 cluster tanpa perlu label sebelumnya (unsupervised learning).
    - **Cluster 0**: Tingkat risiko Rendah
    - **Cluster 1**: Tingkat risiko Sedang
    - **Cluster 2**: Tingkat risiko Tinggi
    
    *Catatan: Penamaan risiko (Rendah, Sedang, Tinggi) diinterpretasikan berdasarkan nilai rata-rata tiap kelompok yang dihasilkan.*

    ### 4. Dimensionality Reduction (PCA)
    Untuk dapat memvisualisasikan data dengan 6 variabel ke dalam grafik 2 Dimensi (Scatter Plot), digunakan metode **Principal Component Analysis (PCA)** pada halaman Clustering. PCA mereduksi 6 variabel tersebut menjadi 2 komponen utama (PCA1 dan PCA2) yang merangkum variansi data semaksimal mungkin.
    """)
