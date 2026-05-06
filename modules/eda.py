import streamlit as st
import plotly.express as px
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from utils.data_loader import load_data

def show():
    st.header("📊 Exploratory Data Analysis (EDA)")


    # LOAD DATA

    df = load_data()

    df = df.rename(columns={
        "TBC Case Detection Rate": "TBC_CDR",
        "TBC Success Rate": "TBC_SR",
        "Jumlah Kasus Penyakit - HIV/AIDS Kasus Baru": "AIDS",
        "New Case Detection Rate of Leprosy per 100,000 Population": "Kusta",
        "Annual Parasite Incidence per 1,000 Population": "Malaria",
        "DHF Incidence Rate per 100,000 Population": "DBD",
        "Cluster": "cluster"
    })

    features = ["TBC_CDR", "TBC_SR", "AIDS", "Kusta", "Malaria", "DBD"]


    # HISTOGRAM
    st.subheader("Histogram Distribusi")

    selected_feature = st.selectbox("Pilih Variabel", features)

    fig_hist = px.histogram(
        df,
        x=selected_feature,
        nbins=20,
        template="plotly_dark"
    )

    # ubah label axis
    fig_hist.update_layout(
        xaxis_title=f"Nilai {selected_feature}",
        yaxis_title="Jumlah Provinsi",
        bargap=0.1
    )

    st.plotly_chart(fig_hist, use_container_width=True)

    
    # BOXPLOT
    
    st.subheader("Boxplot (Sebelum vs Sesudah Normalisasi)")

    scaler = MinMaxScaler()
    df_scaled = df.copy()
    df_scaled[features] = scaler.fit_transform(df[features])

    col1, col2 = st.columns(2)

    with col1:
        fig_before = px.box(
            df,
            y=selected_feature,
            title="Before Scaling",
            template="plotly_dark"
        )
        st.plotly_chart(fig_before, use_container_width=True)

    with col2:
        fig_after = px.box(
            df_scaled,
            y=selected_feature,
            title="After MinMax Scaling",
            template="plotly_dark"
        )
        st.plotly_chart(fig_after, use_container_width=True)

    
    # HEATMAP
    
    st.subheader("Heatmap Korelasi")

    corr = df[features].corr()

    fig_corr = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        template="plotly_dark"
    )
    st.plotly_chart(fig_corr, use_container_width=True)


    # SCATTER

    st.subheader("Scatter Plot Antar Variabel")

    col1, col2 = st.columns(2)

    with col1:
        x_axis = st.selectbox("Sumbu X", features)

    with col2:
        y_axis = st.selectbox("Sumbu Y", features, index=1)

    fig_scatter = px.scatter(
        df,
        x=x_axis,
        y=y_axis,
        color=df["cluster"].astype(str),
        hover_name="Provinsi",
        template="plotly_dark"
    )

    fig_scatter.update_layout(
        xaxis_title=f"Nilai {x_axis}",
        yaxis_title=f"Nilai {y_axis}",
        legend_title="Cluster"
    )

    st.plotly_chart(fig_scatter, use_container_width=True)


    # DATA TABLE + SEARCH + HIGHLIGHT

    st.subheader("Dataset Lengkap")

    search = st.text_input("🔍 Cari Provinsi")

    def highlight_row(row):
        if search and search.lower() in row["Provinsi"].lower():
            return ["background-color: #ff4d4f; color: white; font-weight: bold"] * len(row)
        return [""] * len(row)

    styled_df = df.style.apply(highlight_row, axis=1)

    st.dataframe(styled_df, use_container_width=True)

    # Download CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download CSV",
        csv,
        "dataset_clustering.csv",
        "text/csv"
    )


    # RATA-RATA PER CLUSTER

    st.subheader("Rata-rata Tiap Cluster")

    cluster_mean = df.groupby("cluster")[features].mean().round(2)
    st.dataframe(cluster_mean, use_container_width=True)