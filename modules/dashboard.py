import streamlit as st
import plotly.express as px
from utils.data_loader import load_data
from utils.helpers import get_cluster_label

@st.dialog("📊 Detail Informasi Provinsi")
def show_province_detail(prov_name, df):
    p_data = df[df['Provinsi'] == prov_name].iloc[0]
    
    # Header Info
    risiko_color = {"Rendah": "🟢", "Sedang": "🟠", "Tinggi": "🔴"}
    icon = risiko_color.get(p_data['Tingkat Risiko'], "⚪")
    
    st.markdown(f"### {icon} Provinsi {prov_name}")
    st.caption(f"Status K-Means: **Cluster {p_data['Cluster']}** — Risiko **{p_data['Tingkat Risiko']}**")
    st.divider()
    
    # 2-column layout for beautiful data presentation
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="🦠 TBC (CDR)", value=p_data.get('TBC_CDR', 'N/A'))
        st.metric(label="🦟 Malaria", value=p_data.get('Malaria', 'N/A'))
        st.metric(label="🩸 Kasus AIDS", value=p_data.get('AIDS', 'N/A'))
    with c2:
        st.metric(label="🩺 Kusta", value=p_data.get('Kusta', 'N/A'))
        st.metric(label="🦟 Insiden DBD", value=p_data.get('DBD', 'N/A'))
    
    st.divider()
    st.info("💡 Data di atas dirangkum dari data awal dan digunakan dalam perhitungan K-Means Clustering.")

@st.dialog("🗂️ Detail Area Cluster")
def show_cluster_detail(risiko, df_cluster, df_all):
    risiko_color = {"Rendah": "🟢", "Sedang": "🟠", "Tinggi": "🔴"}
    icon = risiko_color.get(risiko, "⚪")
    
    st.markdown(f"### {icon} Cluster Risiko {risiko}")
    st.caption(f"Menampilkan **{len(df_cluster)}** provinsi yang termasuk dalam kategori risiko {risiko}.")
    st.divider()

    # Menampilkan daftar provinsi dalam layout grid yang rapi
    cols = st.columns(3)
    for i, prov in enumerate(df_cluster['Provinsi']):
        with cols[i % 3]:
            # Jika user mengklik provinsi di sini, akan membuka dialog detail provinsinya!
            if st.button(prov, use_container_width=True, key=f"cbtn_{prov}_{risiko}"):
                st.session_state['open_prov_detail'] = prov
                st.rerun()
    
    st.divider()
    st.info("💡 Daftar ini dikelompokkan berdasarkan kemiripan tingkat kasus penyakit.")

