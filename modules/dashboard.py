import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.data_loader import load_data
from utils.helpers import get_cluster_label

# =====================================================================
# COLOR & MAPPING CONFIGURATION
# =====================================================================
RISIKO_COLOR = {"Rendah": "🟢", "Sedang": "🟠", "Tinggi": "🔴"}
COLOR_MAP = {
    'Rendah': '#00CC96',  # Hijau
    'Sedang': '#FFA15A',  # Kuning/Oranye
    'Tinggi': '#EF553B'   # Merah
}
DISEASE_ICONS = {
    'TBC_CDR': '🦠',
    'AIDS': '🩸',
    'Kusta': '🩺',
    'Malaria': '🦟',
    'DBD': '🦟'
}
DISEASE_NAMES = {
    'TBC_CDR': 'TBC (CDR)',
    'AIDS': 'AIDS',
    'Kusta': 'Kusta',
    'Malaria': 'Malaria',
    'DBD': 'Demam Berdarah (DBD)'
}

# Region mapping for Indonesia
REGION_MAPPING = {
    'Aceh': 'Sumatra', 'Sumatera Utara': 'Sumatra', 'Sumatera Barat': 'Sumatra',
    'Riau': 'Sumatra', 'Jambi': 'Sumatra', 'Sumatera Selatan': 'Sumatra',
    'Bengkulu': 'Sumatra', 'Lampung': 'Sumatra', 'Kepulauan Bangka Belitung': 'Sumatra',
    'Kepulauan Riau': 'Sumatra', 'DKI Jakarta': 'Jawa', 'Jawa Barat': 'Jawa',
    'Jawa Tengah': 'Jawa', 'DI Yogyakarta': 'Jawa', 'Jawa Timur': 'Jawa',
    'Banten': 'Jawa', 'Bali': 'Bali', 'Nusa Tenggara Barat': 'Nusa Tenggara',
    'Nusa Tenggara Timur': 'Nusa Tenggara', 'Kalimantan Barat': 'Kalimantan',
    'Kalimantan Tengah': 'Kalimantan', 'Kalimantan Selatan': 'Kalimantan',
    'Kalimantan Timur': 'Kalimantan', 'Kalimantan Utara': 'Kalimantan',
    'Sulawesi Utara': 'Sulawesi', 'Sulawesi Tengah': 'Sulawesi',
    'Sulawesi Selatan': 'Sulawesi', 'Sulawesi Tenggara': 'Sulawesi',
    'Gorontalo': 'Sulawesi', 'Sulawesi Barat': 'Sulawesi',
    'Maluku': 'Maluku', 'Maluku Utara': 'Maluku', 'Papua Barat': 'Papua',
    'Papua': 'Papua'
}

@st.dialog("📊 Detail Informasi Provinsi")
def show_province_detail(prov_name, df):
    p_data = df[df['Provinsi'] == prov_name].iloc[0]
    
    # Header Info
    icon = RISIKO_COLOR.get(p_data['Tingkat Risiko'], "⚪")
    
    st.markdown(f"### {icon} Provinsi {prov_name}")
    st.caption(f"Status K-Means: **Cluster {p_data['Cluster']}** — Risiko **{p_data['Tingkat Risiko']}**")
    st.divider()
    
    # 2-column layout for beautiful data presentation
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="🦠 TBC (CDR)", value=round(p_data.get('TBC_CDR', 0), 2))
        st.metric(label="🦟 Malaria", value=round(p_data.get('Malaria', 0), 2))
        st.metric(label="🩸 Kasus AIDS", value=round(p_data.get('AIDS', 0), 2))
    with c2:
        st.metric(label="🩺 Kusta", value=round(p_data.get('Kusta', 0), 2))
        st.metric(label="🦟 Insiden DBD", value=round(p_data.get('DBD', 0), 2))
    
    st.divider()
    
    # Comparison with national average
    st.subheader("📊 Perbandingan dengan Rata-rata Nasional")
    disease_cols = ['TBC_CDR', 'AIDS', 'Kusta', 'Malaria', 'DBD']
    
    comparison_data = []
    for disease in disease_cols:
        prov_val = p_data.get(disease, 0)
        national_avg = df[disease].mean()
        diff = prov_val - national_avg
        badge = "🔴 Lebih Tinggi" if diff > 0 else "🟢 Lebih Rendah" if diff < 0 else "⚪ Sama"
        comparison_data.append({
            'Penyakit': DISEASE_NAMES[disease],
            'Provinsi': round(prov_val, 2),
            'Rata-rata': round(national_avg, 2),
            'Perbedaan': round(diff, 2),
            'Status': badge
        })
    
    comp_df = pd.DataFrame(comparison_data)
    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    
    st.divider()
    st.info("💡 Data di atas dirangkum dari data awal dan digunakan dalam perhitungan K-Means Clustering.")

