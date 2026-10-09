import streamlit as st
import pandas as pd
import geopandas as gpd 
import numpy as np
import folium
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
            st.success("Dataset berhasil dibaca!")

            col1, col2 = st.columns(2)
            col1.metric("Jumlah baris", len(df))
            col2.metric("Jumlah kolom", len(df.columns))

            st.subheader("Preview dataset")
            st.dataframe(df.head(100), use_container_width=True)

        elif upload_file.name.lower().endswith(".geojson"):
            geojson_data = gpd.read_file(upload_file)
            st.success(f"File berhasil dibaca: {len(geojson_data)} fitur.")

            if geojson_data.crs is None:
                st.warning(
                    "CRS tidak tercantum di file. GeoJSON seharusnya menggunakan "
                    "EPSG:4326; koordinat akan dianggap sebagai longitude/latitude."
                )
                geojson_data = geojson_data.set_crs(epsg=4326)
            elif geojson_data.crs != "EPSG:4326":
                geojson_data = geojson_data.to_crs(epsg=4326)

            valid_geometry = (
                geojson_data.geometry.notna() & ~geojson_data.geometry.is_empty
            )
            valid_data = geojson_data.loc[valid_geometry]
            map_data = valid_data.head(100).copy()
            st.caption(
                f"CRS peta: EPSG:4326 · Menampilkan {len(map_data)} dari "
                f"{len(valid_data)} fitur valid (maksimal 100)"
            )

            if map_data.empty:
                st.warning(
                    "Tidak ada geometri yang dapat divisualisasikan. "
                    "Periksa apakah fitur di file memiliki koordinat."
                )
                st.dataframe(geojson_data.drop(columns="geometry").head(100))
                st.stop()

            map_data.geometry = map_data.geometry.representative_point()
            min_x, min_y, max_x, max_y = map_data.total_bounds
            if not np.isfinite([min_x, min_y, max_x, max_y]).all():
                raise ValueError("Batas koordinat geometri tidak valid.")
            if min_x < -180 or max_x > 180 or min_y < -90 or max_y > 90:
                raise ValueError(
                    "Koordinat berada di luar rentang EPSG:4326. "
                    "Periksa CRS dan koordinat pada file GeoJSON."
                )

            m = folium.Map(
                location=[(min_y + max_y) / 2, (min_x + max_x) / 2],
                zoom_start=2,
                control_scale=True,
                tiles="OpenStreetMap",
            )

            for point in map_data.geometry:
                folium.CircleMarker(
                    location=[point.y, point.x],
                    radius=5,
                    color="#145DA0",
                    fill=True,
                    fill_color="#2E8BC0",
                    fill_opacity=0.8,
                    weight=1,
                ).add_to(m)

            m.fit_bounds([[min_y, min_x], [max_y, max_x]], max_zoom=15)
            st_folium(m, width=1000, height=600, key="geojson-map")
        else:
            st.warning("Format file tidak didukung.")

    except Exception as e:
        st.error(f"File GeoJSON/CSV tidak dapat dibaca: {e}")