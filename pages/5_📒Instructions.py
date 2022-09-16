import streamlit as st

st.set_page_config(
    layout='wide',
    page_title="Tree Tracker | Instructions",
    page_icon="static/bondy-logo.png",
)

'''
# 📒 Instructions
## 🩺 Vegetation Indices
1. Choose the region from the `Regions` and parcel from the `Parcels` dropdown.
2. The plot of the left shows the boundaries of the all the parcels in the selected region. If the use selectes the `Parcel` option fromteh `Select Map type`, only the selected parcel boundary will be displayed.
3. The plot on the right shows the vegeatation index for the region. Use can choose between `NDVI`, `NDWI` and `MSAVI2` indices. For more information on these indices please refer to the final report.
4. Select the `Year and Month` combination to see the vegetation index plot for that year and month.
4. The plot below these plots shows the variation of the selected index with respect to time.  


## 🌤️ Meterological Data
1. Choose the region from the `Regions` and parcel from the `Parcels` dropdown.
2. Choose between `Air Temperature`, `Precipitation` and `Evapotranspiration` parameters.
3. Select the `From` and `To` dates.
4. Based on the nearest coordinates to selected region and parcel, the parameter chosen is plotted as a time series.

## 🔮 Model Prediction
1. Choose the available models from `models/onnx` folder.
2. Choose available drone images from `data/drone` folder
3. Select the `GSD`, `Tree size` and `Confidence Threshold`
4. User can choose between `Bounding Boxes` and `Patches` for the prediction mask type. Recommended option is `Patches`. 
5. Click on the `Predict` button. The user should be able to see the prediction.

# ➕ How to add new data to the dashboard?

## Planet Data
1. User needs to add `*.tif` data to `data/planet_data/<region_name>` folder . 
2. For example, if he/she wishes to add new `*.tif` files for Andramasina region, the *tif files have to added to the `data/planet_data/Andramasina` folder.


## Meterological Data
1. User needs to add `*.grib` data to `data/meterological_data/` folder.
2. Currently the data is available between January 1, 2020 and May 1,2022.
    - Temperature data is available at `data/meteorological_data/ERA5_Land_2020_2022_t2m.grib`
    - Evapotranspiration data is available at `data/meteorological_data/ERA5_Land_2020_2022_te.grib`
    - Precipitation data is available at `data/meteorological_data/ERA5_Land_2020_2022_tp.grib`

## Drone Image Data
1. User needs to add `data/drone` folder.
2. It is recommended to use `*.jpg` files. However file formats like `*.tif` and `*.png` also work, but with a highly reduced prediction accuracy.

'''