@st.dialog("🗂️ Detail Area Cluster")
def show_cluster_detail(risiko, df_cluster, df_all):
    icon = RISIKO_COLOR.get(risiko, "⚪")
    
    st.markdown(f"### {icon} Cluster Risiko {risiko}")
    st.caption(f"Menampilkan **{len(df_cluster)}** provinsi yang termasuk dalam kategori risiko {risiko}.")
    st.divider()

    # Menampilkan daftar provinsi dalam layout grid yang rapi
    cols = st.columns(3)
    for i, prov in enumerate(df_cluster['Provinsi']):
        with cols[i % 3]:
            if st.button(prov, use_container_width=True, key=f"cbtn_{prov}_{risiko}"):
                st.session_state['open_prov_detail'] = prov
                st.rerun()
    
    st.divider()
    st.info("💡 Daftar ini dikelompokkan berdasarkan kemiripan tingkat kasus penyakit.")

# =====================================================================
# FEATURE 1: ENHANCED KEY INSIGHTS WITH SMART ANALYSIS
# =====================================================================
def show_key_insights(df):
    st.subheader("⚡ Smart Key Insights")
    
    disease_cols = ['TBC_CDR', 'AIDS', 'Kusta', 'Malaria', 'DBD']
    
    # Find top critical provinces
    df_tinggi = df[df['Tingkat Risiko'] == 'Tinggi'].sort_values('TBC_CDR', ascending=False)
    top_critical = df_tinggi.iloc[0] if len(df_tinggi) > 0 else None
    
    # Find most prevalent disease
    disease_means = {disease: df[disease].mean() for disease in disease_cols}
    top_disease = max(disease_means, key=disease_means.get)
    
    # Overall health score
    total_high_risk = len(df[df['Tingkat Risiko'] == 'Tinggi'])
    health_percentage = ((len(df) - total_high_risk) / len(df)) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔴 Provinsi Kritis", top_critical['Provinsi'] if top_critical is not None else "N/A")
    
    with col2:
        st.metric("🦠 Penyakit Terburuk", DISEASE_ICONS[top_disease] + ' ' + DISEASE_NAMES[top_disease].split('(')[0].strip())
    
    with col3:
        st.metric("📊 Health Score", f"{health_percentage:.1f}%")
    
    with col4:
        st.metric("🔴 Provinsi Risiko Tinggi", len(df[df['Tingkat Risiko'] == 'Tinggi']))
    
    # ===== PATTERN ANALYSIS =====
    st.markdown("#### 🔎 Pattern Detection")
    
    col_pat1, col_pat2 = st.columns(2)
    
    with col_pat1:
        # Identify diseases that tend to appear together
        disease_pairs = []
        for i, disease1 in enumerate(disease_cols):
            for disease2 in disease_cols[i+1:]:
                corr = df[disease1].corr(df[disease2])
                if abs(corr) > 0.5:
                    disease_pairs.append((disease1, disease2, corr))
        
        if disease_pairs:
            disease_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
            top_pair = disease_pairs[0]
            corr_status = "🔴 Kuat" if abs(top_pair[2]) > 0.7 else "🟠 Sedang"
            st.info(f"{corr_status} Pola: {DISEASE_NAMES[top_pair[0]]} ↔ {DISEASE_NAMES[top_pair[1]]} "
                   f"(Korelasi: {top_pair[2]:.2f})")
    
    with col_pat2:
        # Anomaly detection: provinces with significant outliers
        df_copy = df.copy()
        df_copy['Total_Disease'] = df_copy[disease_cols].sum(axis=1)
        mean_total = df_copy['Total_Disease'].mean()
        std_total = df_copy['Total_Disease'].std()
        threshold = mean_total + (std_total * 1.5)
        anomalies = df_copy[df_copy['Total_Disease'] > threshold]
        
        if len(anomalies) > 0:
            top_anomaly = anomalies.nlargest(1, 'Total_Disease').iloc[0]
            st.warning(f"⚠️ Anomali Deteksi: {top_anomaly['Provinsi']} memiliki beban penyakit "
                      f"tidak normal ({top_anomaly['Total_Disease']:.1f})")
    
    st.markdown("---")

