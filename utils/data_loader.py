import pandas as pd
import streamlit as st
import os

def standardize_columns(df):
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
            
    return df.rename(columns=rename_mapping)

def check_compatibility(df):
    required_features = ["TBC_CDR", "TBC_SR", "AIDS", "Kusta", "Malaria", "DBD"]
    return all(f in df.columns for f in required_features)

@st.cache_data
def load_data(year=2025):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_path = os.path.join(base_dir, "data", f"dataset_{year}.csv")
    
    # Fallback to old dataset.csv if year file doesn't exist
    if not os.path.exists(data_path):
        fallback_path = os.path.join(base_dir, "data", "dataset.csv")
        if os.path.exists(fallback_path):
            df = pd.read_csv(fallback_path)
        else:
            raise FileNotFoundError(f"File data tidak ditemukan untuk tahun {year}")
    else:
        df = pd.read_csv(data_path)
    
    return standardize_columns(df)

def get_available_years(only_compatible=True):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(base_dir, "data")
    
    years = []
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.startswith("dataset_") and filename.endswith(".csv"):
                try:
                    year_part = filename.replace("dataset_", "").replace(".csv", "")
                    year_val = int(year_part)
                    
                    if only_compatible:
                        filepath = os.path.join(data_dir, filename)
                        # Read only 1 row to check column headers efficiently
                        df_preview = pd.read_csv(filepath, nrows=1)
                        df_std = standardize_columns(df_preview)
                        if check_compatibility(df_std):
                            years.append(year_val)
                    else:
                        years.append(year_val)
                except Exception:
                    pass
    
    # Fallback to 2025 if no compatible year files found
    if not years:
        years = [2025]
            
    return sorted(list(set(years)))