def show():
    from utils.helpers import get_preprocessed_clustered_data
    # Menangani state jika user mengklik provinsi dari dalam dialog Cluster
    if 'open_prov_detail' in st.session_state:
        prov_to_open = st.session_state.pop('open_prov_detail')
        df_temp = get_preprocessed_clustered_data()
        show_province_detail(prov_to_open, df_temp)

    st.header("📊 Dashboard Persebaran Penyakit")
    st.write("Ringkasan distribusi provinsi berdasarkan risiko penyakit menular.")

    df = get_preprocessed_clustered_data()

    # Metrics dengan Button Dialog Interaktif
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Provinsi", len(df))
    
    with col2:
        df_rendah = df[df['Tingkat Risiko'] == 'Rendah']
        st.metric("Risiko Rendah", len(df_rendah))
        if st.button(f"🔍 Detail ({len(df_rendah)})", key="btn_rendah", use_container_width=True):
            show_cluster_detail("Rendah", df_rendah, df)
    
    with col3:
        df_sedang = df[df['Tingkat Risiko'] == 'Sedang']
        st.metric("Risiko Sedang", len(df_sedang))
        if st.button(f"🔍 Detail ({len(df_sedang)})", key="btn_sedang", use_container_width=True):
            show_cluster_detail("Sedang", df_sedang, df)

    with col4:
        df_tinggi = df[df['Tingkat Risiko'] == 'Tinggi']
        st.metric("Risiko Tinggi", len(df_tinggi))
        if st.button(f"🔍 Detail ({len(df_tinggi)})", key="btn_tinggi", use_container_width=True):
            show_cluster_detail("Tinggi", df_tinggi, df)

    st.markdown("---")

    # Choropleth Map Interaktif
    st.subheader("🗺️ Peta Persebaran Risiko Penyakit")
    
    # Mapping nama dataset dengan nama properti di GeoJSON agar peta terarsir seluas daratan provinsinya
    prov_mapping = {
        'Aceh' : 'DI. ACEH', 'Sumatera Utara' : 'SUMATERA UTARA', 'Sumatera Barat' : 'SUMATERA BARAT',
        'Riau' : 'RIAU', 'Jambi' : 'JAMBI', 'Sumatera Selatan' : 'SUMATERA SELATAN',
        'Bengkulu' : 'BENGKULU', 'Lampung' : 'LAMPUNG', 'Kepulauan Bangka Belitung' : 'BANGKA BELITUNG',
        'Kepulauan Riau' : 'KEPULAUAN RIAU', 'DKI Jakarta' : 'DKI JAKARTA', 'Jawa Barat' : 'JAWA BARAT',
        'Jawa Tengah' : 'JAWA TENGAH', 'DI Yogyakarta' : 'DAERAH ISTIMEWA YOGYAKARTA', 'Jawa Timur' : 'JAWA TIMUR',
        'Banten' : 'BANTEN', 'Bali' : 'BALI', 'Nusa Tenggara Barat' : 'NUSATENGGARA BARAT',
        'Nusa Tenggara Timur' : 'NUSA TENGGARA TIMUR', 'Kalimantan Barat' : 'KALIMANTAN BARAT',
        'Kalimantan Tengah' : 'KALIMANTAN TENGAH', 'Kalimantan Selatan' : 'KALIMANTAN SELATAN',
        'Kalimantan Timur' : 'KALIMANTAN TIMUR', 'Kalimantan Utara' : 'KALIMANTAN UTARA',
        'Sulawesi Utara' : 'SULAWESI UTARA', 'Sulawesi Tengah' : 'SULAWESI TENGAH',
        'Sulawesi Selatan' : 'SULAWESI SELATAN', 'Sulawesi Tenggara' : 'SULAWESI TENGGARA',
        'Gorontalo' : 'GORONTALO', 'Sulawesi Barat' : 'SULAWESI BARAT',
        'Maluku' : 'MALUKU', 'Maluku Utara' : 'MALUKU UTARA', 'Papua Barat' : 'PAPUA BARAT',
        'Papua' : 'PAPUA'
    }
    
    df['GeoJSON_Name'] = df['Provinsi'].map(prov_mapping)
    
    color_map = {
        'Rendah': '#00CC96', # Hijau
        'Sedang': '#FFA15A', # Kuning/Oranye
        'Tinggi': '#EF553B'  # Merah
    }
    
    geojson_url = 'https://raw.githubusercontent.com/ans-4175/peta-indonesia-geojson/master/indonesia-prov.geojson'
    
    # Menampilkan Peta Choropleth (Arsir Wilayah) mengunakan Mapbox
    # Catatan: Plotly otomatis menampilkan pop-up tooltip yang interaktif saat hover/diklik
    fig_map = px.choropleth_mapbox(
        df,
        geojson=geojson_url,
        featureidkey="properties.Propinsi",
        locations="GeoJSON_Name",
        color="Tingkat Risiko",
        color_discrete_map=color_map,
        hover_name="Provinsi",
        hover_data={'GeoJSON_Name': False, 'Tingkat Risiko': True, 'Cluster': True, 'TBC_CDR': True, 'AIDS': True, 'Kusta': True, 'Malaria': True, 'DBD': True},
        mapbox_style="carto-positron",
        center={"lat": -0.7893, "lon": 113.9213},
        zoom=3.5,
        opacity=0.7
    )
    
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
    st.dataframe(df[['Provinsi', 'Tingkat Risiko', 'Cluster', 'TBC_CDR', 'AIDS', 'Kusta', 'Malaria', 'DBD']], use_container_width=True)
