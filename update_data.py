import pandas as pd
import yfinance as yf
from fredapi import Fred
import time
from datetime import datetime, timedelta
import os.path

def update_stock_data(existing_file="sp500_market_data.csv"):
    """
    Update stock data by only fetching the most recent data
    """
    # Check if the existing file exists
    if not os.path.isfile(existing_file):
        print(f"Error: {existing_file} not found. Please run stock_fetch.py first to create the initial dataset.")
        return None
    
    # Load existing data
    print(f"Loading existing stock data from {existing_file}...")
    try:
        # First attempt - try with 'Date' as the date column
        existing_data = pd.read_csv(existing_file, parse_dates=["Date"])
        date_column = "Date"
    except ValueError as e:
        if "Missing column provided to 'parse_dates'" in str(e):
            # Check the columns in the file without parsing dates
            temp_df = pd.read_csv(existing_file)
            print(f"Available columns in {existing_file}: {temp_df.columns.tolist()}")
            
            # Look for possible date columns
            date_cols = [col for col in temp_df.columns if 'date' in col.lower() or 'time' in col.lower()]
            if date_cols:
                print(f"Found potential date columns: {date_cols}")
                date_column = date_cols[0]  # Use the first one
                print(f"Using '{date_column}' as the date column")
                existing_data = pd.read_csv(existing_file, parse_dates=[date_column])
            else:
                raise ValueError(f"Could not find a date column in {existing_file}. Please ensure your file has a date column.")
        else:
            raise
    
    # Find the latest date in the existing data
    if date_column not in existing_data.columns:
        print(f"Warning: '{date_column}' column not found in data. Please check column names.")
        print(f"Available columns: {existing_data.columns.tolist()}")
        return None
        
    latest_date = existing_data[date_column].max()
    print(f"Latest date in existing data: {latest_date}")
    start_date = latest_date + timedelta(days=1)
    
    # If latest date is today or in the future, no need to update
    today = pd.Timestamp.now().normalize()
    if start_date > today:
        print(f"Data is already up to date (latest date: {latest_date.strftime('%Y-%m-%d')})")
        return existing_data
    
    print(f"Fetching new data from {start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}...")
    
    # Get unique tickers from existing data
    tickers = existing_data["Ticker"].unique().tolist()
    
    # Data storage for new data
    new_data = pd.DataFrame()
    failed_tickers = []
    
    # Fetch each ticker individually
    for ticker in tickers:
        print(f"Updating data for {ticker}...")
        attempt = 0
        while attempt < 3:  # Retry up to 3 times
            try:
                # Only fetch from the day after the latest date
                data = yf.download(
                    ticker, 
                    start=start_date.strftime('%Y-%m-%d'),
                    end=(today + timedelta(days=1)).strftime('%Y-%m-%d'),  # Add 1 day to include today
                    interval="1d", 
                    auto_adjust=False, 
                    multi_level_index=False
                )
                
                if not data.empty:
                    data.reset_index(inplace=True)
                    data["Ticker"] = ticker
                    new_data = pd.concat([new_data, data], ignore_index=True)
                    break  # Exit retry loop if successful
                else:
                    print(f"No new data found for {ticker}")
                    break
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")
                attempt += 1
                time.sleep(2)  # Pause before retry
                if attempt == 3:
                    failed_tickers.append(ticker)
        
        time.sleep(1)  # Slight delay to avoid rate limits
    
    # If no new data, return existing data
    if new_data.empty:
        print("No new data to append")
        return existing_data
    
    # Combine existing and new data
    updated_data = pd.concat([existing_data, new_data], ignore_index=True)
    
    # Sort by ticker and date
    updated_data.sort_values(["Ticker", date_column], inplace=True)
    
    # Remove duplicates if any
    if date_column == "Date":
        updated_data.drop_duplicates(subset=["Ticker", date_column], keep="last", inplace=True)
    else:
        # If we're using a different date column name, make sure we use that for deduplication
        updated_data.drop_duplicates(subset=["Ticker", date_column], keep="last", inplace=True)
    
    # Create monthly and quarterly columns if they don't exist
    if "Month" not in updated_data.columns:
        updated_data["Month"] = updated_data[date_column].dt.to_period("M").astype(str)  # YYYY-MM
    
    if "Quarter" not in updated_data.columns:
        updated_data["Quarter"] = updated_data[date_column].dt.to_period("Q").astype(str)  # YYYY-Qx
    
    # Save updated data
    updated_data.to_csv(existing_file, index=False)
    print(f"Updated stock data saved to {existing_file}")
    
    # Report on new data
    num_new_records = len(new_data)
    latest_updated_date = new_data["Date"].max() if not new_data.empty else latest_date
    print(f"Added {num_new_records} new records. Data now extends to {latest_updated_date.strftime('%Y-%m-%d')}")
    
    # Log failed tickers
    if failed_tickers:
        print(f"Failed to update data for: {failed_tickers}")
    
    return updated_data

