import streamlit as st
import pandas as pd
from io import BytesIO
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === Connect to Google Sheets ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
gcp_service_account = json.loads(st.secrets["gcp_service_account"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(gcp_service_account, scope)
client = gspread.authorize(credentials)
sheet = client.open("Pokemon Arbitrage App Emails").sheet1

  # Sheet name must match your Sheet exactly

# ✅ Enable wide layout
st.set_page_config(layout="wide")

# Load and clean CSV
df = pd.read_csv("latest_data.csv")
df.columns = [col.strip() for col in df.columns]
df['Set Name'] = df['Set Name'].str.replace("PRICES FOR POKEMON ", "", case=False)

# App Title & Pricing Date
st.title("💸 Pokémon Arbitrage Dashboard")
if 'Date' in df.columns:
    last_date = pd.to_datetime(df['Date'].max()).strftime('%B %d, %Y')
    st.caption(f"💡 Pricing based on PriceCharting.com as of **{last_date}**")

st.markdown("---")

# Add intro text
st.markdown("Find Pokémon cards you can buy raw, grade, and profit on.\nUpdated daily with live market prices.")

# 🔲 3-column filter layout
col1, col2, col3 = st.columns(3)

with col1:
    max_raw = st.number_input("💰 Max Raw Price", min_value=0.0, value=25.0, format="%.2f")
    min_profit = st.number_input("📈 Min Profit Margin", min_value=0.0, value=100.0, format="%.2f")

with col2:
    max_psa = st.number_input("💎 Max PSA 10 Price", min_value=0.0, value=2000.0, format="%.2f")
    selected_sets = st.multiselect("📚 Only show sets:", sorted(df['Set Name'].dropna().unique()))

with col3:
    grading_fee = st.number_input("🖼 Grading Fee", min_value=0, max_value=100, value=20)
    selected_types = st.multiselect(
        "🧪 Only show cards with these in the name:",
        ["V", "VMAX", "VSTAR", "EX", "Reverse Holo"]
    )

# 🔍 Full-width search bar
name_query = st.text_input("🔎 Search for a card (by name):")

# Calculate derived values
df['Total Cost'] = df['Raw Price'] + grading_fee
df['Profit Margin'] = df['PSA 10 Price'] - df['Total Cost']
df['Grading Fee'] = grading_fee

# Apply filters
filtered = df[
    (df['Raw Price'] <= max_raw) &
    (df['PSA 10 Price'] <= max_psa) &
    (df['Profit Margin'] >= min_profit)
]

if selected_sets:
    filtered = filtered[filtered['Set Name'].isin(selected_sets)]

if selected_types:
    filtered = filtered[
        filtered['Card Name'].str.contains('|'.join(selected_types), case=False, na=False)
    ]

if name_query:
    filtered = filtered[
        filtered['Card Name'].str.contains(name_query, case=False, na=False)
    ]

# Results section
st.markdown("### 🔍 FILTERED RESULTS")

if not filtered.empty:
    st.success(f"Found {len(filtered)} cards matching filters:")
    st.dataframe(
        filtered[['Set Name', 'Card Name', 'Raw Price', 'PSA 10 Price', 'Grading Fee', 'Total Cost', 'Profit Margin']],
        use_container_width=True
    )

    # Excel download
    output = BytesIO()
    filtered.to_excel(output, index=False, engine='openpyxl')
    st.download_button(
        label="📅 Download Filtered List as Excel",
        data=output.getvalue(),
        file_name="filtered_arbitrage_list.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("No cards meet the filter criteria.")

st.markdown("---")
st.markdown("### 🚀 Stay in the loop!")

email = st.text_input("Leave your email if you want early access to the full version (optional):")

if st.button("Submit Email"):
    if email:
        sheet.append_row([email])
        st.success("✅ Thanks! You'll be the first to know when we launch.")
    else:
        st.error("Please enter a valid email address before submitting.")


