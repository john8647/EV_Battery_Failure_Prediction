from app_pages.multi_page import MultiPage
import streamlit as st
from app_pages.batteryFailurePrediction import dashboard_body
import pathlib
import requests
import joblib


MODEL_PATH = pathlib.Path("rf_model.pkl")
MODEL_URL = "https://huggingface.co/CodeInstitute/herokuapp_rf_model/resolve/main/rf_model.pkl"


def load_model():
    # Download once if missing
    if not MODEL_PATH.exists():
        print("Downloading model from Hugging Face...")
        with requests.get(MODEL_URL, stream=True) as r:
            r.raise_for_status()
            with open(MODEL_PATH, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

    # Load the model
    return joblib.load(MODEL_PATH)


model = load_model()

# Create the multi-page Streamlit application
app = MultiPage(app_name="EV Battery Health & Degradation Prediction App")
# Register the Dashboard page and its body function.
app.add_page("Main Prediction App", dashboard_body)
# Start the Streamlit application.
app.run()
