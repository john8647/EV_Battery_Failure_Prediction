import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


ReadingTableNormalised = pd.read_csv(
    'ReadingTable_cleaned_normalised.csv')
ReadingTableNormalised.head()


def add_soh_threshold_bands(*args, **kwargs):
    """Custom plotting function mapped across every facet in Seaborn to render

    State of Health threshold regions.
    """
    # 1. Normal Zone (> 0.8) - Subtle Green
    plt.axhspan(0.8, 1.0, color='green', alpha=0.08, label='Normal (>80%)')

    # 2. Accelerated Zone (0.7 to 0.8) - Subtle Orange/Yellow
    plt.axhspan(
        0.7, 0.8, color='orange', alpha=0.12, label='Accelerated (70-80%)'
    )

    # 3. Critical Zone (< 0.7) - Subtle Red
    plt.axhspan(0.0, 0.7, color='red', alpha=0.08, label='Critical (<70%)')

    # 4. Optional: Draw specific dashed boundary lines
    plt.axhline(0.8, color='orange', linestyle='--', linewidth=1, alpha=0.7)
    plt.axhline(0.7, color='red', linestyle='--', linewidth=1, alpha=0.7)


def dashboard_body_visuals():
    st.header("🔋 EV Battery Dashboard")

    st.markdown(
        """
    This **EV Battery Health Estimation** demo illustrates how machine learning pipelines 
    infer **State of Health ($\text{SoH}$)** directly from live operational metrics.
    """
    )
    # st.write("This sample of 6 randomly selected batteries illustrates degradation trajectories across our 4 core predictive features. The horizontal reference bands indicate health thresholds where accelerated wear and operational failure risk increase.")

    # 1. Filter sample battery IDs
    sample_battery_ids = [
        'BATT_00808',
        'BATT_00900',
        'BATT_01571',
        'BATT_01211',
        'BATT_01833',
        'BATT_02077'
    ]
    df_sample = ReadingTableNormalised[
        ReadingTableNormalised['battery_id'].isin(sample_battery_ids)
    ].copy()

    # 2. Melt normalized features into long format
    features_norm = [
        'cycle_count_norm',
        'total_energy_throughput_kwh_norm',
        'internal_resistance_mohm_norm',
        'state_of_health_pct_norm',
    ]

    df_long = pd.melt(
        df_sample,
        id_vars=['battery_id', 'battery_age_days'],
        value_vars=features_norm,
        var_name='Metric',
        value_name='Normalized_Value',
    )

    # 3. Initialize FacetGrid layout
    g = sns.FacetGrid(
        df_long, col='battery_id', col_wrap=3, height=3.5, aspect=1.3,
        sharex=False
    )

    # Map threshold bands onto every subplot
    g.map(add_soh_threshold_bands)

    # 4. Map the multi-line trajectories on top of the shaded background
    g.map_dataframe(
        sns.lineplot,
        x='battery_age_days',
        y='Normalized_Value',
        hue='Metric',
        linewidth=2,
    )

    # 5. Styling and Legends
    g.add_legend(title='Normalized Metric')
    g.set_axis_labels('Battery Age (Days)', 'Normalized Score (0 - 1)')
    g.figure.subplots_adjust(top=0.9)
    g.figure.suptitle(
        'Battery Degradation Trajectories with SoH Threshold Zones',
        fontsize=14,
        fontweight='bold',
    )
    st.pyplot(g.figure)

    # 1. Define custom color palette for chemistries
    chemistry_colors = {
        'LMO': '#1f77b4',
        'LFP': '#2ca02c',
        'NMC': '#9467bd',
        'NCA': '#d62728',
    }

    # 2. Initialize figure canvas
    fig = plt.figure(figsize=(9, 6))

    # 3. Layer 1: Scatter plot colored by chemistry
    ax = sns.scatterplot(
        data=ReadingTableNormalised,
        x='internal_resistance_mohm_norm',
        y='state_of_health_pct_norm',
        hue='chemistry',
        palette=chemistry_colors,
        alpha=0.6,
        s=30,
    )

    # 4. Layer 2: Overall linear trendline across all points
    sns.regplot(
        data=ReadingTableNormalised,
        x='internal_resistance_mohm_norm',
        y='state_of_health_pct_norm',
        scatter=False,
        color='black',
        line_kws={
            'linestyle': '--',
            'linewidth': 2,
            'label': 'Overall Trend',
        },
        ax=ax,
    )
    # st.write("Battery degradation trajectories across core model features, grouped by chemistry. Different chemical compounds react uniquely to operational stress, but all share a consistent overall wear trajectory over time."
    #         "The EV Battery Health Estimation demo illustrates how a model can use the metric it has seen to predict a SoH representitive of the inputs being measured."
    #         "The Risk Factor and Remaining Cycles can now be illustrate at any point without the EV being taken for a service so long as those core features are obtained from the BMS.")
    st.info(
        '💡 **Real-time Remote Diagnostics:** Risk factors and Remaining Useful Life (RUL) '
        'can now be evaluated instantly without physical vehicle servicing, provided key features '
        'are streamed directly from the onboard **Battery Management System (BMS)**.'
    )

    st.caption(
        'Battery degradation trajectories across core model features, grouped by chemistry. '
        'While different chemical compounds react uniquely to operational stress, '
        'all follow a consistent wear pattern over time.'
    )
    # 5. Styling and Labels
    plt.title(
        'State of Health vs. Internal Resistance by Chemistry',
        fontsize=13,
        fontweight='bold',
        pad=12,
    )
    plt.xlabel('Normalized Internal Resistance (0 - 1)', fontsize=10)
    plt.ylabel('Normalized State of Health (0 - 1)', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.5)

    # Restrict y-axis to only show values above 0
    plt.ylim(bottom=0)

    # Ensure legend displays cleanly
    plt.legend(title='Chemistry / Trend',
               bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    st.pyplot(fig)