# =====================================================================
# FEATURE 2: ALERT & WARNING BADGES
# =====================================================================
def show_alerts_and_warnings(df):
    st.subheader("⚠️ Alerts & Warnings")
    
    # Critical provinces
    df_critical = df[df['Tingkat Risiko'] == 'Tinggi'].sort_values('TBC_CDR', ascending=False)
    
    if len(df_critical) > 0:
        st.error(f"🔴 **CRITICAL**: {len(df_critical)} provinsi dengan risiko TINGGI memerlukan perhatian segera!")
        
        with st.expander("📍 Lihat Provinsi Kritis"):
            for idx, row in df_critical.head(10).iterrows():
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    st.markdown("🔴")
                with col2:
                    st.write(f"**{row['Provinsi']}** - Cluster {row['Cluster']}")
                with col3:
                    if st.button("Detail", key=f"alert_detail_{row['Provinsi']}"):
                        st.session_state['open_prov_detail'] = row['Provinsi']
                        st.rerun()
    else:
        st.success("✅ Semua provinsi dalam status aman!")
    
    st.markdown("---")

# =====================================================================
# FEATURE 3: INTERACTIVE COMPARISON TOOL
# =====================================================================
def show_interactive_comparison(df):
    st.subheader("🔄 Interactive Province Comparison")
    
    provinces = df['Provinsi'].unique()
    
    col_comp1, col_comp2 = st.columns(2)
    
    with col_comp1:
        prov1 = st.selectbox("Pilih Provinsi 1:", provinces, key="prov_comp_1")
    
    with col_comp2:
        prov2 = st.selectbox("Pilih Provinsi 2:", provinces, index=1 if len(provinces) > 1 else 0, key="prov_comp_2")
    
    if prov1 != prov2:
        disease_cols = ['TBC_CDR', 'AIDS', 'Kusta', 'Malaria', 'DBD']
        
        p1_data = df[df['Provinsi'] == prov1].iloc[0]
        p2_data = df[df['Provinsi'] == prov2].iloc[0]
        
        # Normalize data untuk radar chart (0-1 scale)
        normalized_data = {}
        for disease in disease_cols:
            max_val = df[disease].max()
            normalized_data[disease] = {
                prov1: p1_data[disease] / max_val if max_val > 0 else 0,
                prov2: p2_data[disease] / max_val if max_val > 0 else 0
            }
        
        # Create radar chart
        categories = [DISEASE_NAMES[d] for d in disease_cols]
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[normalized_data[d][prov1] for d in disease_cols],
            theta=categories,
            fill='toself',
            name=prov1,
            line_color='#EF553B'
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[normalized_data[d][prov2] for d in disease_cols],
            theta=categories,
            fill='toself',
            name=prov2,
            line_color='#00CC96'
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            height=500,
            title=f"Perbandingan Profil Penyakit: {prov1} vs {prov2}"
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Detailed comparison table
        st.markdown("#### 📊 Detailed Metrics")
        
        comparison_data = []
        for disease in disease_cols:
            p1_val = p1_data[disease]
            p2_val = p2_data[disease]
            diff = p1_val - p2_val
            pct_diff = ((p1_val - p2_val) / p2_val * 100) if p2_val > 0 else 0
            
            comparison_data.append({
                'Penyakit': DISEASE_NAMES[disease],
                prov1: round(p1_val, 2),
                prov2: round(p2_val, 2),
                'Selisih': f"{diff:+.2f}",
                '% Diff': f"{pct_diff:+.1f}%"
            })
        
        comp_df = pd.DataFrame(comparison_data)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
        
        # Risk level comparison
        col_risk1, col_risk2 = st.columns(2)
        with col_risk1:
            st.info(f"**{prov1}** - Risiko: {p1_data['Tingkat Risiko']} (Cluster {p1_data['Cluster']})")
        with col_risk2:
            st.info(f"**{prov2}** - Risiko: {p2_data['Tingkat Risiko']} (Cluster {p2_data['Cluster']})")
    else:
        st.warning("⚠️ Silakan pilih 2 provinsi yang berbeda untuk membandingkan!")
    
    st.markdown("---")

