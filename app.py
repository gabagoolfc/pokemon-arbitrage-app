import streamlit as st
import pandas as pd
from io import BytesIO

# Sample data – you can later connect this to your real scraping logic
data = {
    'Card Name': ['Charizard V', 'Umbreon V', 'Gengar VMAX', 'Pikachu Full Art'],
    'Set': ['Brilliant Stars', 'Evolving Skies', 'Fusion Strike', 'Vivid Voltage'],
    'Raw Price': [22.4, 17.8, 25.0, 10.5],
    'PSA 10 Price': [165.0, 145.0, 130.0, 95.0]
}

df = pd.DataFrame(data)
df['Grading Fee'] = 20.0
df['Total Cost'] = df['Raw Price'] + df['Grading Fee']
df['Profit Margin'] = df['PSA 10 Price'] - df['Total Cost']

# --- Streamlit UI ---
st.title("🧠 Pokémon Card Arbitrage Finder")

st.write("This tool helps you find profitable flips by comparing raw prices to PSA 10 resale values.")

min_profit = st.slider("Minimum Profit Margin ($)", 0, 150, 50)

filtered = df[df['Profit Margin'] >= min_profit]

if not filtered.empty:
    st.success(f"Found {len(filtered)} profitable cards:")
    st.dataframe(filtered)

    output = BytesIO()
    filtered.to_excel(output, index=False, engine='openpyxl')

    st.download_button(
        label="📥 Download as Excel",
        data=output.getvalue(),
        file_name="arbitrage_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("No cards meet the profit margin criteria.")
