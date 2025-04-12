import pandas as pd

# Load your dataset
file_path = "big_data/merged_stock_macro_data.csv"  # Update with your actual file path
df = pd.read_csv(file_path)

# Create a copy of the macro variables for later
macro_vars = df[['Date_x', 'Inflation', 'Unemployment Rate']].drop_duplicates().set_index('Date_x')

# Pivot the stock data to wide format
wide_df = df.pivot(index=['Date_x', 'Month', 'Quarter'],
                   columns='Ticker',
                   values=['Adj Close', 'Volume'])

# Flatten multi-index column names
wide_df.columns = [f"{ticker}_{col}" for col, ticker in wide_df.columns]

# Reset index for a cleaner DataFrame
wide_df = wide_df.reset_index()

# Merge the macro variables back
wide_df = wide_df.merge(macro_vars, on='Date_x', how='left')

# Print a preview of the result
print(wide_df.head(10))

# Save the transformed dataset
wide_df.to_csv("big_data/wide_form_data.csv", index=False)

print("✅ wide-form dataset saved successfully!")