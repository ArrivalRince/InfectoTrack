import streamlit as st
import pandas as pd
import plotly.express as px
import os

def show():

    st.header("📊 EDA Data Mentah (Tanpa Cleaning)")

    # ================================
    # UPLOAD DATASET
    # ================================
    st.subheader("📤 Upload Dataset Baru")
    st.write("Silakan upload dataset baru Anda dalam format CSV. Anda dapat menentukan tahun data untuk diolah secara otomatis oleh sistem.")
    
    base_path = os.path.dirname(os.path.dirname(__file__))
    
    col_up1, col_up2 = st.columns([2, 1])
    with col_up2:
        upload_year = st.number_input(
            "Tahun Data yang Di-upload:",
            min_value=2000,
            max_value=2100,
            value=st.session_state.get('selected_year', 2026),
            step=1
        )
    with col_up1:
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"], key=f"uploader_{upload_year}")
        
    if uploaded_file is not None:
        try:
            # Baca file upload ke pandas untuk divalidasi
            df_uploaded = pd.read_csv(uploaded_file)
            from utils.data_loader import standardize_columns, check_compatibility
            df_std = standardize_columns(df_uploaded)
            
            if not check_compatibility(df_std):
                required_features = ["TBC_CDR", "TBC_SR", "AIDS", "Kusta", "Malaria", "DBD"]
                missing = [f for f in required_features if f not in df_std.columns]
                st.error(f"❌ Validasi Gagal! Dataset tidak memiliki kolom yang sesuai dengan kebutuhan sistem.")
                st.info(f"**Indikator yang hilang:** {', '.join(missing)}\n\n"
                        f"Pastikan nama kolom pada CSV mengandung kata kunci seperti: "
                        f"'CDR'/'Penemuan TBC', 'SR'/'Keberhasilan Pengobatan', 'AIDS'/'HIV', 'Kusta', 'Malaria', 'DBD'/'Dengue'.")
            else:
                st.success("✅ File valid! Siap untuk disimpan.")
                
                # Tampilkan pratinjau dataset
                st.write("**Pratinjau Data (5 Baris Pertama):**")
                st.dataframe(df_uploaded.head(5), use_container_width=True)
                
                # Tombol konfirmasi untuk menyimpan
                if st.button("💾 Simpan Dataset Baru", type="primary", use_container_width=True):
                    # Simpan berkas jika valid dan tombol ditekan
                    file_path = os.path.join(base_path, "data", f"dataset_{upload_year}.csv")
                    df_uploaded.to_csv(file_path, index=False)
                    st.success(f"✅ Dataset berhasil disimpan sebagai data tahun {upload_year}.")
                    st.session_state['selected_year'] = upload_year
                    st.cache_data.clear()  # Bersihkan cache agar data loader mengambil data terbaru
                    st.rerun()
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan saat membaca file: {str(e)}")

    # ================================
    # KELOLA & HAPUS DATASET
    # ================================
    st.markdown("---")
    st.subheader("🗑️ Kelola & Hapus Dataset")
    st.write("Hapus dataset tahunan yang sudah tidak diperlukan dari sistem.")
    
    from utils.data_loader import get_available_years
    available_years_to_delete = get_available_years(only_compatible=False)
    
    if len(available_years_to_delete) <= 1:
        st.warning("⚠️ Hanya terdapat 1 dataset di sistem. Penghapusan tidak diizinkan demi menjaga kestabilan aplikasi.")
    else:
        col_del1, col_del2 = st.columns([2, 1])
        with col_del1:
            delete_year = st.selectbox(
                "Pilih Tahun Dataset yang Ingin Dihapus:",
                options=available_years_to_delete,
                key="delete_year_select"
            )
        with col_del2:
            st.write("") # Spacer
            st.write("") # Spacer
            confirm_delete = st.button("🗑️ Hapus Dataset", type="secondary", use_container_width=True)
            
        if confirm_delete:
            st.session_state['confirm_delete_year'] = delete_year
            st.rerun()
            
    if 'confirm_delete_year' in st.session_state:
        del_yr = st.session_state['confirm_delete_year']
        
        st.warning(f"⚠️ Apakah Anda yakin ingin menghapus dataset tahun **{del_yr}**? Tindakan ini tidak dapat dibatalkan.")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("Ya, Hapus", type="primary", use_container_width=True):
                file_to_delete = os.path.join(base_path, "data", f"dataset_{del_yr}.csv")
                if os.path.exists(file_to_delete):
                    os.remove(file_to_delete)
                    st.success(f"✅ Dataset tahun {del_yr} berhasil dihapus.")
                else:
                    st.error(f"❌ File dataset_{del_yr}.csv tidak ditemukan.")
                
                # Update selected_year if the deleted one was selected
                remaining_years = [y for y in available_years_to_delete if y != del_yr]
                if remaining_years:
                    new_active_year = remaining_years[0]
                    if st.session_state.get('selected_year') == del_yr:
                        st.session_state['selected_year'] = new_active_year
                
                st.session_state.pop('confirm_delete_year', None)
                st.cache_data.clear()
                st.rerun()
                
        with col_c2:
            if st.button("Batal", use_container_width=True):
                st.session_state.pop('confirm_delete_year', None)
                st.rerun()

    # ================================
    # LOAD DATA
    # ================================
    selected_year = st.session_state.get('selected_year', 2025)
    file_path = os.path.join(base_path, "data", f"dataset_{selected_year}.csv")
    
    if not os.path.exists(file_path):
        # Coba fallback ke file default jika belum ada dataset untuk tahun terpilih
        file_path_default = os.path.join(base_path, "data", "Disease by Province and Type of Disease, 2025.csv")
        if os.path.exists(file_path_default):
            df = pd.read_csv(file_path_default)
            df.to_csv(file_path, index=False) # jadikan dataset utama tahun terpilih
        else:
            st.warning(f"⚠️ Belum ada dataset untuk tahun {selected_year}. Silakan upload dataset CSV terlebih dahulu.")
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