# =====================================================================
# FEATURE 4: SUMMARY STATISTICS CARDS
# =====================================================================
def show_summary_statistics(df):
    st.subheader("📊 Summary Statistics per Penyakit")
    
    disease_cols = ['TBC_CDR', 'AIDS', 'Kusta', 'Malaria', 'DBD']
    
    cols = st.columns(len(disease_cols))
    
    for idx, disease in enumerate(disease_cols):
        with cols[idx]:
            stats_data = df[disease].describe()
            
            with st.container(border=True):
                st.markdown(f"### {DISEASE_ICONS[disease]} {DISEASE_NAMES[disease]}")
                st.metric("Mean", f"{stats_data['mean']:.2f}")
                st.metric("Max", f"{stats_data['max']:.2f}")
                st.metric("Min", f"{stats_data['min']:.2f}")
                st.metric("Median", f"{df[disease].median():.2f}")
    
    st.markdown("---")



# =====================================================================
# FEATURE 9: REGIONAL COMPARISON CHART
# =====================================================================
def show_regional_comparison(df):
    st.subheader("🌍 Perbandingan Penyakit per Region")
    
    # Add region column
    df_copy = df.copy()
    df_copy['Region'] = df_copy['Provinsi'].map(REGION_MAPPING)
    
    disease_cols = ['TBC_CDR', 'AIDS', 'Kusta', 'Malaria', 'DBD']
    
    # Aggregate by region
    region_agg = df_copy.groupby('Region')[disease_cols].mean().reset_index()
    
    # Melt for plotting
    region_melted = region_agg.melt(id_vars=['Region'], var_name='Penyakit', value_name='Nilai')
    region_melted['Penyakit'] = region_melted['Penyakit'].map(lambda x: DISEASE_ICONS[x] + ' ' + DISEASE_NAMES[x])
    
    # Chart type selector
    chart_type = st.radio("Jenis Chart:", ["Bar", "Area", "Line"], horizontal=True, key="region_chart_type")
    
    if chart_type == "Bar":
        fig_regional = px.bar(
            region_melted,
            x='Region',
            y='Nilai',
            color='Penyakit',
            barmode='group',
            title="Rata-rata Penyakit per Region"
        )
    elif chart_type == "Area":
        fig_regional = px.area(
            region_melted,
            x='Region',
            y='Nilai',
            color='Penyakit',
            title="Rata-rata Penyakit per Region"
        )
    else:
        fig_regional = px.line(
            region_melted,
            x='Region',
            y='Nilai',
            color='Penyakit',
            markers=True,
            title="Rata-rata Penyakit per Region"
        )
    
    st.plotly_chart(fig_regional, use_container_width=True)
    st.markdown("---")

# =====================================================================
# FEATURE 8: ADVANCED FILTER PANEL
# =====================================================================
def apply_advanced_filters(df):
    st.subheader("🔍 Advanced Filters")
    
    with st.expander("📋 Klik untuk membuka/tutup filter", expanded=True):
        col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 0.8])
        
        with col1:
            risk_filter = st.multiselect(
                "Filter by Risk Level:",
                options=['Rendah', 'Sedang', 'Tinggi'],
                default=['Rendah', 'Sedang', 'Tinggi'],
                key="risk_filter_main"
            )
        
        with col2:
            region_filter = st.multiselect(
                "Filter by Region:",
                options=sorted(set(REGION_MAPPING.values())),
                default=sorted(set(REGION_MAPPING.values())),
                key="region_filter_main"
            )
        
        with col3:
            disease_cols = ['TBC_CDR', 'AIDS', 'Kusta', 'Malaria', 'DBD']
            selected_disease = st.selectbox(
                "Sort by Disease:",
                options=disease_cols,
                format_func=lambda x: DISEASE_NAMES[x],
                key="sort_disease_main"
            )
        
        with col4:
            st.write("")
            st.write("")
            if st.button("🔄 Reset", use_container_width=True):
                st.rerun()
    
    # Apply filters only if there are selections
    if not risk_filter or not region_filter:
        st.warning("Silakan pilih minimal satu Risk Level dan satu Region")
        return df
    
    # Apply filters
    df_filtered = df[df['Tingkat Risiko'].isin(risk_filter)].copy()
    
    df_filtered['Region'] = df_filtered['Provinsi'].map(REGION_MAPPING)
    df_filtered = df_filtered[df_filtered['Region'].isin(region_filter)]
    
    # Sort by selected disease
    df_filtered = df_filtered.sort_values(by=selected_disease, ascending=False)
    
    return df_filtered

