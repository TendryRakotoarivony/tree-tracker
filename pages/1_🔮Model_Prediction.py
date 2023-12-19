import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import onnxruntime  # type: ignore
import streamlit as st
from skimage.measure import label, regionprops  # type: ignore

from tree_tracker.util import download_data

st.set_page_config(
    layout="wide",
    page_title="Tree Tracker | Model Prediction",
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


def extract_bboxes(image, mask, circle=False):
    bboxes = []
    props = regionprops(label(mask))
    for prop in props:
        x1 = prop.bbox[1]
        y1 = prop.bbox[0]
        x2 = prop.bbox[3]
        y2 = prop.bbox[2]

        bboxes.append([x1, y1, x2, y2])

    drawed_image = image.copy()

    for bbox in bboxes:
        x1, y1, x2, y2 = bbox
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        radius = (x2 - x1) // 2 if (x2 - x1) > (y2 - y1) else (y2 - y1) // 2

        if not circle:
            drawed_image = cv2.rectangle(
                drawed_image, (x1, y1), (x2, y2), color=(255, 0, 0), thickness=10
            )
        else:
            drawed_image = cv2.circle(
                drawed_image,
                (center_x, center_y),
                color=(255, 0, 0),
                radius=radius,
                thickness=10,
            )

    return bboxes, drawed_image


def overlay_mask(image, mask, color=(255, 0, 0), alpha=0.4):
    seg = label(mask)
    contours, _ = cv2.findContours(seg, cv2.RETR_FLOODFILL, cv2.CHAIN_APPROX_NONE)

    drawed_image = image.copy()
    canvas = np.ones_like(image, np.uint8)

    for i, c in enumerate(contours):
        cv2.drawContours(canvas, [c], -1, color, thickness=cv2.FILLED)
        cv2.drawContours(drawed_image, [c], -1, color, thickness=10)

    drawed_image = cv2.addWeighted(canvas, alpha, drawed_image, 1 - alpha, 0)

    return len(np.unique(seg)) - 1, drawed_image


st.header("🔮 Model Prediction")

model_col, btn_col, file_col = st.columns([3, 1, 3])

# Download data
download_data("model")
download_data("drone")

# Model and image path
model_path = "data/model"
image_path = "data/drone"

# Model and image selection widgets
selected_model = model_col.selectbox(
    "Choose model file",
    [image for image in os.listdir(model_path)],
)
selected_image = file_col.selectbox(
    "Available images",
    [model for model in os.listdir(image_path)],
)

# Selected model and image
selected_model = os.path.join(model_path, selected_model)
selected_image = os.path.join(image_path, selected_image)

original_image = cv2.imread(selected_image)
original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

# original_mask = cv2.imread(mask_image, cv2.IMREAD_GRAYSCALE)
IMAGE_SIZE = 416
image = cv2.resize(original_image, (IMAGE_SIZE, IMAGE_SIZE), interpolation=cv2.INTER_AREA)
image = np.transpose(image, (2, 0, 1)).astype(np.float32) / 255.0

# Tuning Parameters
GSD = st.sidebar.number_input(
    "Ground Sampling Distance (m)",
    min_value=0.0,
    max_value=0.005,
    value=0.0013,
    step=1e-6,
    format="%.5f",
    help="Ground Sampling Distance is the distance between \
center points of each sample taken of the ground",
)
tree_size_in_meters = st.sidebar.number_input(
    "Tree size (m)",
    min_value=0.0,
    max_value=99.0,
    value=4.0,
    step=0.1,
    help="Tree size is used to help identify the trees in teh prediction",
)
confidence = st.sidebar.number_input(
    "Confidence Threshold",
    min_value=0.3,
    max_value=0.99,
    value=0.8,
    step=0.01,
    help="Confidence threshold is used to tune the predictions",
)
ort_session = onnxruntime.InferenceSession(selected_model)
ort_inputs = {ort_session.get_inputs()[0].name: image[np.newaxis, ...]}
ort_outs = ort_session.run(None, ort_inputs)
pred_mask = (ort_outs[0] > confidence) * 1.0

pred_mask = cv2.resize(pred_mask[0][0], (4000, 3000), interpolation=cv2.INTER_NEAREST)

pred_mask_type = st.sidebar.radio("Prediction Mask type", ["Bounding Boxes", "Patches"])
if pred_mask_type == "Bounding Boxes":
    bboxes, drawed_image = extract_bboxes(original_image, pred_mask, circle=True)
    patches = len(bboxes)
else:
    patches, drawed_image = overlay_mask(original_image, pred_mask, color=(0, 255, 0), alpha=0.2)

veg_percent = np.count_nonzero(pred_mask > 0.0) / np.prod(pred_mask.shape)

tree_size_in_pixels = tree_size_in_meters / GSD
num_tree = np.count_nonzero(pred_mask > 0.0) // tree_size_in_pixels

if st.sidebar.button("Predict"):
    col_0, col_1, col_2 = st.columns(3)
    col_0.metric("🌳 Patches", patches, delta="", delta_color="normal")
    col_1.metric("🌳 Identified", int(num_tree), delta="", delta_color="normal")
    col_2.metric("🌳 Vegetation %", round(veg_percent, 4), delta="", delta_color="normal")

    show_image = st.sidebar.checkbox("Show image", value=True)
    if show_image:
        with st.spinner("Rendering images..."):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

            ax1.set_title("IMAGE - GROUND TRUTH")
            ax1.imshow(original_image)
            ax1.grid(False)
            ax1.set_axis_off()

            ax2.set_title("IMAGE - PREDICTION")
            ax2.imshow(drawed_image)
            ax2.grid(False)
            ax2.set_axis_off()

            st.pyplot(fig)
