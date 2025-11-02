import numpy as np
def calculate_dew_point(temp, humidity):
    a = 17.27
    b = 237.7
    # According to Magnus Formula, this is the default empherical value for a and b
    alpha = ((a * temp) / (b + temp)) + np.log(humidity / 100)
    dew_point = (b * alpha) / (a - alpha)
    return dew_point

def dew_point_risk_analysis(df, zones, thresholds):
    df = df.copy()
    results = {}

    for zone, cols in zones.items():
        temp_col = cols.get("temp")
        hum_col = cols.get("humidity")
        if not temp_col or not hum_col:
            continue

        T = df[temp_col]
        H = df[hum_col]
        dew_point = calculate_dew_point(T, H)

        dp_col = f"Dew Point (°C) - {zone}"
        risk_col = f"At Risk ({zone})"

        df[dp_col] = dew_point
        df[risk_col] = T <= dew_point + thresholds[zone]

        results[zone] = df[df[risk_col]]

    return df, results

def detect_zone_columns(df):
    zones = {}

    for col in df.columns:
        col_clean = col.lower()

        if "north" in col_clean:
            zone = "Production North"
        elif "middle" in col_clean:
            zone = "Production Middle"
        elif "attic" in col_clean:
            zone = "Attic Area"
        else:
            continue

        if "temp" in col_clean:
            zones.setdefault(zone, {})["temp"] = col
        elif "humid" in col_clean:
            zones.setdefault(zone, {})["humidity"] = col

    return zones