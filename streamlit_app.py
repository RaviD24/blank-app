import streamlit as st
import pandas as pd
import numpy as np

from forecast_future_svr import forecast_svr

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
    options=[5, 7, 10, 14, 21, 28, 30, 60, 90, 180, 365],
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

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload an Excel file to begin.")
