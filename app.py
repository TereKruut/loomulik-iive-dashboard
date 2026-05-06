import streamlit as st
import requests
import pandas as pd
from io import StringIO
import json
import geopandas as gpd
import matplotlib.pyplot as plt
import os

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
    url = "https://gist.github.com/TereKruut/f950ce9732b7a20f2c5f2dad27a63100"
    return gpd.read_file(url)

st.title("Loomulik iive maakonniti")

df = import_data()
gdf = import_geojson()

merged = gdf.merge(df, left_on='MNIMI', right_on='Maakond')
merged["Loomulik iive"] = merged["Mehed Loomulik iive"] + merged["Naised Loomulik iive"]

aasta = st.sidebar.selectbox("Vali aasta", sorted(merged["Aasta"].unique(), reverse=True))

aasta_data = merged[merged["Aasta"] == aasta]

fig, ax = plt.subplots(1, 1, figsize=(12, 8))
aasta_data.plot(column='Loomulik iive', ax=ax, legend=True,
                cmap='RdYlGn', legend_kwds={'label': "Loomulik iive"})
plt.title(f'Loomulik iive maakonniti aastal {aasta}')
plt.axis('off')
plt.tight_layout()

st.pyplot(fig)
