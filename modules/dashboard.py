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
    col2.metric("Risiko Rendah", len(df[df['Tingkat Risiko'] == 'Rendah']))
    col3.metric("Risiko Sedang", len(df[df['Tingkat Risiko'] == 'Sedang']))
    col4.metric("Risiko Tinggi", len(df[df['Tingkat Risiko'] == 'Tinggi']))

    st.markdown("---")

    # Choropleth Map
    st.subheader("🗺️ Peta Persebaran Risiko Penyakit")
    
    # URL GeoJSON untuk batasan administrasi tiap provinsi di Indonesia
    geojson_url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json"
    
    color_map = {
        'Rendah': '#00CC96', # Hijau
        'Sedang': '#FFA15A', # Kuning/Oranye
        'Tinggi': '#EF553B'  # Merah
    }
    
    # Menampilkan Peta Choropleth
    fig_map = px.choropleth(
        df,
        geojson=geojson_url,
        featureidkey="properties.Propinsi", # Menyesuaikan dengan property dari geoJSON
        locations="Provinsi",               # Nama kolom yang ada di dataset
        color="Tingkat Risiko",
        color_discrete_map=color_map,
        hover_name="Provinsi",
        hover_data=['TBC_CDR', 'AIDS', 'Kusta', 'Malaria', 'DBD'],
        projection="mercator"
    )
    
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")

    # Bar chart with dropdown and Pie Chart
    col_chart, col_bar = st.columns(2)

    with col_chart:
        st.subheader("Distribusi Cluster")
        cluster_counts = df['Tingkat Risiko'].value_counts().reset_index()
        cluster_counts.columns = ['Tingkat Risiko', 'Jumlah']
        
        fig_pie = px.pie(
            cluster_counts, 
            names='Tingkat Risiko', 
            values='Jumlah', 
            color='Tingkat Risiko',
            color_discrete_map=color_map,
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        st.subheader("Top 5 Provinsi per Penyakit")
        
        disease_options = ['TBC_CDR', 'AIDS', 'Kusta', 'Malaria', 'DBD']
        selected_disease = st.selectbox("Pilih Penyakit:", disease_options)
        
        top5_df = df[['Provinsi', selected_disease, 'Tingkat Risiko']].sort_values(by=selected_disease, ascending=False).head(5)
        
        fig_bar = px.bar(
            top5_df, 
            x='Provinsi', 
            y=selected_disease, 
            color='Tingkat Risiko',
            color_discrete_map=color_map,
            text_auto=True
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    st.subheader("Data Ringkas")
    st.dataframe(df[['Provinsi', 'Tingkat Risiko', 'TBC_CDR', 'AIDS', 'Kusta', 'Malaria', 'DBD']], use_container_width=True)
