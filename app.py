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
st.sidebar.title("Navigasi")

menu = st.sidebar.selectbox(
    "Pilih halaman",
    ["Dashboard", "EDA", "Preprocessing", "Clustering", "Metodologi"],
)

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