# =====================================================================
# FEATURE 7: PROVINCE DEEP-DIVE PROFILE
# =====================================================================
def show_province_deep_dive(df):
    st.subheader("📍 Profil Provinsi Terpilih")
    
    provinces = st.selectbox("Pilih Provinsi:", df['Provinsi'].unique(), key="province_selector")
    
    p_data = df[df['Provinsi'] == provinces].iloc[0]
    icon = RISIKO_COLOR.get(p_data['Tingkat Risiko'], "⚪")
    
    with st.container(border=True):
        st.markdown(f"## {icon} {provinces}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Risk Level", p_data['Tingkat Risiko'])
        with col2:
            st.metric("Cluster", p_data['Cluster'])
        with col3:
            region = REGION_MAPPING.get(provinces, "Unknown")
            st.metric("Region", region)
        with col4:
            # Rank dalam kategori risiko
            same_risk = df[df['Tingkat Risiko'] == p_data['Tingkat Risiko']]
            rank = (same_risk['TBC_CDR'].rank(ascending=False) == (same_risk[same_risk['Provinsi'] == provinces].index[0])).sum()
            st.metric("Rank (Risk Category)", f"{rank}/{len(same_risk)}")
        
        st.divider()
        
        # Disease profile
        st.write("**Profil Penyakit:**")
        disease_cols = ['TBC_CDR', 'AIDS', 'Kusta', 'Malaria', 'DBD']
        
        disease_data = []
        for disease in disease_cols:
            val = p_data[disease]
            rank = (df[disease].rank(ascending=False) == (df[df['Provinsi'] == provinces].index[0])).sum()
            disease_data.append({
                'Penyakit': DISEASE_NAMES[disease],
                'Nilai': round(val, 2),
                'Rank': rank
            })
        
        disease_df = pd.DataFrame(disease_data)
        st.dataframe(disease_df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Recommendations
        st.write("**Rekomendasi Aksi:**")
        worst_disease = disease_data[0]['Penyakit']
        st.info(f"• Prioritaskan kontrol {worst_disease} di {provinces}\n"
                f"• Fokus pada pencegahan dan screening untuk 3 penyakit teratas\n"
                f"• Koordinasikan dengan provinsi tetangga di region {region}")
    
    st.markdown("---")

# =====================================================================
# FEATURE 10: METHODOLOGY INFO PANEL
# =====================================================================
def show_methodology_panel():
    st.subheader("📚 Tentang Dashboard & Metodologi")
    
    with st.expander("🔍 Cara Membaca Dashboard", expanded=False):
        st.markdown("""
        ### Panduan Penggunaan Dashboard
        
        **1. Key Insights**
        - Ringkasan cepat status kesehatan nasional
        - Identifikasi provinsi dan penyakit paling kritis
        
        **2. Alerts & Warnings**
        - Daftar provinsi dengan status risiko TINGGI
        - Klik untuk melihat detail lebih lanjut
        
        **3. Risk Heatmap**
        - Visualisasi matriks: penyakit vs provinsi
        - Warna lebih merah = risiko lebih tinggi
        
        **4. Top 10 Provinces**
        - Ranking provinsi berdasarkan beban penyakit total
        - Disease Burden Score = rata-rata dari 5 penyakit
        
        **5. Disease Correlation**
        - Identifikasi penyakit yang cenderung muncul bersama
        - Trendline menunjukkan arah korelasi
        
        **6. Regional Comparison**
        - Perbandingan penyakit antar region geografis
        - Pilih chart type (Bar/Area/Line) sesuai preferensi
        """)
    
    with st.expander("🔬 K-Means Clustering Explained", expanded=False):
        st.markdown("""
        ### Penjelasan K-Means Clustering
        
        **Apa itu K-Means?**
        - Algoritma machine learning untuk mengelompokkan data
        - Membagi 34 provinsi menjadi 3 cluster berdasarkan profil penyakit
        
        **3 Risk Clusters:**
        - **Cluster 0 (Rendah 🟢)**: Provinsi dengan beban penyakit rendah
        - **Cluster 1 (Sedang 🟠)**: Provinsi dengan beban penyakit sedang
        - **Cluster 2 (Tinggi 🔴)**: Provinsi dengan beban penyakit tinggi
        
        **Fitur yang Digunakan:**
        - TBC_CDR: Tingkat Penemuan TBC
        - TBC_SR: Tingkat Keberhasilan Pengobatan TBC
        - AIDS: Jumlah kasus AIDS
        - Kusta: Jumlah kasus Kusta
        - Malaria: Jumlah kasus Malaria
        - DBD: Insiden Demam Berdarah
        """)
    
    with st.expander("📊 Definisi Penyakit", expanded=False):
        disease_definitions = {
            'TBC (CDR)': 'Case Detection Rate - Persentase penemuan kasus TBC aktif',
            'AIDS': 'Acquired Immunodeficiency Syndrome - Jumlah kasus HIV/AIDS yang terdeteksi',
            'Kusta': 'Penyakit Kusta/Lepra - Penyakit infeksi bakteri Mycobacterium leprae',
            'Malaria': 'Penyakit parasit yang ditularkan nyamuk Anopheles',
            'DBD': 'Demam Berdarah Dengue - Penyakit virus yang ditularkan nyamuk Aedes'
        }
        
        for disease, definition in disease_definitions.items():
            st.write(f"**{disease}**: {definition}")
    
    with st.expander("📅 Data Information", expanded=False):
        st.markdown("""
        **Data Source**: Profil Kesehatan Indonesia 2025
        
        **Update Frequency**: Data diperbarui sesuai dengan update dari sumber resmi
        
        **Coverage**: 34 Provinsi di Indonesia
        
        **Catatan Penting**:
        - Data merupakan agregasi dari berbagai sumber kesehatan
        - Beberapa nilai missing diimputasi dengan rata-rata
        - Outlier detection dilakukan pada preprocessing stage
        """)
    

def show_year_comparison():
    st.subheader("🔄 Perbandingan Perkembangan Risiko Antar Tahun")
    st.write("Bandingkan klaster risiko dan perkembangan indikator penyakit menular dari tahun ke tahun.")
    
    from utils.data_loader import get_available_years
    from utils.helpers import get_preprocessed_clustered_data
    
    years = get_available_years()
    if len(years) < 2:
        st.info("💡 Unggah dataset baru untuk tahun yang berbeda di halaman **EDA** untuk melihat perbandingan antar tahun.")
        return
        
    # Kumpulkan data dari seluruh tahun yang tersedia
    prov_risk_matrix = []
    for y in years:
        df_y = get_preprocessed_clustered_data(y)
        for _, row in df_y.iterrows():
            prov_risk_matrix.append({
                'Provinsi': row['Provinsi'],
                'Tahun': str(y),
                'Tingkat Risiko': row['Tingkat Risiko']
            })
            
    df_matrix = pd.DataFrame(prov_risk_matrix)
    risk_rank = {"Rendah": 0, "Sedang": 1, "Tinggi": 2}
    
    # =====================================================================
    # 1. TREN INDEKS RISIKO NASIONAL (GRAFIK GARIS TUNGGAL)
    # =====================================================================
    st.markdown("### 📈 Tren Indeks Risiko Nasional (Semua Tahun)")
    st.write("Indeks Risiko Nasional dihitung berdasarkan rata-rata tingkat risiko seluruh provinsi (Rendah = 0, Sedang = 1, Tinggi = 2). Kenaikan menunjukkan peningkatan risiko nasional secara keseluruhan.")
    
    national_trends = []
    for y in years:
        df_y = get_preprocessed_clustered_data(y)
        total_weight = df_y['Tingkat Risiko'].map(risk_rank).sum()
        avg_risk = total_weight / len(df_y) if len(df_y) > 0 else 0
        national_trends.append({
            'Tahun': str(y),
            'Indeks Risiko': round(avg_risk, 3)
        })
        
    df_national_trend = pd.DataFrame(national_trends)
    
    fig_national = px.line(
        df_national_trend,
        x='Tahun',
        y='Indeks Risiko',
        markers=True,
        title='Tren Indeks Risiko Kesehatan Nasional (Tahun ke Tahun)',
        template="plotly_dark"
    )
    fig_national.update_traces(line=dict(width=3, color='#EF553B'), marker=dict(size=8))
    fig_national.update_layout(
        yaxis=dict(range=[-0.1, 2.1])
    )
    st.plotly_chart(fig_national, use_container_width=True)
    
    st.markdown("---")
    
    # =====================================================================
    # 2. TREN RISIKO PER PROVINSI (GRAFIK GARIS TUNGGAL)
    # =====================================================================
    st.markdown("### 📌 Tren Perkembangan Risiko per Provinsi (Semua Tahun)")
    st.write("Pilih provinsi untuk melihat perkembangan tingkat risiko dari tahun ke tahun secara spesifik.")
    
    all_provinces = sorted(list(df_matrix['Provinsi'].unique()))
    selected_prov = st.selectbox("Pilih Provinsi:", all_provinces, key="prov_trend_selectbox")
    
    df_prov = df_matrix[df_matrix['Provinsi'] == selected_prov].copy()
    df_prov['Bobot Risiko'] = df_prov['Tingkat Risiko'].map(risk_rank)
    df_prov = df_prov.sort_values('Tahun')
    
    # Render line chart for selected province
    fig_prov = px.line(
        df_prov,
        x='Tahun',
        y='Bobot Risiko',
        markers=True,
        title=f'Tren Perkembangan Risiko Provinsi: {selected_prov}',
        template="plotly_dark"
    )
    # Color based on latest risk status
    latest_status = df_prov['Tingkat Risiko'].iloc[-1]
    color_line = COLOR_MAP.get(latest_status, '#FFA15A')
    
    fig_prov.update_traces(line=dict(width=3, color=color_line), marker=dict(size=8))
    fig_prov.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 2],
            ticktext=['Rendah 🟢', 'Sedang 🟠', 'Tinggi 🔴'],
            range=[-0.2, 2.2]
        )
    )
    st.plotly_chart(fig_prov, use_container_width=True)
    
    st.markdown("---")
    
    # =====================================================================
    # 3. MATRIKS REKAM JEJAK RISIKO PROVINSI (SEMUA TAHUN)
    # =====================================================================
    st.markdown("### 🗺️ Matriks Perkembangan Risiko Provinsi")
    st.write("Tabel rekam jejak tingkat risiko untuk seluruh provinsi pada semua tahun data yang tersedia.")
    
    if not df_matrix.empty:
        df_pivot = df_matrix.pivot(index='Provinsi', columns='Tahun', values='Tingkat Risiko')
        df_pivot = df_pivot.sort_index()
        
        # Fungsi styling warna sel
        def style_risk_cell(val):
            if val == 'Rendah':
                return 'background-color: rgba(0, 204, 150, 0.2); color: #00CC96; font-weight: bold; text-align: center;'
            elif val == 'Sedang':
                return 'background-color: rgba(255, 161, 90, 0.2); color: #FFA15A; font-weight: bold; text-align: center;'
            elif val == 'Tinggi':
                return 'background-color: rgba(239, 85, 59, 0.2); color: #EF553B; font-weight: bold; text-align: center;'
            return 'text-align: center; color: gray;'

        styled_pivot = df_pivot.style.map(style_risk_cell)
        st.dataframe(styled_pivot, use_container_width=True, height=500)
    
    st.markdown("---")
    
    # =====================================================================
    # 4. ANALISIS DETAIL PERGESERAN DUA TAHUN
    # =====================================================================
    st.markdown("### 🔍 Analisis Pergeseran Detail (Dua Tahun)")
    st.write("Bandingkan pergeseran status risiko secara spesifik antara dua tahun pilihan.")
    
    col1, col2 = st.columns(2)
    with col1:
        year_base = st.selectbox("Pilih Tahun Awal (Basis):", options=years[:-1], index=0)
    with col2:
        compare_options = [y for y in years if y > year_base]
        year_compare = st.selectbox("Pilih Tahun Pembanding:", options=compare_options, index=0)
        
    df_base = get_preprocessed_clustered_data(year_base)
    df_compare = get_preprocessed_clustered_data(year_compare)
    
    # Merge on Province
    df_merged = pd.merge(
        df_base[['Provinsi', 'Tingkat Risiko', 'Cluster']], 
        df_compare[['Provinsi', 'Tingkat Risiko', 'Cluster']], 
        on='Provinsi', 
        suffixes=(f'_{year_base}', f'_{year_compare}')
    )
    
    def get_status_change(row):
        r_base = risk_rank.get(row[f'Tingkat Risiko_{year_base}'], 0)
        r_comp = risk_rank.get(row[f'Tingkat Risiko_{year_compare}'], 0)
        if r_comp > r_base:
            return "🔴 Meningkat (Memburuk)"
        elif r_comp < r_base:
            return "🟢 Menurun (Membaik)"
        else:
            return "⚪ Tetap"
            
    df_merged['Perubahan Status'] = df_merged.apply(get_status_change, axis=1)
    
    # Visual Metrics
    counts = df_merged['Perubahan Status'].value_counts()
    c_worse = counts.get("🔴 Meningkat (Memburuk)", 0)
    c_better = counts.get("🟢 Menurun (Membaik)", 0)
    c_same = counts.get("⚪ Tetap", 0)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("🟢 Provinsi Membaik", c_better)
    col_m2.metric("🔴 Provinsi Memburuk", c_worse)
    col_m3.metric("⚪ Provinsi Tetap", c_same)
    
    def color_change(val):
        if "Meningkat" in val:
            return 'background-color: rgba(239, 85, 59, 0.2); color: #EF553B; font-weight: bold; text-align: center;'
        elif "Menurun" in val:
            return 'background-color: rgba(0, 204, 150, 0.2); color: #00CC96; font-weight: bold; text-align: center;'
        return 'color: gray; text-align: center;'
        
    styled_merged = df_merged[['Provinsi', f'Tingkat Risiko_{year_base}', f'Tingkat Risiko_{year_compare}', 'Perubahan Status']].style.map(
        color_change, subset=['Perubahan Status']
    )
    st.dataframe(styled_merged, use_container_width=True, height=400)
    
