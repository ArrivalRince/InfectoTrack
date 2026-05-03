import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_path = os.path.join(base_dir, "data", "dataset.csv")
    df = pd.read_csv(data_path)
    return df
