import streamlit as st
import pandas as pd
import numpy as np

from forecast_future_svr import forecast_svr
from calculate_dew_point import dew_point_risk_analysis, detect_zone_columns

# --- Streamlit App UI ---

st.set_page_config(page_title="SVR Forecast Demo", layout="wide")

st.title("SVR Forecasting Demo App")

st.markdown("""
This demo app allows you to:
1. Upload an Excel file containing sensor readings  
2. Select a forecast period  
3. Generate SVR-based forecasts
""")

uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

forecast_days = st.selectbox(
    "Select forecast period (in days):",
    options=[5, 7, 10, 14, 21, 28, 30, 60, 90, 180, 365, 730, 1095],
    index=1
)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        st.subheader("Uploaded Data Preview")
        st.dataframe(df.head())

        target_columns = [
            'Producation North AHU-Return Air Temperature (°C)',
            'Producation North AHU-Return Air Humidity (%)',
            'Production Middle AHU-Return Air Temperature (°C)',
            'Production Middle AHU-Return Air Humidity (%)',
            'Attic Area temperature (°C)',
            'Attic Area Relative Humidity (%)'
        ]
        forecast_period = int(forecast_days * 96)
        with st.spinner("Running SVR forecast..."):
            forecast_df = forecast_svr(df, target_columns, 10, forecast_period)
        
        st.success("Forecast complete!")
        st.subheader("Forecast Results")
        st.dataframe(forecast_df.head())

        csv = forecast_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Forecast (CSV)",
            data=csv,
            file_name="forecast_output.csv",
            mime="text/csv"
        )

        # --- Combine DataFrames ---
        forecast_df["Source"] = "Forecast"
        combined_df = pd.concat([df, forecast_df])
        # combined_df = combined_df.reset_index().rename(columns={"index": "Date"})

        # combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]

        # --- Dew Point Risk Step ---
        st.markdown("---")
        st.subheader("Dew Point Condensation Risk Analysis")

        zones = detect_zone_columns(combined_df)
        if not zones:
            st.error("Could not detect zone temperature/humidity columns automatically.")
        else:
            st.markdown("Detected zones:")
            st.json(zones)

            st.markdown("Set dew point thresholds for each zone (°C):")
            threshold_inputs = {}
            cols = st.columns(len(zones))
            for i, zone in enumerate(zones.keys()):
                threshold_inputs[zone] = cols[i].number_input(
                    f"{zone} Threshold (°C)", value=5.0
                )
            
            # col1, col2, col3 = st.columns(3)
            # with col1:
            #     th_north = st.number_input("Production North Threshold (°C)", value=5.0)
            # with col2:
            #     th_middle = st.number_input("Production Middle Threshold (°C)", value=3.0)
            # with col3:
            #     th_attic = st.number_input("Attic Area Threshold (°C)", value=2.5)

            # thresholds = {
            #     "North": th_north,
            #     "Middle": th_middle,
            #     "Attic": th_attic
            # }

            if st.button("Calculate Dew Point Risk"):
                with st.spinner("Analyzing dew point risks..."):
                    final_df, risk_zones = dew_point_risk_analysis(combined_df.copy(), zones, threshold_inputs)

                st.success("Dew Point Risk Analysis Complete")
                st.subheader("Dew Point vs Temperature (All Zones)")
                for zone, zone_df in risk_zones.items():
                    st.markdown(f"### {zone}")
                    if zone_df.empty:
                        st.info("No condensation risk detected.")
                    else:
                        cols_to_show = [
                            c for c in zone_df.columns
                            if any(k in c.lower() for k in ["temp", "dew", "humid", "date"])
                        ]
                        st.dataframe(zone_df[cols_to_show].tail(50))
                        chart_cols = [
                            c for c in zone_df.columns if "temp" in c.lower() or "dew" in c.lower()
                        ]
                        zone_df = zone_df.set_index("Date")
                        # st.line_chart(zone_df[chart_cols])

                # st.markdown("---")
                # st.subheader("Final Combined Data (with Dew Point & Risk Columns)")
                # st.dataframe(final_df.tail(50))

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload an Excel file to begin.")
