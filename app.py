from app_pages.multi_page import MultiPage
import streamlit as st
from app_pages.batteryFailurePrediction import dashboard_body
from app_pages.batteryPerformanceDashboard import dashboard_body_visuals

# Create the multi-page Streamlit application
app = MultiPage(app_name="EV Battery Health & Degradation Prediction App")
# Register the Dashboard page and its body function.
app.add_page("Main Prediction App", dashboard_body)
app.add_page("EV Battery dashboard", dashboard_body_visuals)
# Start the Streamlit application.
app.run()
