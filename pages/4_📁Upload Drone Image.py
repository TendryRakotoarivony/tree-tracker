from typing import Any, Literal

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit.delta_generator import DeltaGenerator

from tree_tracker import util

st.set_page_config(
    layout="wide",
    page_title="Tree Tracker | Upload Drone Image",
    page_icon="static/bondy-logo.png",
)

st.header("📁 Upload Drone Image")
col2: DeltaGenerator = st.columns([1, 3, 1])[1]

with col2.form("upload_form"):
    drone_image: list[UploadedFile] | None = st.file_uploader(
        "Select Drone Image:", type=["png", "jpg"], accept_multiple_files=True
    )

    # Every form must have a submit button.
    submitted: bool = st.form_submit_button("Upload")
    if submitted:
        if drone_image is not None:
            status: list[Any] = []
            for image in drone_image:
                with st.spinner("Uploading..."):
                    _image: str | Literal[False] | None = util.save_upload(image, "drone")
                    if _image:
                        status.append(util.upload_data(_image, "drone"))

            if all(status):
                st.success("Image uploaded successfully")
            else:
                st.error("Image upload failed")
        else:
            st.error("No image selected")
