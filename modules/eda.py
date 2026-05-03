import streamlit as st
import plotly.express as px
from utils.data_loader import load_data

def show():
    st.header("📈 Exploratory Data Analysis (EDA)")
    st.write("Eksplorasi data dan korelasi antar variabel penyakit di Indonesia.")

    df = load_data()
    
    features = ["TBC_CDR", "TBC_SR", "AIDS", "Kusta", "Malaria", "DBD"]

    st.subheader("Distribusi Data Penyakit")
    selected_feature = st.selectbox("Pilih Penyakit:", features)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram
        fig_hist = px.histogram(
            df, 
            x=selected_feature, 
            nbins=15, 
            title=f"Histogram {selected_feature}",
            color_discrete_sequence=['#636EFA']
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        # Boxplot
        fig_box = px.box(
            df, 
            y=selected_feature, 
            title=f"Boxplot {selected_feature}",
            color_discrete_sequence=['#EF553B']
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")
    st.subheader("Heatmap Korelasi")
    
    corr_matrix = df[features].corr()
    fig_corr = px.imshow(
        corr_matrix, 
        text_auto=True, 
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Korelasi Antar Fitur"
    )
    st.plotly_chart(fig_corr, use_container_width=True)
