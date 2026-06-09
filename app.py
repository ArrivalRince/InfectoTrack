import streamlit as st
from modules import dashboard, eda, preprocessing, clustering, methodology

st.set_page_config(page_title="InfectoTrack", layout="wide")

def load_css(file_name):
    import os
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css('assets/style.css')

st.title("InfectoTrack")
from utils.data_loader import get_available_years

# Get available years from data files
available_years = get_available_years()

st.sidebar.title("Navigasi")

menu = st.sidebar.selectbox(
    "Pilih halaman",
    ["Dashboard", "EDA", "Preprocessing", "Clustering", "Metodologi"],
)

st.sidebar.markdown("---")
st.sidebar.subheader("📅 Tahun Data")
selected_year = st.sidebar.selectbox(
    "Pilih Tahun Analisis:",
    options=available_years,
    index=available_years.index(st.session_state.get('selected_year', 2025)) if st.session_state.get('selected_year', 2025) in available_years else 0
)
st.session_state['selected_year'] = selected_year
st.sidebar.info(f"Tahun aktif: **{selected_year}**")
st.sidebar.markdown("---")

if menu == "Dashboard":
    dashboard.show()
elif menu == "EDA":
    eda.show()
elif menu == "Preprocessing":
    preprocessing.show()
elif menu == "Clustering":
    clustering.show()
elif menu == "Metodologi":
    methodology.show()
