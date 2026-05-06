import streamlit as st
import requests
import pandas as pd
from io import StringIO
import json
import geopandas as gpd
import os
import plotly.express as px

STATISTIKAAMETI_API_URL = "https://andmed.stat.ee/api/v1/et/stat/RV032"

JSON_PAYLOAD_STR = """
{
  "query": [
    {"code": "Aasta", "selection": {"filter": "item", "values": ["2014","2015","2016","2017","2018","2019","2020","2021","2022","2023"]}},
    {"code": "Maakond", "selection": {"filter": "item", "values": ["39","44","49","51","57","59","65","67","70","74","78","82","84","86","37"]}},
    {"code": "Sugu", "selection": {"filter": "item", "values": ["2","3"]}}
  ],
  "response": {"format": "csv"}
}
"""

@st.cache_data
def import_data():
    parsed_payload = json.loads(JSON_PAYLOAD_STR)
    response = requests.post(STATISTIKAAMETI_API_URL, json=parsed_payload)
    text = response.content.decode('utf-8-sig')
    return pd.read_csv(StringIO(text))

@st.cache_data
def import_geojson():
    url = "https://gist.githubusercontent.com/TereKruut/f950ce9732b7a20f2c5f2dad27a63100/raw/bf4775d8b546fe5cd8fc68b75986a254a40d3990/gistfile1.txt"
    response = requests.get(url)
    return gpd.read_file(StringIO(response.text))

st.title("Loomulik iive maakonniti")

df = import_data()
gdf = import_geojson()

merged = gdf.merge(df, left_on='MNIMI', right_on='Maakond')
merged["Loomulik iive"] = merged["Mehed Loomulik iive"] + merged["Naised Loomulik iive"]

aasta = st.sidebar.selectbox("Vali aasta", sorted(merged["Aasta"].unique(), reverse=True))

aasta_data = merged[merged["Aasta"] == aasta]

fig = px.choropleth_map(
    aasta_data,
    geojson=aasta_data.geometry,
    locations=aasta_data.index,
    color='Loomulik iive',
    color_continuous_scale='RdYlGn',
    map_style="carto-positron",
    center={"lat": 58.7, "lon": 25.0},
    zoom=6,
    hover_name='MNIMI',
    title=f'Loomulik iive maakonniti aastal {aasta}'
)
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

col_left, col_right = st.columns([1, 3])

with col_left:
    maakond = st.selectbox("Vali maakond", sorted(merged['MNIMI'].unique()))

with col_right:
    maakond_data = merged[merged['MNIMI'] == maakond].sort_values('Aasta')
    fig2 = px.line(maakond_data, x='Aasta', y='Loomulik iive', title=f'{maakond} trend')
    st.plotly_chart(fig2, use_container_width=True)

col1, col2, col3 = st.columns(3)
parim = aasta_data.loc[aasta_data['Loomulik iive'].idxmax(), 'MNIMI']
halvim = aasta_data.loc[aasta_data['Loomulik iive'].idxmin(), 'MNIMI']
kokku = int(aasta_data['Loomulik iive'].sum())

col1.markdown(f"**Parim maakond**\n\n{parim}")
col2.markdown(f"**Halvim maakond**\n\n{halvim}")
col3.markdown(f"**Kokku Eestis**\n\n{kokku}")



