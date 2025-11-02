import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler

def forecast_svr(df, target_cols, n_lags=10, n_forecast=100, output_file="data/svr_forecast_all_columns.xlsx"):
    """
    Forecasts future values for all specified columns using SVR and saves results to a single Excel file.
    Args:
        df (pd.DataFrame): DataFrame with 'Date' and target columns.
        target_cols (list): List of column names to forecast.
        n_lags (int): Number of lagged features.
        n_forecast (int): Number of future days to predict.
        output_file (str): Path to save combined forecast file.
    Returns:
        pd.DataFrame: Combined forecast DataFrame.
    """
    combined_df = pd.DataFrame()
    for target_col in target_cols:
        values = df[target_col].values.reshape(-1, 1)
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(values)

        def create_lagged_features(series, n_lags):
            X, y = [], []
            for i in range(n_lags, len(series)):
                X.append(series[i-n_lags:i, 0])
                y.append(series[i, 0])
            return np.array(X), np.array(y)

        X, y = create_lagged_features(scaled, n_lags)
        svr = SVR(C=100, gamma=0.1)
        svr.fit(X, y)

        last_window = scaled[-n_lags:].flatten()
        future_preds = []
        # n_forecast = n_forecast*96
        for _ in range(n_forecast):
            pred = svr.predict(last_window.reshape(1, -1))[0]
            future_preds.append(pred)
            last_window = np.roll(last_window, -1)
            last_window[-1] = pred

        future_preds_inv = scaler.inverse_transform(np.array(future_preds).reshape(-1, 1)).flatten()
        last_time = df['Date'].iloc[-1]
        interval = df['Date'].diff().mode()[0]
        future_times = [last_time + interval * (i+1) for i in range(n_forecast)]

        if combined_df.empty:
            combined_df['Date'] = future_times
        combined_df[f'Forecasted {target_col}'] = future_preds_inv

        # print(f"Forecast for {target_col} completed.")

    # combined_df.to_excel(output_file, index=False)
    # print(f"All forecasts saved to {output_file}")
    return combined_df