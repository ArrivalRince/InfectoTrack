import streamlit as st
from modules import dashboard, eda, clustering, predict, methodology

st.set_page_config(page_title="InfectoTrack", layout="wide")
st.title("InfectoTrack")
st.sidebar.title("Navigasi")

menu = st.sidebar.selectbox(
    "Pilih halaman",
    ["Dashboard", "EDA", "Clustering", "Prediksi", "Metodologi"],
)

if menu == "Dashboard":
    dashboard.show()
elif menu == "EDA":
    eda.show()
elif menu == "Clustering":
    clustering.show()
elif menu == "Prediksi":
    predict.show()
elif menu == "Metodologi":
    methodology.show()
