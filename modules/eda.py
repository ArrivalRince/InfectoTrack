import streamlit as st
import pandas as pd
import plotly.express as px
import os

def show():

    st.header("📊 EDA Data Mentah (Tanpa Cleaning)")

    # ================================
    # UPLOAD DATASET
    # ================================
    st.subheader("📤 Upload Dataset")
    st.write("Silakan upload dataset baru Anda dalam format CSV. Dataset ini akan digunakan di seluruh sistem (EDA, Preprocessing, dll).")
    
    base_path = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_path, "data", "dataset.csv")
    
    uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])
    if uploaded_file is not None:
        # Simpan file yang di-upload ke dataset.csv (agar tersinkron dengan halaman lain)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ Dataset berhasil di-upload dan disimpan sebagai dataset sistem.")
        st.cache_data.clear()  # Bersihkan cache agar data loader mengambil data terbaru

    # ================================
    # LOAD DATA
    # ================================
    if not os.path.exists(file_path):
        # Coba fallback ke file default jika belum ada dataset.csv
        file_path_default = os.path.join(base_path, "data", "Disease by Province and Type of Disease, 2025.csv")
        if os.path.exists(file_path_default):
            df = pd.read_csv(file_path_default)
            df.to_csv(file_path, index=False) # jadikan dataset utama
        else:
            st.warning("⚠️ Belum ada dataset yang di-upload. Silakan upload dataset CSV terlebih dahulu.")
            return

    df = pd.read_csv(file_path)

    # ================================
    # DATA RAW
    # ================================
    st.subheader("📌 Data Mentah (Raw)")
    st.dataframe(df)

    # ================================
    # INFORMASI DATASET
    # ================================
    st.subheader("📌 Informasi Dataset")

    st.write("Jumlah baris:", df.shape[0])
    st.write("Jumlah kolom:", df.shape[1])

    st.write("Tipe data:")
    st.write(df.dtypes)

    # ================================
    # DETEKSI MISSING VALUE
    # ================================
    st.subheader("📌 Deteksi Missing Value")

    missing_real = df.isna().sum()

    missing_symbol = (
        (df == "–").sum() +
        (df == "-").sum()
    )

    missing_total = missing_real + missing_symbol

    fig_missing = px.bar(
        x=missing_total.index,
        y=missing_total.values,
        labels={
            "x": "Kolom",
            "y": "Jumlah Missing"
        },
        template="plotly_dark"
    )

    st.plotly_chart(fig_missing, use_container_width=True)

    st.info(
        "Missing mencakup NaN, None, simbol '–', dan '-'."
    )

    # ================================
    # RINGKASAN OUTLIER KESELURUHAN
    # ================================
    st.subheader("📌 Ringkasan Outlier Keseluruhan Data")
    st.write("Tabel di bawah ini menunjukkan jumlah outlier yang terdeteksi pada setiap kolom numerik berdasarkan perhitungan batas atas dan batas bawah IQR (*Interquartile Range*).")
    
    outlier_counts = []
    for col in df.columns:
        # Abaikan kolom string/label
        if col not in ['Provinsi', 'Cluster', 'Unnamed: 0', 'index', 'id', 'ID']:
            temp_num = pd.to_numeric(df[col], errors='coerce')
            if not temp_num.isna().all():
                Q1 = temp_num.quantile(0.25)
                Q3 = temp_num.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                num_outliers = ((temp_num < lower_bound) | (temp_num > upper_bound)).sum()
                outlier_counts.append({"Kolom (Indikator)": col, "Jumlah Outlier": num_outliers})
                
    if outlier_counts:
        df_outliers_summary = pd.DataFrame(outlier_counts)
        st.dataframe(df_outliers_summary, use_container_width=True)
        total_outliers = df_outliers_summary["Jumlah Outlier"].sum()
        if total_outliers > 0:
            st.info(f"Terdapat total **{total_outliers}** nilai outlier di seluruh dataset.")
        else:
            st.success("Tidak ada nilai outlier yang terdeteksi di seluruh kolom numerik.")
    else:
        st.warning("Tidak ada kolom numerik yang valid untuk dianalisis outlier-nya.")

    # ================================
    # PILIH KOLOM
    # ================================
    st.subheader("📌 Visualisasi Data")

    selected_col = st.selectbox(
        "Pilih Kolom",
        df.columns
    )

    # ================================
    # KONVERSI SEMENTARA
    # ================================
    numeric_data = pd.to_numeric(
        df[selected_col],
        errors='coerce'
    )

    # ================================
    # HISTOGRAM
    # ================================
    st.subheader("📊 Histogram Distribusi Data")

    try:

        fig_hist = px.histogram(
            x=numeric_data,
            nbins=20,
            template="plotly_dark",
            labels={
                "x": selected_col,
                "y": "Jumlah Data"
            }
        )

        st.plotly_chart(
            fig_hist,
            use_container_width=True
        )

    except:
        st.error("Kolom tidak dapat divisualisasikan.")

    # ================================
    # DETEKSI OUTLIER
    # ================================
    st.subheader("🚨 Visualisasi Outlier")

    try:

        # IQR
        Q1 = numeric_data.quantile(0.25)
        Q3 = numeric_data.quantile(0.75)

        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Copy dataframe
        df_outlier = df.copy()

        df_outlier["value_numeric"] = numeric_data

        # Label outlier
        df_outlier["Kategori"] = df_outlier[
            "value_numeric"
        ].apply(
            lambda x:
            "Outlier"
            if pd.notnull(x)
            and (
                x < lower_bound
                or x > upper_bound
            )
            else "Normal"
        )

        # Scatter plot
        fig_scatter = px.scatter(
            df_outlier,
            x="Provinsi",
            y="value_numeric",
            color="Kategori",
            hover_data=[
                "Provinsi",
                "value_numeric"
            ],
            template="plotly_dark"
        )

        fig_scatter.update_layout(
            xaxis_title="Provinsi",
            yaxis_title=selected_col,
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig_scatter,
            use_container_width=True
        )

        # ================================
        # TABEL OUTLIER
        # ================================
        st.subheader("📌 Data Outlier")

        outlier_only = df_outlier[
            df_outlier["Kategori"] == "Outlier"
        ]

        if len(outlier_only) > 0:

            st.dataframe(
                outlier_only[
                    [
                        "Provinsi",
                        "value_numeric"
                    ]
                ].rename(
                    columns={
                        "value_numeric": selected_col
                    }
                )
            )

        else:
            st.success(
                "Tidak ditemukan outlier."
            )

    except:
        st.error(
            "Kolom tidak dapat dianalisis."
        )

    st.subheader("📌 Catatan")

    st.markdown("""
    ⚠️ Dataset masih dalam kondisi mentah

    """)