import streamlit as st
import pandas as pd
import plotly.express as px
import os

def show():

    st.header("📊 EDA Data Mentah (Tanpa Cleaning)")

    # ================================
    # LOAD DATA
    # ================================
    base_path = os.path.dirname(os.path.dirname(__file__))

    file_path = os.path.join(
        base_path,
        "data",
        "Disease by Province and Type of Disease, 2025.csv"
    )

    if not os.path.exists(file_path):
        st.error("File tidak ditemukan! Pastikan ada di folder /data")
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