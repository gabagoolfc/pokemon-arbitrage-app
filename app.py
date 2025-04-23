import pandas as pd
import os
import re
import streamlit as st
from datetime import datetime
from io import BytesIO

# Utility to load and sort historical files
def load_historical_data(folder_path):
    pattern = r'pokemon_tracking_(\d{4}-\d{2}-\d{2})\.csv'
    data_files = []

    for filename in os.listdir(folder_path):
        match = re.match(pattern, filename)
        if match:
            date_str = match.group(1)
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            df["Date"] = pd.to_datetime(date_str)
            data_files.append(df)

    if not data_files:
        return None, None

    data_files.sort(key=lambda df: df["Date"].iloc[0])
    return data_files[0], data_files[-1]

# Load latest snapshot
latest_data = pd.read_csv("latest_data.csv")

# Load trends from daily_tracker
earliest_df, latest_df = load_historical_data("daily_tracker")

# Basic cleaning
latest_data = latest_data.dropna(subset=["Card Name", "Raw Price", "PSA 10 Price"])
latest_data["Raw Price"] = latest_data["Raw Price"].astype(float)
latest_data["PSA 10 Price"] = latest_data["PSA 10 Price"].astype(float)

# Add trend columns if both data sets exist
if earliest_df is not None and latest_df is not None:
    earliest_df = earliest_df.dropna(subset=["Card Name", "Raw Price", "PSA 10 Price"])
    earliest_df["Raw Price"] = earliest_df["Raw Price"].astype(float)
    earliest_df["PSA 10 Price"] = earliest_df["PSA 10 Price"].astype(float)

    trend_map = {}
    for _, row in earliest_df.iterrows():
        trend_map[row["Card Name"]] = {
            "Raw Price": row["Raw Price"],
            "PSA 10 Price": row["PSA 10 Price"]
        }

    def trend_icon(current, old):
        if pd.isna(current) or pd.isna(old):
            return "❓"
        if current > old:
            return "🔺"
        elif current < old:
            return "🔻"
        else:
            return "➖"

    raw_trends = []
    psa_trends = []

    for _, row in latest_data.iterrows():
        name = row["Card Name"]
        current_raw = row["Raw Price"]
        current_psa = row["PSA 10 Price"]
        if name in trend_map:
            prev_raw = trend_map[name]["Raw Price"]
            prev_psa = trend_map[name]["PSA 10 Price"]
            raw_trends.append(trend_icon(current_raw, prev_raw))
            psa_trends.append(trend_icon(current_psa, prev_psa))
        else:
            raw_trends.append("❓")
            psa_trends.append("❓")

    latest_data["Raw Trend"] = raw_trends
    latest_data["PSA 10 Trend"] = psa_trends

# Streamlit UI
st.set_page_config(page_title="Pokémon Arbitrage Tracker", layout="wide")
st.title("📊 Pokémon Arbitrage Dashboard")

st.markdown(f"🕒 **Pricing based on PriceCharting.com as of {datetime.now().strftime('%B %d, %Y')}**")

grading_fee = st.number_input("🔧 Grading Fee", value=20)
max_raw = st.slider("💰 Max Raw Price", 0.0, 100.0, 25.0)
max_psa = st.number_input("💎 Max PSA 10 Price", value=10000.0)
min_margin = st.number_input("📈 Min Profit Margin", value=50.0)

# Filter logic
filtered = latest_data[
    (latest_data["Raw Price"] <= max_raw) &
    (latest_data["PSA 10 Price"] <= max_psa) &
    ((latest_data["PSA 10 Price"] - (latest_data["Raw Price"] + grading_fee)) >= min_margin)
]

filtered["Total Cost"] = filtered["Raw Price"] + grading_fee
filtered["Profit Margin"] = filtered["PSA 10 Price"] - filtered["Total Cost"]

st.subheader("📋 Filtered Results")
st.success(f"Found {len(filtered)} cards matching filters:")

if "Raw Trend" in filtered.columns:
    display_cols = ["Card Name", "Raw Price", "Raw Trend", "PSA 10 Price", "PSA 10 Trend", "Total Cost", "Profit Margin"]
else:
    display_cols = ["Card Name", "Raw Price", "PSA 10 Price", "Total Cost", "Profit Margin"]

st.dataframe(filtered[display_cols], use_container_width=True)

# Download option
def convert_df(df):
    output = BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()

st.download_button(
    label="⬇️ Download Filtered List as CSV",
    data=convert_df(filtered),
    file_name='filtered_cards.csv',
    mime='text/csv',
)
