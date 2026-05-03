import streamlit as st
import plotly.express as px
from utils.data_loader import load_data
from utils.helpers import get_cluster_label

def show():
    st.header("📊 Dashboard Persebaran Penyakit")
    st.write("Ringkasan distribusi provinsi berdasarkan risiko penyakit menular.")

    df = load_data()
    
    # Map label for better readability
    df['Tingkat Risiko'] = df['Cluster'].apply(get_cluster_label)

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Provinsi", len(df))
    col2.metric("Risiko Rendah", len(df[df['Cluster'] == 0]))
    col3.metric("Risiko Sedang", len(df[df['Cluster'] == 1]))
    col4.metric("Risiko Tinggi", len(df[df['Cluster'] == 2]))

    st.markdown("---")

    col_chart, col_table = st.columns([1, 1])

    with col_chart:
        st.subheader("Distribusi Cluster")
        cluster_counts = df['Tingkat Risiko'].value_counts().reset_index()
        cluster_counts.columns = ['Tingkat Risiko', 'Jumlah']
        
        fig = px.pie(
            cluster_counts, 
            names='Tingkat Risiko', 
            values='Jumlah', 
            color='Tingkat Risiko',
            color_discrete_map={
                'Rendah': '#00CC96',
                'Sedang': '#FFA15A',
                'Tinggi': '#EF553B'
            },
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.subheader("Data Ringkas")
        st.dataframe(df[['Provinsi', 'Tingkat Risiko', 'TBC_CDR', 'AIDS', 'DBD']], use_container_width=True, height=350)
