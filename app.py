import streamlit as st
import pandas as pd
import geopandas as gpd 
import json
from streamlit_folium import st_folium



st.set_page_config(
    page_title='GeoClean',
    page_icon='🌍',
    layout='wide'
)

st.title("GeoClean")
st.subheader("Geospatial Data Quality & Validation System")

st.write(
    "Unggah data geospasial, periksa kualitasnya, "
    "bersihkan kesalahan sederhana, dan tinjau temuan "
    "sebelum mengunduh hasil akhir."
)

upload_file=st.file_uploader(
    "Unggah Dataset",
    type=("csv",'geojson')
)

if upload_file is not None: 
    try:
        if upload_file.name.lower().endswith(".csv"):
            df = pd.read_csv(upload_file)
        else:
            df = gpd.read_csv(upload_file)

        st.success("Dataset berhasil dibaca!")

        st.success("Dataset berhasil dibaca!")

        col1, col2 = st.columns(2)
        col1.metric("Jumlah baris", len(df))
        col2.metric("Jumlah kolom", len(df.columns))

        st.subheader("Preview dataset")
        st.dataframe(df.head(100), use_container_width=True)

    except Exception as e:
        st.error(f"File tidak dapat dibaca: {e}")   