import os
import glob
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
from rasterstats import zonal_stats
import geopandas as gpd

st.set_page_config(
    layout="wide",
    page_title="Tree Tracker | Vegetation Indices",
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


def calculate_ndvi(src):
    # Allow division by zero
    np.seterr(divide="ignore", invalid="ignore")

    band_red = src.read(3)
    band_nir = src.read(4)

    return (band_nir.astype(float) - band_red.astype(float)) / (band_nir +
                                                                band_red)


def calculate_ndwi(src):
    # Allow division by zero
    np.seterr(divide="ignore", invalid="ignore")
    band_green = src.read(2)
    band_nir = src.read(4)

    return (band_green.astype(float) - band_nir.astype(float)) / (band_green +
                                                                  band_nir)


def calculate_msavi2(src):
    # Allow division by zero
    np.seterr(divide="ignore", invalid="ignore")
    band_green = src.read(2)
    band_red = src.read(3)
    band_nir = src.read(4)

    # 2∗ir+1
    msavi2_first = 2 * band_nir.astype(float) + 1

    # 8(ir−r)
    msavi2_second = 8 * (band_nir.astype(float) - band_red.astype(float))

    return (msavi2_first -
            np.sqrt(np.square(msavi2_first) - msavi2_second)) / 2


def makeParcelNameList(df):
    parcelNameList = []
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
        parcelNameList.append(parcelName)

    return parcelNameList


def get_parcel_stats(parcel_polygon, selected_index):
    parcel_polygon = parcel_polygon.to_crs(crs=selected_index.crs)
    ndval = 1
    #get the matrix:
    array = selected_index.read(1)
    array = array.astype('float64')
    array[array == ndval] = np.nan

    affine = selected_index.transform

    #get the stats
    zs_parcel_polygon = zonal_stats(parcel_polygon,
                                    array,
                                    affine=affine,
                                    nodata=np.nan,
                                    stats=['min', 'max', 'mean'])

    #bring the stats to the load_data function
    return zs_parcel_polygon


@st.cache
def load_data():
    data_path = r"data/planet"

    # Create a metrics dataframe
    df_metrics = pd.DataFrame(columns=[
        "year",
        "month",
        "region",
        "NDVI_min",
        "NDVI_max",
        "NDVI_average",
        "NDWI_min",
        "NDWI_max",
        "NDWI_average",
        "MSAVI2_min",
        "MSAVI2_max",
        "MSAVI2_average",
    ])
    # Read all the regions
    region_list = ['Andramasina', 'Antolojanahary']
    for region in region_list:
        tif_path = os.path.join(data_path, region)
        file_list = glob.glob(tif_path + "/*clip.tif")

        for file_ in file_list:
            image_file = rasterio.open(file_)
            with image_file as src:
                string_end = "_clip.tif"
                len_string_end = len(string_end)
                len_month = 2
                len_year = 4
                extra = 1

                len_remove = len_string_end + len_month + len_year + extra

                file_path_s1 = file_[-len_remove:-len_string_end]

                split_text = file_path_s1.split("-")

                year = split_text[0]
                month = split_text[1]

                # Calculate NDVI - check if you can change to after the dashboard loads
                ndvi = calculate_ndvi(src)
                min_ndvi = np.nanmin(ndvi)
                max_ndvi = np.nanmax(ndvi)
                avg_ndvi = np.nanmean(ndvi)

                ndwi = calculate_ndwi(src)
                min_ndwi = np.nanmin(ndwi)
                max_ndwi = np.nanmax(ndwi)
                avg_ndwi = np.nanmean(ndwi)

                msavi2 = calculate_msavi2(src)
                min_msavi2 = np.nanmin(msavi2)
                max_msavi2 = np.nanmax(msavi2)
                avg_msavi2 = np.nanmean(msavi2)

                series_list = [
                    year,
                    month,
                    region,
                    min_ndvi,
                    max_ndvi,
                    avg_ndvi,
                    min_ndwi,
                    max_ndwi,
                    avg_ndwi,
                    min_msavi2,
                    max_msavi2,
                    avg_msavi2,
                ]
                # Append calculated metrics to df
                df_tmp = pd.Series(series_list, index=df_metrics.columns)
                length_df = len(df_metrics)
                df_metrics.loc[length_df] = df_tmp
    df_metrics["label"] = (df_metrics["year"].map(str) + "-" +
                           df_metrics["month"].map(str))
    df_metrics = df_metrics.sort_values(by=["year", "month"])
    df_metrics.reset_index(drop=True, inplace=True)
    df_metrics["NDVI_delta"] = df_metrics["NDVI_average"].diff()
    df_metrics["NDWI_delta"] = df_metrics["NDWI_average"].diff()
    df_metrics["MSAVI2_delta"] = df_metrics["MSAVI2_average"].diff()
    df_metrics = df_metrics.replace(np.nan, 0)
    return df_metrics


path_parcels = "data/parcel/BondyPlantedParcels.geojson"
gdf_BondyPlantedParcels = gpd.read_file(path_parcels)

# Regions
selected_region = st.sidebar.selectbox(
    "🌍 Regions",
    gdf_BondyPlantedParcels["regionName"].unique(),
    help='Select region available from GeoJSON file')

rslt_df = gdf_BondyPlantedParcels[gdf_BondyPlantedParcels["regionName"].isin(
    [selected_region])]
list_parcels = makeParcelNameList(rslt_df)

# Parcels
selected_parcel = st.sidebar.selectbox("📍 Parcels", list_parcels)

parcelID = int(selected_parcel.split(" | ")[0])
parcel_name = selected_parcel.split(" | ")[1]

head_col, metric_col, month_year_col = st.columns([5, 2, 2])
vegetation_metric = metric_col.selectbox("🔎 Select a metric to plot",
                                         ["NDVI", "NDWI", "MSAVI2"])
df_metrics = load_data()
#st.dataframe(df_metrics)

month_year = month_year_col.selectbox("📅 Select Month & Year",
                                      df_metrics["label"].unique())
head_col.header("🩺 Vegetation Indices")
with st.spinner("Calculating indices...."):
    st.subheader(f"🇲🇬 Region: {selected_region} | {parcel_name}")
    #st.write("Last Inspected: June 25, 2022")

    delta_NDVI = df_metrics[df_metrics["label"] ==
                            month_year]["NDVI_delta"].values[0]
    delta_NDWI = df_metrics[df_metrics["label"] ==
                            month_year]["NDWI_delta"].values[0]
    delta_MSAVI2 = df_metrics[df_metrics["label"] ==
                              month_year]["MSAVI2_delta"].values[0]

    col_2, col_3, col_4 = st.columns(3)

    # col_2.metric(
    #     "🩺 NDVI",
    #     round(df_metrics[df_metrics["label"] == month_year]["NDVI_average"], 4),
    #     delta=round(delta_NDVI, 4),
    #     delta_color="normal",
    # )
    # col_3.metric(
    #     "🩺 NDWI",
    #     round(df_metrics[df_metrics["label"] == month_year]["NDWI_average"], 4),
    #     delta=round(delta_NDWI, 4),
    #     delta_color="normal",
    # )
    # col_4.metric(
    #     "🩺 MSAVI2",
    #     round(df_metrics[df_metrics["label"] == month_year]["MSAVI2_average"], 4),
    #     delta=round(delta_MSAVI2, 4),
    #     delta_color="normal",
    # )

    st.subheader(f"{vegetation_metric} : By time and region")
    col_5, col_6 = st.columns(2)

    image_file = rasterio.open(
        f"data/planet/{selected_region}/planet_medres_normalized_analytic_{month_year}_clip.tif"
    )

    with image_file as src:
        meta = src.meta.copy()
        # st.write(meta)

        # Calculate metric
        metric_data = {
            "NDVI": calculate_ndvi(src),
            "NDWI": calculate_ndwi(src),
            "MSAVI2": calculate_msavi2(src),
        }

    # Plot the metric values over time
    fig, axes = plt.subplots(figsize=(12, 3))
    plt.fill_between(
        x=df_metrics["label"],
        y1=df_metrics[vegetation_metric + "_min"],
        y2=df_metrics[vegetation_metric + "_max"],
        alpha=0.2,
        color="green",
    )
    plt.plot(df_metrics["label"],
             df_metrics[vegetation_metric + "_average"],
             color="green")
    plt.xticks(rotation=45)
    plt.title(vegetation_metric + " with time")
    plt.axvline(x=month_year, color="black", linestyle=":")
    st.pyplot(fig)

    gdf_BondyPlantedParcels = gdf_BondyPlantedParcels.to_crs("WGS84")

    geodf = gdf_BondyPlantedParcels
    min_x, min_y, max_x, max_y = geodf.iloc[parcelID].geometry.bounds
    lat_new = (min_y + max_y) / 2
    lon_new = (min_x + max_x) / 2

    # st.write(geodf.crs)
    # Displaying the selected metric
    fig, axes = plt.subplots(figsize=(10, 10))
    img = axes.imshow(
        metric_data[vegetation_metric],
        cmap="viridis",
        interpolation='none',
    )
    axes.set(title=vegetation_metric)
    # axes.set_xlim([10, 20])
    # axes.set_ylim([400, 450])
    axes.invert_yaxis()

    # plt.colorbar(img, fraction=0.035, pad=0.025)
    plt.grid(False)
    col_6.pyplot(fig)

    map_selection = st.sidebar.selectbox('Select map area',
                                         ['Region', 'Parcel'])
    geodf = geodf.to_crs(3857)
    fig, ax = plt.subplots(figsize=(10, 10))
    img = show(metric_data[vegetation_metric], cmap='viridis', aspect='auto')
    ax.set(title='Boundary/Boundaries')
    # ax.scatter(x=[30, 40], y=[50, 60], c='r', s=40)
    geodf.plot(edgecolor="red", facecolor="None", linewidth=1, ax=ax)

    if map_selection == 'Region':
        min_x, min_y, max_x, max_y = src.bounds
    else:
        min_x, min_y, max_x, max_y = geodf.iloc[parcelID].geometry.bounds

    ax.set_xlim([min_x, max_x])
    ax.set_ylim([min_y, max_y])
    ax.invert_yaxis()
    ax.grid(False)

    col_5.pyplot(fig)
    #st.write(geodf)
