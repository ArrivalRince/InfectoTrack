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
