import base64
import json
import os
import re
import time
import uuid
from io import BytesIO
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from utils.processor import *

def main():
    if "button_id" not in st.session_state:
        st.session_state["button_id"] = ""
    if "color_to_label" not in st.session_state:
        st.session_state["color_to_label"] = {}
    latitude = st.number_input("Latitude:", -90.0, 90.0, 30.71979998667062 , step=1e-7, format="%.7f", key="latitude")
    longitude = st.number_input("Longitude:", -180.0, 180.0, 76.72142742674824, step=1e-7, format="%.7f", key="longitude")
    image_path,depth_path,heading_path = process_location(latitude,longitude)
    col1, col2 = st.columns(2)
    col1.image(Image.open(depth_path))
    col2.image(Image.open(heading_path))
    PAGES = {
        "Annotator": full_app,
    }
    page = st.sidebar.selectbox("Page:", options=list(PAGES.keys()))
    PAGES[page](image_path,depth_path,heading_path)




def full_app(image_path,depth_path,heading_path):
    st.sidebar.header("Configuration")
    st.markdown(
        """
    asdf
    """
    )
    #run only onc
    
    

    drawing_mode = st.sidebar.selectbox(
        "Drawing tool:",
        ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
    )
    stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
    if drawing_mode == "point":
        point_display_radius = st.sidebar.slider("Point display radius: ", 1, 25, 3)
    stroke_color = st.sidebar.color_picker("Stroke color hex: ")
    realtime_update = st.sidebar.checkbox("Update in realtime", True)
    # Create a canvas component
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        # background_image=Image.open(bg_image) if bg_image else None,
        background_image=Image.open(image_path),
        update_streamlit=realtime_update,
        height=256,
        width = 512,
        drawing_mode=drawing_mode,
        point_display_radius=point_display_radius if drawing_mode == "point" else 0,
        display_toolbar=st.sidebar.checkbox("Display toolbar", True),
        key="full_app",
    )
    df = pd.DataFrame()
    if canvas_result.json_data is not None:
        objects = pd.json_normalize(canvas_result.json_data["objects"])
        for col in objects.select_dtypes(include=["object"]).columns:
            objects[col] = objects[col].astype("str")
        st.dataframe(objects)
        df = objects
        df.to_csv('pandas.csv')

if __name__ == "__main__":
    st.set_page_config(
        page_title="Streamlit Annotator", page_icon=":pencil2:"
    )
    st.title("Annotator")
    st.sidebar.subheader("Configuration")
    main()