from app_pages.multi_page import MultiPage
import streamlit as st
from app_pages.batteryFailurePrediction import dashboard_body
import pathlib
import requests
import joblib

MODEL_PATH = pathlib.Path("rf_model.pkl")
# real 300 MB file
MODEL_URL = "https://huggingface.co/CodeInstitute/herokuapp_rf_model/resolve/main/rf_model.pkl"
if not MODEL_PATH.exists():
    # First run on a fresh dyno: download the real model
    with requests.get(MODEL_URL, stream=True) as r:
        r.raise_for_status()
        with open(MODEL_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

model = joblib.load(MODEL_PATH)

# Create the multi-page Streamlit application
app = MultiPage(app_name="EV Battery Health & Degradation Prediction App")
# Register the Dashboard page and its body function.
app.add_page("Main Prediction App", dashboard_body)
# Start the Streamlit application.
app.run()
