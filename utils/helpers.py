import streamlit as st
import os

def load_model(year=None):
    if year is None:
        year = st.session_state.get('selected_year', 2025)
        
    df = get_preprocessed_clustered_data(year)
    features = ["TBC_CDR", "TBC_SR", "AIDS", "Kusta", "Malaria", "DBD"]
    
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])
    
    model = KMeans(n_clusters=3, random_state=42, n_init=10)
    model.fit(X_scaled)
    
    return model, scaler

def get_cluster_label(cluster_id):
    mapping = {
        0: "Rendah",
        1: "Sedang",
        2: "Tinggi"
    }
    return mapping.get(cluster_id, "Unknown")

@st.cache_data
def get_preprocessed_clustered_data(year=2025):
    from utils.data_loader import load_data
    import pandas as pd
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    
    df = load_data(year)
    features = ["TBC_CDR", "TBC_SR", "AIDS", "Kusta", "Malaria", "DBD"]
    
    # 1. Cleaning
    if "Provinsi" in df.columns:
        invalid_rows = ["Catatan", "Indonesia", "Kondisi", "Kondisi Luar Biasa", "Total", "Nasional"]
        df = df[~df["Provinsi"].isin(invalid_rows)]
        df = df[~df["Provinsi"].str.contains("Catatan", na=False, case=False)]
        df = df[~df["Provinsi"].str.contains("Kondisi", na=False, case=False)]
        
    df = df.dropna(subset=['Provinsi'])
    df = df.dropna(how='all')
        
    df[features] = df[features].replace(["-", "–"], pd.NA)
    df[features] = df[features].apply(pd.to_numeric, errors='coerce')
    
    # Impute missing values with mean instead of dropping them
    df[features] = df[features].fillna(df[features].mean())
    df = df.reset_index(drop=True)
    
    # 2. Fit Scaler and KMeans dynamically in-memory
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])
    
    model = KMeans(n_clusters=3, random_state=42, n_init=10)
    model.fit(X_scaled)
    
    # 3. Dynamic Labeling Logic (Ensuring Consistent Risk Interpretability)
    # Centroids mapping: higher cases = higher risk, higher success rate = lower risk
    centroids = model.cluster_centers_  # shape (3, 6)
    
    burden_scores = []
    for idx in range(3):
        c = centroids[idx]
        # TBC_CDR (+) - TBC_SR (-) + AIDS (+) + Kusta (+) + Malaria (+) + DBD (+)
        score = c[0] - c[1] + c[2] + c[3] + c[4] + c[5]
        burden_scores.append((idx, score))
        
    # Sort by burden score in ascending order (lowest burden -> lowest risk)
    burden_scores.sort(key=lambda x: x[1])
    
    # Map cluster index to label
    mapping = {
        burden_scores[0][0]: "Rendah",
        burden_scores[1][0]: "Sedang",
        burden_scores[2][0]: "Tinggi"
    }
    
    # Update cluster mapping
    df['Cluster'] = model.predict(X_scaled)
    df['Tingkat Risiko'] = df['Cluster'].map(mapping)
    
    return df
