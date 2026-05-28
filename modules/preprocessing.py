import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import streamlit.components.v1 as components
import json
from utils.data_loader import load_data
import os

def show():
    st.title("Preprocessing Data")
    st.markdown("---")

    # Load raw data
    df_raw = load_data()

    # ==========================
    # 1. SECTION PREVIEW & CLEANING
    # ==========================
    st.header("1. Data Cleaning")
    st.write("Proses awal untuk membersihkan dataset dari baris/kolom yang tidak relevan.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Proses Cleaning:")
        st.markdown("- [x] Menghapus baris kosong")
        st.markdown("- [x] Menghapus baris 'Catatan'")
        st.markdown("- [x] Menghapus data selain provinsi")
        st.markdown("- [x] Menghapus data 'Indonesia' atau 'Kondisi'")
    
    with col2:
        st.success("✅ Seluruh proses data cleaning berhasil dijalankan.")

    # Apply Cleaning Logic
    df_clean = df_raw.copy()
    
    # Menghapus baris kosong (jika seluruhnya NaN)
    df_clean = df_clean.dropna(how='all')
    
    # Menghapus baris "Catatan", "Indonesia", "Kondisi", dan baris selain provinsi jika ada
    if "Provinsi" in df_clean.columns:
        invalid_rows = ["Catatan", "Indonesia", "Kondisi", "Kondisi Luar Biasa", "Total", "Nasional"]
        df_clean = df_clean[~df_clean["Provinsi"].isin(invalid_rows)]
        # Filter substring jika kolom mengandung kata "Catatan" atau "Kondisi"
        df_clean = df_clean[~df_clean["Provinsi"].str.contains("Catatan", na=False, case=False)]
        df_clean = df_clean[~df_clean["Provinsi"].str.contains("Kondisi", na=False, case=False)]

    st.write("**Dataset setelah Data Cleaning:**")
    st.dataframe(df_clean, use_container_width=True)

    # ==========================
    # 2. FEATURE SELECTION
    # ==========================
    st.header("2. Feature Selection")
    # Rename kolom yang memiliki nama panjang/BPS agar sesuai dengan standar sistem (TBC_CDR, TBC_SR, dll)
    rename_mapping = {}
    for col in df_clean.columns:
        col_lower = col.lower()
        if "angka penemuan tbc" in col_lower or "cdr" in col_lower:
            rename_mapping[col] = "TBC_CDR"
        elif "keberhasilan pengobatan tbc" in col_lower or "sr" in col_lower:
            rename_mapping[col] = "TBC_SR"
        elif "hiv" in col_lower or "aids" in col_lower:
            rename_mapping[col] = "AIDS"
        elif "kusta" in col_lower:
            rename_mapping[col] = "Kusta"
        elif "malaria" in col_lower:
            rename_mapping[col] = "Malaria"
        elif "dbd" in col_lower or "dengue" in col_lower:
            rename_mapping[col] = "DBD"
            
    df_clean = df_clean.rename(columns=rename_mapping)
    
    if "Provinsi" in df_clean.columns:
        labels = df_clean["Provinsi"].reset_index(drop=True)
        # Pisahkan atribut numerik
        # Hapus juga kolom lain yang tidak relevan seperti index / cluster jika ada di raw data
        cols_to_drop = [col for col in ["Provinsi", "Unnamed: 0", "Cluster", "index", "id", "ID"] if col in df_clean.columns]
        features = df_clean.drop(columns=cols_to_drop).reset_index(drop=True)
        
        # Ensure we only take the standard features if they exist
        std_features = ["TBC_CDR", "TBC_SR", "AIDS", "Kusta", "Malaria", "DBD"]
        available_features = [f for f in std_features if f in features.columns]
        if available_features:
            features = features[available_features]
            
        col_lbl, col_feat = st.columns([1, 2])
        with col_lbl:
            st.write("**Label (Provinsi):**")
            st.dataframe(labels, use_container_width=True)
        with col_feat:
            st.write("**Fitur Numerik:**")
            st.dataframe(features, use_container_width=True)
    else:
        st.warning("Kolom 'Provinsi' tidak ditemukan. Pastikan data mentah memiliki kolom tersebut.")
        features = df_clean.copy()
        labels = pd.Series(index=features.index, dtype='object')

    # ==========================
    # 3. HANDLE INVALID VALUE
    # ==========================
    st.header("3. Handle Invalid Value")
    st.write("Mengubah nilai yang tidak valid (seperti simbol '-') menjadi *Missing Value* (NaN) agar bisa diproses lebih lanjut, lalu mengkonversi seluruh fitur menjadi tipe numerik.")
    
    # Replace "-" and "–" with NaN
    features = features.replace(["-", "–"], np.nan)
    # Convert all columns to numeric
    features = features.apply(pd.to_numeric, errors='coerce')
    
    st.success("✅ Simbol '–' berhasil dikonversi menjadi NaN.")
    st.success("✅ Seluruh data fitur telah dikonversi menjadi numerik.")

    # ==========================
    # 4. HANDLE MISSING VALUE
    # ==========================
    st.header("4. Handle Missing Value")
    st.write("Melakukan pengecekan *missing value* dan melakukan **Mean Imputation** (mengganti nilai kosong dengan rata-rata dari kolom tersebut).")
    
    missing_before = features.isnull().sum()
    
    # Impute missing values with mean
    features_imputed = features.fillna(features.mean())
    missing_after = features_imputed.isnull().sum()
    
    # Show comparison
    df_missing_comparison = pd.DataFrame({
        "Kolom": missing_before.index,
        "Missing Sebelum": missing_before.values,
        "Missing Sesudah": missing_after.values
    })
    
    st.dataframe(df_missing_comparison, use_container_width=True)
    if missing_before.sum() > 0:
        st.info("Catatan: Ditemukan missing value dan telah berhasil ditangani menggunakan mean imputation.")
    else:
        st.info("Catatan: Tidak ditemukan missing value pada dataset.")

    # ==========================
    # 5. STANDARD SCALER
    # ==========================
    st.header("5. StandardScaler")
    st.write("Melakukan standardisasi pada data agar memiliki rata-rata ($\mu$) = 0 dan standar deviasi ($\sigma$) = 1.")
    st.latex(r"z = \frac{x - \mu}{\sigma}")
    
    st.write("**Data sebelum scaling:**")
    st.dataframe(features_imputed.head(), use_container_width=True)
    
    # Apply Standard Scaler
    scaler = StandardScaler()
    features_scaled_array = scaler.fit_transform(features_imputed)
    features_scaled = pd.DataFrame(features_scaled_array, columns=features_imputed.columns)
    
    st.write("**Data sesudah scaling:**")
    st.dataframe(features_scaled.head(), use_container_width=True)
    
    st.write("**Statistik hasil scaling (Cek Mean mendekati 0 dan Std mendekati 1):**")
    stat_mean = features_scaled.mean().round(4)
    stat_std = features_scaled.std().round(4)
    df_stats = pd.DataFrame({
        "Mean (μ)": stat_mean,
        "Std Dev (σ)": stat_std
    })
    st.dataframe(df_stats, use_container_width=True)

    # ==========================
    # 6. VISUALISASI DATA (APEXCHARTS)
    # ==========================
    st.header("6. Visualisasi Data (Setelah Standardisasi)")
    st.write("Menampilkan Boxplot untuk mendeteksi sebaran dan outlier, serta Heatmap untuk melihat korelasi antar fitur menggunakan ApexCharts.")
    
    # Prepare data for Boxplot (ApexCharts format)
    # We will create a boxplot series: { x: 'Column Name', y: [min, q1, median, q3, max] }
    box_series = []
    for col in features_scaled.columns:
        q1 = features_scaled[col].quantile(0.25)
        median = features_scaled[col].median()
        q3 = features_scaled[col].quantile(0.75)
        iqr = q3 - q1
        min_val = features_scaled[col].min()
        max_val = features_scaled[col].max()
        
        # Determine actual whisker limits (usually within 1.5 * IQR)
        whisker_low = max(min_val, q1 - 1.5 * iqr)
        whisker_high = min(max_val, q3 + 1.5 * iqr)
        
        box_series.append({
            "x": col,
            "y": [whisker_low, q1, median, q3, whisker_high]
        })
        
    box_series_json = json.dumps([{"type": "boxPlot", "data": box_series}])
    
    # Prepare data for Heatmap (ApexCharts format)
    corr_matrix = features_scaled.corr().round(2)
    heatmap_series = []
    for col_name in corr_matrix.columns:
        row_data = []
        for idx_name in corr_matrix.index:
            row_data.append({"x": idx_name, "y": corr_matrix.loc[idx_name, col_name]})
        heatmap_series.append({
            "name": col_name,
            "data": row_data
        })
        
    heatmap_series_json = json.dumps(heatmap_series)
    
    # HTML template to load ApexCharts via CDN and render charts
    apexcharts_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <style>
            .chart-container {{
                display: flex;
                flex-direction: column;
                gap: 40px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }}
            h3 {{ text-align: center; color: #333; font-weight: 600; margin-bottom: 5px; }}
            .chart-wrapper {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }}
        </style>
    </head>
    <body>
        <div class="chart-container">
            <div class="chart-wrapper">
                <h3>Boxplot (Distribusi & Outlier)</h3>
                <div id="boxplot"></div>
            </div>
            <div class="chart-wrapper">
                <h3>Heatmap (Korelasi Fitur)</h3>
                <div id="heatmap"></div>
            </div>
        </div>

        <script>
            // Render Boxplot
            var boxplotOptions = {{
                series: {box_series_json},
                chart: {{ type: 'boxPlot', height: 350, toolbar: {{ show: false }} }},
                colors: ['#008FFB', '#FEB019'],
                title: {{ text: '', align: 'left' }},
                plotOptions: {{ boxPlot: {{ colors: {{ upper: '#5C4742', lower: '#A5978B' }} }} }}
            }};
            var boxplotChart = new ApexCharts(document.querySelector("#boxplot"), boxplotOptions);
            boxplotChart.render();

            // Render Heatmap
            var heatmapOptions = {{
                series: {heatmap_series_json},
                chart: {{ type: 'heatmap', height: 400, toolbar: {{ show: false }} }},
                dataLabels: {{ enabled: true }},
                colors: ["#008FFB"],
                title: {{ text: '' }}
            }};
            var heatmapChart = new ApexCharts(document.querySelector("#heatmap"), heatmapOptions);
            heatmapChart.render();
        </script>
    </body>
    </html>
    """
    
    components.html(apexcharts_html, height=900, scrolling=True)

    # ==========================
    # 7. FINAL OUTPUT
    # ==========================
    st.header("7. Final Output")
    st.success("🎉 **Data siap digunakan untuk K-Means Clustering**")
    
    final_df = features_scaled.copy()
    final_df.insert(0, "Provinsi", labels)
    
    st.write(f"- **Jumlah fitur final:** {features_scaled.shape[1]} fitur numerik")
    st.write(f"- **Ukuran dataset final:** {final_df.shape[0]} baris x {final_df.shape[1]} kolom")
    
    st.write("**Tabel Dataset Final:**")
    st.dataframe(final_df, use_container_width=True)

    # ==========================
    # 8. TOMBOL ACTION
    # ==========================
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("💾 Simpan Hasil Preprocessing", use_container_width=True):
            # Define output directory and save the dataframe
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "dataset_preprocessed.csv")
            final_df.to_csv(output_path, index=False)
            st.success(f"Data berhasil disimpan di: `{output_path}`")
            
    with col_btn2:
        if st.button("🚀 Lanjut ke Clustering", use_container_width=True):
            st.info("Pindah ke halaman Clustering dari sidebar untuk melanjutkan proses!")
