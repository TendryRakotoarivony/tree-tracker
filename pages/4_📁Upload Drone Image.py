import streamlit as st

import util


st.set_page_config(
    layout='wide',
    page_title="Tree Tracker | Upload Drone Image",
    page_icon="static/bondy-logo.png",
)

st.header("📁 Upload Drone Image")
_, col2, _ = st.columns([1, 3, 1])

with col2.form("upload_form"):
    drone_image = st.file_uploader("Select Drone Image:",
                                   type=["png", "jpg"],
                                   accept_multiple_files=True)

    # Every form must have a submit button.
    submitted = st.form_submit_button("Upload")
    if submitted:
        if drone_image is not None:
            status = []
            for image in drone_image:
                with st.spinner("Uploading..."):
                    image = util.save_upload(image, "drone")
                    status.append(util.upload_data(image, "drone"))

            if all(status):
                st.success("Image uploaded successfully")
            else:
                st.error("Image upload failed")
        else:
            st.error("No image selected")