def update_macro_data(existing_file="merged_stock_macro_data.csv"):
    """
    Update macroeconomic data from FRED
    """
    # Set up FRED API Key
    fred = Fred(api_key='b20083ae5ef93b557cb16e15bf89353c')
    
    # Define macroeconomic indicators
    macro_indicators = {
        "CPIAUCSL": "Inflation",  # Consumer Price Index (CPI, Monthly)
        "UNRATE": "Unemployment Rate"  # Unemployment Rate (Monthly)
    }
    
    # Check if we need to update macro data (FRED data is monthly, so only update if it's a new month)
    today = datetime.now()
    current_month = f"{today.year}-{today.month:02d}"
    
    # Check if merged file exists
    if os.path.isfile(existing_file):
        # Load existing merged data
        print(f"Loading existing merged data from {existing_file}...")
        merged_df = pd.read_csv(existing_file)
        
        # Check the date columns that exist
        date_cols = [col for col in merged_df.columns if 'date' in col.lower()]
        print(f"Date-related columns found: {date_cols}")
        
        # Define stock date column and macro date column
        stock_date_col = next((col for col in date_cols if col.lower().endswith('_x')), None)
        macro_date_col = next((col for col in date_cols if col.lower().endswith('_y')), None)
        
        if stock_date_col:
            print(f"Using {stock_date_col} as stock date column")
            merged_df[stock_date_col] = pd.to_datetime(merged_df[stock_date_col])
        
        if macro_date_col:
            print(f"Using {macro_date_col} as macro date column")
            merged_df[macro_date_col] = pd.to_datetime(merged_df[macro_date_col])
            latest_macro_date = merged_df[macro_date_col].max()
            print(f"Latest macro date found: {latest_macro_date}")
        elif "Month" in merged_df.columns:
            # If we're using the Month column for merging
            months = merged_df["Month"].unique()
            print(f"Months present in data: {sorted(months)[-5:]} (showing last 5)")
            if current_month in months:
                print("Macroeconomic data is already up to date for the current month")
                return merged_df
        else:
            print("Warning: Could not find date columns to check macro data. Will proceed with update.")
    
    # Fetch updated stock data
    stock_data = update_stock_data()
    if stock_data is None:
        return None
    
    print("Fetching latest macroeconomic data from FRED...")
    
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
    
    # Identify date column in stock data
    stock_date_cols = [col for col in stock_data.columns if 'date' in col.lower()]
    stock_date_col = stock_date_cols[0] if stock_date_cols else "Date"
    
    # Make sure "Month" column exists in stock_data
    if "Month" not in stock_data.columns:
        stock_data["Month"] = stock_data[stock_date_col].dt.to_period("M").astype(str)
    
    # Merge stock data with macro data (Left Join on Month)
    merged_data = stock_data.merge(macro_df, on="Month", how="left")
    
    # Save final dataset
    merged_data.to_csv(existing_file, index=False)
    print(f"Updated merged data saved to {existing_file}")
    
    return merged_data

if __name__ == "__main__":
    # Update both stock and macro data
    updated_data = update_macro_data()
    
    if updated_data is not None:
        print("\nData update complete!")
        
        # Print some statistics about the updated dataset
        num_tickers = updated_data["Ticker"].nunique()
        
        # Get date columns and determine which to use for reporting
        date_cols = [col for col in updated_data.columns if 'date' in col.lower()]
        stock_date_col = next((col for col in date_cols if col.lower().endswith('_x')), 
                              next((col for col in date_cols if not col.lower().endswith('_y')), "Date"))
        
        try:
            date_range = f"{updated_data[stock_date_col].min().strftime('%Y-%m-%d')} to {updated_data[stock_date_col].max().strftime('%Y-%m-%d')}"
        except:
            date_range = "Unknown (could not determine date range from available columns)"
            
        records = len(updated_data)
        
        print(f"\nDataset Statistics:")
        print(f"Number of tickers: {num_tickers}")
        print(f"Date range: {date_range}")
        print(f"Total records: {records}")
        print(f"Columns available: {', '.join(updated_data.columns.tolist())}")