st.markdown("---")

def show():
    from utils.helpers import get_preprocessed_clustered_data
    selected_year = st.session_state.get('selected_year', 2025)
    
    # Handle state for province detail dialog
    if 'open_prov_detail' in st.session_state:
        prov_to_open = st.session_state.pop('open_prov_detail')
        df_temp = get_preprocessed_clustered_data(selected_year)
        show_province_detail(prov_to_open, df_temp)

    st.header("📊 Dashboard Persebaran Penyakit")
    st.write("Dashboard informatif dan eksplanatoris untuk analisis risiko penyakit menular di seluruh Indonesia.")

    dashboard_mode = st.radio(
        "Pilih Mode Analisis:",
        ["📊 Analisis Tahun Aktif", "🔄 Perbandingan Antar Tahun"],
        horizontal=True
    )
    st.markdown("---")
    
    if dashboard_mode == "🔄 Perbandingan Antar Tahun":
        show_year_comparison()
        return

    df = get_preprocessed_clustered_data(selected_year)
    
    # ===== SECTION 1: KEY INSIGHTS =====
    show_key_insights(df)
    
    # ===== SECTION 2: ALERTS & WARNINGS =====
    show_alerts_and_warnings(df)
    
    # ===== SECTION 3: SUMMARY STATISTICS =====
    show_summary_statistics(df)
    
    # ===== SECTION 4: MAIN METRICS WITH CLUSTER BUTTONS =====
    st.subheader("📈 Ringkasan Cluster Risiko")
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

    # ===== SECTION 5: CHOROPLETH MAP ====="
    st.subheader("🗺️ Peta Persebaran Risiko Penyakit")
    
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
    
    geojson_url = 'https://raw.githubusercontent.com/ans-4175/peta-indonesia-geojson/master/indonesia-prov.geojson'
    
    fig_map = px.choropleth_mapbox(
        df,
        geojson=geojson_url,
        featureidkey="properties.Propinsi",
        locations="GeoJSON_Name",
        color="Tingkat Risiko",
        color_discrete_map=COLOR_MAP,
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

    # ===== SECTION 6: DISTRIBUTION CHARTS ====="
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
            color_discrete_map=COLOR_MAP,
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
            color_discrete_map=COLOR_MAP,
            text_auto=True
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    
    # ===== SECTION 7: REGIONAL COMPARISON ====="
    show_regional_comparison(df)
    
    # ===== SECTION 8: INTERACTIVE COMPARISON ====="
    show_interactive_comparison(df)
    
    # ===== SECTION 9: ADVANCED FILTERS & FILTERED DATA ====="
    st.subheader("📊 Hasil Filter & Export Data")
    
    df_filtered = apply_advanced_filters(df)
    
    st.write(f"**Menampilkan {len(df_filtered)} dari {len(df)} provinsi**")
    st.dataframe(
        df_filtered[['Provinsi', 'Tingkat Risiko', 'Cluster', 'TBC_CDR', 'AIDS', 'Kusta', 'Malaria', 'DBD']],
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # ===== SECTION 10: PROVINCE DEEP-DIVE =====
    show_province_deep_dive(df)
    
    # ===== SECTION 11: METHODOLOGY & INFO =====
    show_methodology_panel()
