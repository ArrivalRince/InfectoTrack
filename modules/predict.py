import streamlit as st
import pandas as pd
from utils.helpers import load_model, get_cluster_label

def show():
    st.header("🎯 Prediksi Tingkat Risiko Daerah")
    st.write("Masukkan indikator kesehatan daerah untuk memprediksi tingkat risikonya berdasarkan model K-Means yang telah dilatih.")

    model, scaler = load_model()

    with st.form("predict_form"):
        st.subheader("Input Indikator Kesehatan")
        col1, col2 = st.columns(2)
        
        with col1:
            tbc_cdr = st.number_input("TBC_CDR (Case Detection Rate %)", min_value=0.0, max_value=100.0, value=50.0)
            tbc_sr = st.number_input("TBC_SR (Success Rate %)", min_value=0.0, max_value=100.0, value=75.0)
            aids = st.number_input("Kasus AIDS", min_value=0, value=100)
            
        with col2:
            kusta = st.number_input("Kasus Kusta", min_value=0, value=50)
            malaria = st.number_input("Kasus Malaria", min_value=0, value=200)
            dbd = st.number_input("Kasus DBD", min_value=0, value=150)
            
        submitted = st.form_submit_button("Prediksi Cluster")

    if submitted:
        input_data = pd.DataFrame({
            "TBC_CDR": [tbc_cdr],
            "TBC_SR": [tbc_sr],
            "AIDS": [aids],
            "Kusta": [kusta],
            "Malaria": [malaria],
            "DBD": [dbd]
        })
        
        # Scaling
        scaled_data = scaler.transform(input_data)
        
        # Predict
        cluster_pred = model.predict(scaled_data)[0]
        label = get_cluster_label(cluster_pred)
        
        st.markdown("---")
        st.subheader("Hasil Prediksi")
        
        if label == "Rendah":
            st.success(f"Berdasarkan input, daerah ini diprediksi masuk dalam Cluster 0: **Risiko {label}**")
        elif label == "Sedang":
            st.warning(f"Berdasarkan input, daerah ini diprediksi masuk dalam Cluster 1: **Risiko {label}**")
        else:
            st.error(f"Berdasarkan input, daerah ini diprediksi masuk dalam Cluster 2: **Risiko {label}**")
