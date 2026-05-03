import os
import joblib
import streamlit as st

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

@st.cache_resource
def load_scaler():
    path = os.path.join(BASE_DIR, "model", "scaler.pkl")
    return joblib.load(path)

@st.cache_resource
def load_model():
    path = os.path.join(BASE_DIR, "model", "kmeans_model.pkl")
    return joblib.load(path)
