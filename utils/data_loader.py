import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_path = os.path.join(base_dir, "data", "dataset.csv")
    df = pd.read_csv(data_path)
    
    # Standardize column names
    rename_mapping = {}
    for col in df.columns:
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
            
    df = df.rename(columns=rename_mapping)
    return df
