import streamlit as st
import plotly.express as px
from sklearn.decomposition import PCA
from utils.data_loader import load_data
from utils.helpers import get_cluster_label, load_model

def show():
    st.header("🔵 Analisis Clustering (K-Means)")
    st.write("Visualisasi pengelompokan (clustering) dari algoritma K-Means.")

    df = load_data()
    features = ["TBC_CDR", "TBC_SR", "AIDS", "Kusta", "Malaria", "DBD"]
    
    df['Tingkat Risiko'] = df['Cluster'].apply(get_cluster_label)

    # PCA for 2D visualization
    pca = PCA(n_components=2)
    pca_features = pca.fit_transform(df[features])
    df['PCA1'] = pca_features[:, 0]
    df['PCA2'] = pca_features[:, 1]

    st.subheader("Visualisasi Persebaran Cluster (2D PCA)")
    
    fig = px.scatter(
        df, x="PCA1", y="PCA2", 
        color="Tingkat Risiko", 
        hover_data=["Provinsi"] + features,
        color_discrete_map={
            'Rendah': '#00CC96',
            'Sedang': '#FFA15A',
            'Tinggi': '#EF553B'
        },
        size_max=10
    )
    fig.update_traces(marker=dict(size=10, opacity=0.8, line=dict(width=1, color='DarkSlateGrey')))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Karakteristik Centroid (Rata-Rata per Cluster)")
    
    # Calculate means
    cluster_means = df.groupby('Tingkat Risiko')[features].mean().reset_index()
    st.dataframe(cluster_means.style.background_gradient(cmap='Blues'), use_container_width=True)
