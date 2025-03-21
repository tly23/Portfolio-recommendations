import yfinance as yf
import pandas as pd
import time

# Load S&P 500 tickers from the uploaded CSV file
sp500_df = pd.read_csv('SP500.csv')
tickers = sp500_df['Symbol'].str.strip().str.upper().tolist()

# Additional assets to fetch
tickers += ["SPY", "DIA", "QQQ", "IWM", "GLD", "USO", "BTC-USD", "TLT", "SHY", "^VIX", "EEM", "FXI", "EWZ", "VWO", "ILF","EWJ","XLF", "XLE", "XLK", "XLY", "XLI", "XLB", "XLV", "XLU", "XLC", "XLRE"]

# Data storage
all_stock_data = pd.DataFrame()
failed_tickers = []

# Fetch each ticker individually to avoid API issues
for ticker in tickers:
    print(f"Fetching data for {ticker}...")
    attempt = 0
    while attempt < 3:  # Retry up to 3 times
        try:
            data = yf.download(ticker, interval="1d", auto_adjust=False, multi_level_index=False)
            if not data.empty:
                data.reset_index(inplace=True)
                data["Ticker"] = ticker
                all_stock_data = pd.concat([all_stock_data, data], ignore_index=True)
                break  # Exit retry loop if successful
            else:
                print(f"No data found for {ticker}, skipping...")
                failed_tickers.append(ticker)
                break
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            attempt += 1
            time.sleep(2)  # Pause before retry

    time.sleep(1)  # Slight delay to avoid rate limits

# Save to CSV
output_file = "sp500_market_data.csv"
all_stock_data.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")

# Log failed tickers
if failed_tickers:
    print(f"Failed to download data for: {failed_tickers}")