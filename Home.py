import streamlit as st
from PIL import Image


st.set_page_config(
    layout='wide',
    page_title="Home",
    page_icon="static/bondy-logo.png",
)

st.write("# Welcome to Bôndy Dashboard! 👋")
col1, col2 = st.columns([3,1])

col1.subheader("Problem statement")
col1.markdown("""
- Madagascar is the 5️⃣th poorest country globally and faces terrific consequences due to climate change.
- With multiple parties promising to provide reforestation services comes the fact that planting trees is simple, but making sure they will grow is more complex. 
- For the moment, Bôndy monitors trees physically, but this is not a scalable model. 
- Together with the Omdena, a solution to combine satellite and drone imagery, meterological data, and Machine Learning a dashboard was developed to monitor plants.

- Repo available at: [DagsHub](https://dagshub.com/Omdena/Bondy) 
""")

st.sidebar.info("Powered by Omdena")

logo = Image.open('static/bondy-logo.png')
col2.image(logo)

madagascar_map = Image.open('static/madagascar-flag.png')
col2.image(madagascar_map)

col1.info('''
- Team members who made this possible:
    - Gijs van den Dool
    - Joan V
    - Duplex
    - Lu Htoo Kyaw
    - Jeremy Simon
    - Md. Safirur Rashid
    - Fred Mensah
    - Sanjiv Chemudupati
    - Aldrin L
    - Deepali Bidwai (Product Owner)''')
