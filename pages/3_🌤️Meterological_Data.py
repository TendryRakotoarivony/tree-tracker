import streamlit as st
import datetime
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
import matplotlib.pyplot as plt

pd.set_option("display.precision", 4)
st.set_page_config(
    layout="wide",
    page_title="Tree Tracker | Meteorological Data",
    page_icon="static/bondy-logo.png",
)

st.markdown(
    """
<style>
div[data-testid="metric-container"] {
   background-color: #F0F2F6;
   border: 1px solid #F0F2F6;
   height: 125px;
   padding: 5% 5% 5% 10%;
   border-radius: 10px;
   font-weight:500px;
   color: black;
   overflow-wrap: break-word;

}

/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: black;
   font-size: 20px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.header("🌤️ Meterological Data")


def get_parcel_list(df):
    parcel_list = []
    for index, row in df.iterrows():
        if row["plotName"] == None:
            if row["name"] == None:
                print("none")
            if len(row["name"]) == 0:
                parcelFolder = row["folders"].split("; ")
                n = len(parcelFolder)
                if n > 1:
                    n = -n + 1
                    parcelName = ", ".join(parcelFolder[n:])
                else:
                    parcelName = parcelFolder

            else:
                parcelName = row["name"]
        else:
            parcelName = row["plotName"]

        parcelName = str(index) + " | " + parcelName
        parcel_list.append(parcelName)

    return parcel_list


# Air Temperature
# https://drive.google.com/file/d/1v6tIuDkQCA46dkDpH2txqVXUI5rjrizC/view?usp=sharing
fname_temp = 'data/meteor/ERA5_Land_2020_2022_t2m.grib'

# Evaporation
# https://drive.google.com/file/d/1SqzuiL2lioFU1KLmGLf8Mw1VtVMWPeFS/view?usp=sharing
fname_evat = 'data/meteor/ERA5_Land_2020_2022_te.grib'

# Precipitation
# https://drive.google.com/file/d/1KljDY9fgopB9y-TwcF9z9ynJNUnJKJ2W/view?usp=sharing
fname_prec = 'data/meteor/ERA5_Land_2020_2022_tp.grib'

#The data has subsurface and surface data as well as edition conflicts:
#The below statement will give access to temperature (t2m) and total precipitation (tp)
ds_temp = xr.open_dataset(fname_temp, engine="cfgrib")
ds_prec = xr.open_dataset(fname_prec, engine="cfgrib")
ds_evap = xr.open_dataset(fname_evat, engine="cfgrib")

#opening the geojson file
path_Parcels = 'data/parcel/BondyPlantedParcels.geojson'
gdf_BondyPlantedParcels = gpd.read_file(path_Parcels)

selected_region = st.sidebar.selectbox(
    "🌍 Regions",
    gdf_BondyPlantedParcels["regionName"].unique(),
    help='Select region available from GeoJSON file')

rslt_df = gdf_BondyPlantedParcels[gdf_BondyPlantedParcels["regionName"].isin(
    [selected_region])]
list_parcels = get_parcel_list(rslt_df)

# Parcels
selected_parcel = st.sidebar.selectbox("📍 Parcels", list_parcels)

# Clean up the parcel information
parcel_ID = int(selected_parcel.split(" | ")[0])
parcel_name = selected_parcel.split(" | ")[1]

parcel_polygon = gdf_BondyPlantedParcels.iloc[[parcel_ID]].copy()
#projecting the polygon
parcel_polygon = parcel_polygon.to_crs(4087)
#getting the point
parcel_point = parcel_polygon.centroid
#back to degrees
parcel_point = parcel_point.to_crs(crs=4326)

# Get the coordinates
lat = parcel_point.y.values
lon = parcel_point.x.values

y_grid = int(0.2 * np.round(lat[0] / 0.2) * 10) / 10
x_grid = int(0.2 * np.round(lon[0] / 0.2) * 10) / 10

col_a, col_b, col_c = st.columns([3, 1, 1])
col_a.subheader(f'{selected_region} - {parcel_name} ')
col_a.write(f'📍 Coordinates: ({y_grid}, {x_grid})')

#Subset on location
data_temp = ds_temp.sel(longitude=x_grid, latitude=y_grid, method='nearest')
data_prec = ds_prec.sel(longitude=x_grid, latitude=y_grid, method='nearest')
data_evap = ds_evap.sel(longitude=x_grid, latitude=y_grid, method='nearest')

#Subset on time
slice_start = str(col_b.date_input('📅 From', value=datetime.date(
    2020, 8, 1))) + "T00"  #"2020-08-01T00"
slice_end = str(col_c.date_input('📅 To')) + "T00"  #"2022-12-31T00"

data_temp = data_temp.sel(time=slice(slice_start, slice_end))
data_prec = data_prec.sel(time=slice(slice_start, slice_end))
data_evap = data_evap.sel(time=slice(slice_start, slice_end))

df_prec = data_prec.to_dataframe()
df_evap = data_evap.to_dataframe()

# Convert to deg C
air_temp = data_temp.t2m - 273.15

df_air_temp = air_temp.to_dataframe()
df_air_temp = df_air_temp.reset_index()
df_air_temp = df_air_temp.set_index(df_air_temp.valid_time)

df_prec = df_prec.reset_index()
df_prec = df_prec.set_index(df_air_temp['valid_time'])

df_evap = df_evap.reset_index()
df_evap = df_evap.set_index(df_air_temp['valid_time'])

selected_parameter = st.sidebar.selectbox(
    '🌡️ Parameter', ['Air Temperature', 'Precipitation', 'Evapotranspiration'])

# Group by date to get the aggregated values
gb_air_temp = df_air_temp.groupby([df_air_temp['valid_time'].dt.date]).agg({
    'latitude':
    'mean',
    'longitude':
    'mean',
    't2m':
    'max'
})
gb_prec = df_prec.groupby([df_prec['valid_time'].dt.date]).agg({
    'latitude': 'mean',
    'longitude': 'mean',
    'tp': 'sum'
})
gb_evap = df_evap.groupby([df_evap['valid_time'].dt.date]).agg({
    'latitude': 'mean',
    'longitude': 'mean',
    'e': 'sum'
})

col_1, col_2, col_3 = st.columns(3)
col_1.metric("🌬️ Air Temperature (°C)",
             str(round(gb_air_temp['t2m'].mean(), 2)),
             delta="",
             delta_color="normal")
col_2.metric("🌧️ Precipitation (mm)",
             str(round(gb_prec['tp'].mean(), 4)),
             delta="",
             delta_color="normal")
col_3.metric("🌪️ Evapotranspiration (mm/unit time)",
             str(round(gb_evap['e'].mean(), 4)),
             delta="",
             delta_color="normal")

if selected_parameter == 'Air Temperature':
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.plot(gb_air_temp['t2m'], color='orange')
    plt.ylabel('Air Temperature', fontsize=16)
    plt.grid()
    st.plotly_chart(fig, use_container_width=True)
    #st.dataframe(gb_air_temp.describe())

if selected_parameter == 'Precipitation':
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.plot(gb_prec['tp'], color='blue')
    plt.ylabel('Precipitation', fontsize=16)
    plt.grid()
    st.plotly_chart(fig, use_container_width=True)
    #st.dataframe(gb_prec.describe())

if selected_parameter == 'Evapotranspiration':
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.plot(gb_evap['e'], color='black')
    plt.ylabel('Evapotranspiration', fontsize=16)
    plt.grid()
    st.plotly_chart(fig, use_container_width=True)
    #st.dataframe(gb_evap.describe())
