import joblib
import streamlit as st
import os

@st.cache_resource
def load_model():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    model_path = os.path.join(base_dir, "model", "kmeans_model.pkl")
    scaler_path = os.path.join(base_dir, "model", "scaler.pkl")
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    return model, scaler

def get_cluster_label(cluster_id):
    mapping = {
        0: "Rendah",
        1: "Sedang",
        2: "Tinggi"
    }
    return mapping.get(cluster_id, "Unknown")

@st.cache_data
def get_preprocessed_clustered_data():
    from utils.data_loader import load_data
    import pandas as pd
    
    df = load_data()
    features = ["TBC_CDR", "TBC_SR", "AIDS", "Kusta", "Malaria", "DBD"]
    
    # 1. Cleaning
    if "Provinsi" in df.columns:
        invalid_rows = ["Catatan", "Indonesia", "Kondisi", "Kondisi Luar Biasa", "Total", "Nasional"]
        df = df[~df["Provinsi"].isin(invalid_rows)]
        df = df[~df["Provinsi"].str.contains("Catatan", na=False, case=False)]
        df = df[~df["Provinsi"].str.contains("Kondisi", na=False, case=False)]
        
    df[features] = df[features].replace(["-", "–"], pd.NA)
    df[features] = df[features].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=features).reset_index(drop=True)
    
    # 2. Predict Clusters
    model, scaler = load_model()
    X_scaled = scaler.transform(df[features])
    df['Cluster'] = model.predict(X_scaled)
    df['Tingkat Risiko'] = df['Cluster'].apply(get_cluster_label)
    
    return df
