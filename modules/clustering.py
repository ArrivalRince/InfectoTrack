import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler
from utils.data_loader import load_data
from utils.helpers import get_cluster_label, load_model

def show():
    st.header("🔵 Analisis Clustering (K-Means)")
    st.write("Visualisasi pengelompokan (clustering) dari algoritma K-Means.")

    from utils.helpers import get_preprocessed_clustered_data
    df = get_preprocessed_clustered_data()
    features = ["TBC_CDR", "TBC_SR", "AIDS", "Kusta", "Malaria", "DBD"]

    # 1. PCA for 2D visualization
    pca = PCA(n_components=2)
    pca_features = pca.fit_transform(df[features])
    df['PCA1'] = pca_features[:, 0]
    df['PCA2'] = pca_features[:, 1]

    st.subheader("Visualisasi Persebaran Cluster (2D PCA)")
    
    fig = px.scatter(
        df, x="PCA1", y="PCA2", 
        color="Tingkat Risiko", 
        hover_name="Provinsi",
        hover_data=features,
        color_discrete_map={
            'Rendah': '#00CC96',
            'Sedang': '#FFA15A',
            'Tinggi': '#EF553B'
        },
        size_max=10
    )
    fig.update_traces(marker=dict(size=12, opacity=0.85, line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(
        xaxis_title="Principal Component 1 (PCA1)",
        yaxis_title="Principal Component 2 (PCA2)",
        legend_title="Tingkat Risiko"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 2. Radar Chart Profil Cluster
    st.subheader("🕸️ Radar Chart Profil Cluster")
    st.write("Profil rata-rata tiap cluster untuk semua 6 variabel (dinormalisasi 0-1 untuk visualisasi berimbang).")
    
    # Scale features to [0, 1] for radar chart representation
    scaler_minmax = MinMaxScaler()
    df_scaled_radar = df.copy()
    df_scaled_radar[features] = scaler_minmax.fit_transform(df[features])
    cluster_means_radar = df_scaled_radar.groupby('Tingkat Risiko')[features].mean()

    # Layout for 3 radar charts side-by-side
    col_r1, col_r2, col_r3 = st.columns(3)
    
    colors_map = {
        'Rendah': '#00CC96',
        'Sedang': '#FFA15A',
        'Tinggi': '#EF553B'
    }

    def create_radar_chart(cluster_label):
        r_values = cluster_means_radar.loc[cluster_label].values.tolist()
        # Close the loop
        r_values += [r_values[0]]
        theta_values = features + [features[0]]
        
        fig = go.Figure()
        color = colors_map[cluster_label]
        
        fig.add_trace(go.Scatterpolar(
            r=r_values,
            theta=theta_values,
            fill='toself',
            name=cluster_label,
            line_color=color,
            fillcolor=color,
            opacity=0.4
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=False,
            title=dict(
                text=f"Profil Risiko {cluster_label}",
                x=0.5,
                xanchor='center',
                font=dict(size=14, color='white' if st.get_option("theme.base") == "dark" else 'black')
            ),
            margin=dict(l=40, r=40, t=50, b=40),
            height=300
        )
        return fig

    with col_r1:
        st.plotly_chart(create_radar_chart('Rendah'), use_container_width=True)
    with col_r2:
        st.plotly_chart(create_radar_chart('Sedang'), use_container_width=True)
    with col_r3:
        st.plotly_chart(create_radar_chart('Tinggi'), use_container_width=True)

    st.markdown("---")

    # 3. Centroid Bar Chart (dengan drop-down)
    st.subheader("📊 Perbandingan Nilai Centroid (Rata-Rata per Cluster)")
    
    # Calculate raw/denormalized means
    cluster_means = df.groupby('Tingkat Risiko')[features].mean().reset_index()
    
    col_t, col_b = st.columns([1, 1])
    
    with col_t:
        st.write("Tabel Nilai Centroid (Nilai Riil):")
        st.dataframe(
            cluster_means.style.background_gradient(cmap='Blues', subset=features).format(precision=2), 
            use_container_width=True
        )
        
    with col_b:
        selected_feature_bar = st.selectbox("Pilih Indikator untuk Perbandingan Centroid:", features)
        fig_bar = px.bar(
            cluster_means,
            x='Tingkat Risiko',
            y=selected_feature_bar,
            color='Tingkat Risiko',
            color_discrete_map=colors_map,
            title=f"Perbandingan Rata-rata {selected_feature_bar} (Nilai Riil)",
            text_auto='.2f'
        )
        fig_bar.update_layout(showlegend=False, xaxis_title="Tingkat Risiko", yaxis_title="Nilai Rata-rata")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # 4. Tabel Provinsi + Label Cluster (Terfilter)
    st.subheader("📋 Daftar Provinsi dan Label Cluster")
    st.write("Daftar lengkap pembagian cluster provinsi. Gunakan filter di bawah untuk membatasi tampilan.")

    selected_clusters = st.multiselect(
        "Filter Berdasarkan Tingkat Risiko:",
        options=["Rendah", "Sedang", "Tinggi"],
        default=["Rendah", "Sedang", "Tinggi"]
    )
    
    filtered_df = df[df['Tingkat Risiko'].isin(selected_clusters)]
    
    def color_cluster(val):
        if val == 'Rendah':
            return 'background-color: rgba(0, 204, 150, 0.2); color: #00CC96; font-weight: bold; border: 1px solid #00CC96; text-align: center;'
        elif val == 'Sedang':
            return 'background-color: rgba(255, 161, 90, 0.2); color: #FFA15A; font-weight: bold; border: 1px solid #FFA15A; text-align: center;'
        elif val == 'Tinggi':
            return 'background-color: rgba(239, 85, 59, 0.2); color: #EF553B; font-weight: bold; border: 1px solid #EF553B; text-align: center;'
        return ''

    # Reorder columns for display
    display_cols = ['Provinsi', 'Tingkat Risiko'] + features
    styled_filtered = filtered_df[display_cols].style.map(
        color_cluster, subset=['Tingkat Risiko']
    ).format(precision=2, subset=features)
    
    st.dataframe(styled_filtered, use_container_width=True, height=350)

    st.markdown("---")

    # 5. Evaluasi Kualitas Clustering (Silhouette Score & Elbow Method)
    st.subheader("📈 Evaluasi Kualitas K-Means")
    
    # Calculate evaluation metrics
    model, scaler = load_model()
    X_scaled = scaler.transform(df[features])
    
    sil_score = silhouette_score(X_scaled, df['Cluster'])
    
    # Calculate Elbow Curve
    K_range = range(1, 9)
    inertias = []
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)

    col_eval1, col_eval2 = st.columns([1, 1.5])
    
    with col_eval1:
        st.write("### Ringkasan Evaluasi")
        st.metric(label="Silhouette Score (k=3)", value=f"{sil_score:.4f}")
        
        st.markdown("""
        **Analisis & Penafsiran:**
        *   **Silhouette Score ($0.1778$):** Menunjukkan struktur klaster yang cukup terpisah. Mengingat kompleksitas data kesehatan dengan 6 dimensi (indikator) dan variabilitas tinggi antar provinsi di Indonesia, nilai ini tergolong wajar dan mencerminkan pola persebaran yang nyata.
        *   **Jumlah Cluster ($k=3$):** Dipilih secara intuitif untuk membagi tingkat kerawanan penyakit menular menjadi **Rendah**, **Sedang**, dan **Tinggi**, yang memudahkan dinas kesehatan dalam memprioritaskan alokasi intervensi medis.
        """)
        
    with col_eval2:
        # Elbow Chart
        fig_elbow = px.line(
            x=list(K_range),
            y=inertias,
            markers=True,
            title="Metode Elbow (Inersia vs. Jumlah Cluster)",
            labels={'x': 'Jumlah Cluster (k)', 'y': 'Inersia (WCSS)'}
        )
        # Highlight k=3
        fig_elbow.add_annotation(
            x=3, y=inertias[2],
            text="k=3 (Siku Optimal)",
            showarrow=True,
            arrowhead=1,
            ax=45, ay=-45,
            font=dict(color="#EF553B", size=12),
            arrowcolor="#EF553B"
        )
        fig_elbow.update_layout(
            xaxis=dict(tickmode='linear', tick0=1, dtick=1)
        )
        st.plotly_chart(fig_elbow, use_container_width=True)

