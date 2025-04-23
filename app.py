import streamlit as st
import pandas as pd
from io import BytesIO

# ✅ Enable full-width layout
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

# 🎯 Stacked Filter Inputs
max_raw = st.number_input("💰 Max Raw Price", min_value=0.0, value=25.0, format="%.2f")
max_psa = st.number_input("💎 Max PSA 10 Price", min_value=0.0, value=10000.0, format="%.2f")
grading_fee = st.number_input("🛠 Grading Fee", min_value=0, max_value=100, value=20)
min_profit = st.number_input("📈 Min Profit Margin", min_value=0.0, value=50.0, format="%.2f")

# 📚 Set Filter
all_sets = sorted(df['Set Name'].dropna().unique())
selected_sets = st.multiselect("📚 Only show sets:", all_sets)

# 🧪 Card Type Filter
selected_types = st.multiselect(
    "🧪 Only show cards with these in the name:",
    ["V", "VMAX", "VSTAR", "EX", "Reverse Holo"]
)

# 🔍 Search by Card Name
name_query = st.text_input("🔎 Search for a card (by name):")

# Calculate derived values
df['Total Cost'] = df['Raw Price'] + grading_fee
df['Profit Margin'] = df['PSA 10 Price'] - df['Total Cost']
df['Grading Fee'] = grading_fee

# Apply numeric filters
filtered = df[
    (df['Raw Price'] <= max_raw) &
    (df['PSA 10 Price'] <= max_psa) &
    (df['Profit Margin'] >= min_profit)
]

# Apply set filter
if selected_sets:
    filtered = filtered[filtered['Set Name'].isin(selected_sets)]

# Apply card type filter
if selected_types:
    filtered = filtered[
        filtered['Card Name'].str.contains('|'.join(selected_types), case=False, na=False)
    ]

# Apply name search
if name_query:
    filtered = filtered[
        filtered['Card Name'].str.contains(name_query, case=False, na=False)
    ]

# Display section title
st.markdown("### 🔍 FILTERED RESULTS")

# Show results or warning
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
        label="📥 Download Filtered List as Excel",
        data=output.getvalue(),
        file_name="filtered_arbitrage_list.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("No cards meet the filter criteria.")
