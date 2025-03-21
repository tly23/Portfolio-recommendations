

import pandas as pd
from fredapi import Fred

# Set up FRED API Key (replace 'YOUR_API_KEY' with your actual key)
fred = Fred(api_key='b20083ae5ef93b557cb16e15bf89353c')

# Define macroeconomic indicators
macro_indicators = {
    "CPIAUCSL": "Inflation",  # Consumer Price Index (CPI, Monthly)
    "UNRATE": "Unemployment Rate"  # Unemployment Rate (Monthly)
}

# Fetch macro data
macro_data = {}
for series, name in macro_indicators.items():
    print(f"Fetching {name} from FRED...")
    df = fred.get_series(series)
    df = df.to_frame(name)
    df.index = pd.to_datetime(df.index)
    macro_data[name] = df

# Convert CPI to Year-over-Year (YoY) percentage change
macro_data["Inflation"] = macro_data["Inflation"].pct_change(periods=12) * 100

# Combine macro data into one DataFrame
macro_df = pd.concat(macro_data.values(), axis=1)
macro_df = macro_df.reset_index().rename(columns={"index": "Date"})
macro_df["Month"] = macro_df["Date"].dt.to_period("M").astype(str)  # Convert to YYYY-MM

# Load stock data
stock_data = pd.read_csv("sp500_market_data.csv", parse_dates=["Date"])

# Create monthly and quarterly columns
stock_data["Month"] = stock_data["Date"].dt.to_period("M").astype(str)  # YYYY-MM
stock_data["Quarter"] = stock_data["Date"].dt.to_period("Q").astype(str)  # YYYY-Qx

# Merge stock data with macro data (Left Join on Date)
merged_data = stock_data.merge(macro_df, on="Month", how="left")

# Save final dataset
output_file = "merged_stock_macro_data.csv"
merged_data.to_csv(output_file, index=False)
print(f"Merged data saved to {output_file}")
