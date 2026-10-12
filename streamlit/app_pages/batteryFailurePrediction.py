import streamlit as st
import pandas as pd
import joblib


def classify_soh_status(predicted_soh: float) -> tuple[str, str]:
    """Maps a predicted State of Health percentage (SoH) to its corresponding

    Failure Risk Label and Degradation Category based on custom quantile
    thresholds.

    Parameters:
        predicted_soh (float): Predicted State of Health percentage.

    Returns:
        tuple[str, str]: (failure_risk_label, degradation_category)
    """

    # 1. Determine Failure Risk Label
    if predicted_soh >= 92.78:
        failure_risk_label = 'Low'
    elif predicted_soh >= 85.64:
        failure_risk_label = 'Medium/Low'
    elif predicted_soh >= 81.5175:
        failure_risk_label = 'Medium'
    elif predicted_soh >= 77.77:
        failure_risk_label = 'Medium/High'
    else:
        failure_risk_label = 'High'

    # 2. Determine Degradation Category
    if predicted_soh >= 91.65:
        degradation_category = 'Normal'
    elif predicted_soh >= 79.92:
        degradation_category = 'Accelerated/Normal'
    elif predicted_soh >= 74.81:
        degradation_category = 'Accelerated'
    elif predicted_soh >= 68.12:
        degradation_category = 'Accelerated/Critical'
    else:
        degradation_category = 'Critical'

    return failure_risk_label, degradation_category


def calculate_rul_heuristic(
    predicted_soh: float, current_cycles: int, target_soh: float = 70.0
) -> int:
    """Calculates remaining cycles using a linear degradation rate."""
    if predicted_soh <= target_soh:
        return 0  # Already reached or passed End of Life

    health_lost = 100.0 - predicted_soh
    if health_lost <= 0 or current_cycles <= 0:
        return 5000  # Default max estimate for brand-new battery

    wear_rate = health_lost / current_cycles
    remaining_soh_margin = predicted_soh - target_soh

    remaining_cycles = remaining_soh_margin / wear_rate
    return int(max(0, remaining_cycles))


# Load trained model once
@st.cache_resource
def load_model():
    return joblib.load("rf_model.pkl")


model = load_model()


def dashboard_body():
    st.header("🔋 EV Battery Health Estimation")

    st.write("Provide battery details below to estimate State of Health (SoH), "
             "remaining cycles (RUL), and degradation risk.")

    # --- Dropdowns ---
    manufacturer = st.selectbox(
        "Manufacturer",
        ["StormCell", "VoltaCore", "IonFlux",
            "Amperion", "NexCell", "PowerGrid Batteries"]
    )

    vehicle_model = st.selectbox(
        "Vehicle Model",
        ["Crossover-X2", "Sedan-E1", "Van-E4", "Sport-E9",
         "Hatch-E3", "SUV-E5", "Pickup-E7", "Compact-E1"]
    )

    climate_zone = st.selectbox(
        "Climate Zone",
        ["cold", "temperate", "tropical_humid", "mixed", "hot_arid"]
    )

    chemistry = st.selectbox(
        "Chemistry",
        ["LMO", "LFP", "NMC", "NCA"]
    )

    # --- Numeric Inputs ---
    pack_capacity_kwh = st.slider(
        "Pack Capacity (kWh)",
        min_value=40,
        max_value=100,
        value=75
    )

    internal_resistance_mohm = st.slider(
        "Internal Resistance (mΩ)",
        min_value=15,
        max_value=130,
        value=24
    )

    total_energy_throughput_kwh = st.slider(
        "Total Energy Throughput (kWh)",
        min_value=0,
        max_value=400000,
        value=20000,
        step=1000
    )

    cycle_count = st.slider(
        "Cycle Count",
        min_value=0,
        max_value=5000,
        value=36
    )

    # --- Manufacture Date → battery_age_days ---
    manufacture_date = st.date_input(
        "Manufacture Date (after 2015)",
        min_value=pd.to_datetime("2015-01-01")
    )

    today = pd.Timestamp.today()
    battery_age_days = (today - pd.to_datetime(manufacture_date)).days

    # --- Prediction Button ---
    if st.button("Predict Battery Health"):
        # Build model input row
        row = pd.DataFrame([{
            "battery_age_days": battery_age_days,
            "chemistry": chemistry,
            "internal_resistance_mohm": internal_resistance_mohm,
            "total_energy_throughput_kwh": total_energy_throughput_kwh,
            "cycle_count": cycle_count
        }])

        # Parked feature of the battery
        # "manufacturer": manufacturer,
        # "vehicle_model": vehicle_model,
        # "pack_capacity_kwh": pack_capacity_kwh,
        # "climate_zone": climate_zone,
        # Note:
        # The additional fields (manufacturer, vehicle model, pack capacity, climate zone) are included for record‑keeping and future analytics.
        # Our current SoH model does not use these features, so they do not influence the prediction.
        # They are stored only for context — for example, to analyse how performance degradation varies across manufacturers, climates, or vehicle platforms over time, or to generate a battery‑health certificate or historical trend graph.

        # 1. Predict SoH
        predicted_soh = float(model.predict(row)[0])

        # 2. Compute RUL
        rul = calculate_rul_heuristic(predicted_soh, cycle_count)

        # 3. Classify risk + degradation
        risk, category = classify_soh_status(predicted_soh)

        # --- Output (same style as repair cost example) ---
        st.success(
            f"**Predicted SoH:** {predicted_soh:.2f}%\n\n"
            f"**Failure Risk:** {risk}\n\n"
            f"**Degradation Category:** {category}\n\n"
            f"**Estimated Remaining Cycles (RUL):** {rul:,}"
        )
