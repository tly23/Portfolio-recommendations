# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 19:57:09 2025

@author: clark

Script for feature creation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import warnings

# Suppress the PerformanceWarning about fragmented DataFrames
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

# Load the cleaned weekday data
file_path = "clean_weekday_data.csv"
df = pd.read_csv(file_path)

# Ensure Date_x is datetime
df['Date_x'] = pd.to_datetime(df['Date_x'])
df = df.sort_values('Date_x')  # Ensure data is sorted by date

print(f"Loaded dataset with shape: {df.shape}")
print(f"Date range: {df['Date_x'].min()} to {df['Date_x'].max()}")

# Get all ticker symbols from column names
all_columns = df.columns
ticker_columns = [col for col in all_columns if '_' in col]
unique_tickers = set()
for col in ticker_columns:
    ticker = col.split('_')[0]
    if ticker not in ['Date', 'Month', 'Quarter']:
        unique_tickers.add(ticker)

tickers = sorted(list(unique_tickers))
print(f"Found {len(tickers)} unique tickers")

# Create empty DataFrame to store all features
features_df = df[['Date_x', 'Month', 'Quarter']].copy()
if 'Inflation' in df.columns:
    features_df['Inflation'] = df['Inflation']
if 'Unemployment Rate' in df.columns:
    features_df['Unemployment Rate'] = df['Unemployment Rate']

# Function to calculate features for a ticker
def calculate_ticker_features(ticker, df, features_df):
    # Check if ticker has Adj Close and Volume columns
    adj_close_col = f"{ticker}_Adj Close"
    volume_col = f"{ticker}_Volume"
    
    if adj_close_col in df.columns and volume_col in df.columns:
        # Extract price and volume data
        prices = df[adj_close_col].copy()
        volumes = df[volume_col].copy()
        
        # Identify and handle extreme outliers in price data
        zscore = stats.zscore(prices, nan_policy='omit')
        price_outliers = abs(zscore) > 4
        prices[price_outliers] = np.nan
        prices = prices.fillna(method='ffill').fillna(method='bfill')
        
        # 1. Calculate daily returns (with outlier handling)
        daily_returns = prices.pct_change()
        # Handle extreme return outliers (4+ standard deviations)
        ret_zscore = stats.zscore(daily_returns, nan_policy='omit')
        ret_outliers = abs(ret_zscore) > 4
        daily_returns[ret_outliers] = np.nan
        daily_returns = daily_returns.fillna(method='ffill').fillna(0)  # Replace outliers with 0 return
        features_df[f"{ticker}_Return"] = daily_returns
        
        # 2. Calculate 200-day moving average
        ma_200 = prices.rolling(window=200, min_periods=100).mean()
        features_df[f"{ticker}_MA200"] = ma_200
        
        # Price relative to 200-day MA (percentage)
        price_to_ma = prices / ma_200 - 1
        # Handle inf/nan values
        price_to_ma = np.clip(price_to_ma, -0.9, 9)  # Limit extreme values
        features_df[f"{ticker}_Price_to_MA200"] = price_to_ma * 100
        
        # 3. Calculate RSI (Relative Strength Index) - 14 day period
        delta = prices.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        
        # Use simple method to avoid DataFrame fragmentation
        avg_gain = gain.rolling(window=14, min_periods=1).mean()
        avg_loss = loss.rolling(window=14, min_periods=1).mean()
        
        # Avoid division by zero
        avg_loss = avg_loss.replace(0, np.nan)
        rs = avg_gain / avg_loss
        rs = rs.fillna(0)
        
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.clip(0, 100)  # Ensure RSI is between 0-100
        features_df[f"{ticker}_RSI"] = rsi
        
        # 4. Calculate liquidity metric (Dollar volume needed to move price 1%)
        # Use 20-day rolling window to estimate price impact
        dollar_volume = prices * volumes
        
        # Calculate average daily dollar volume (20-day)
        avg_dollar_volume = dollar_volume.rolling(window=20, min_periods=5).mean()
        
        # Calculate average daily absolute return (20-day)
        abs_returns = daily_returns.abs()
        # Handle zeros in denominators
        abs_returns = abs_returns.replace(0, np.nan)
        avg_abs_return = abs_returns.rolling(window=20, min_periods=5).mean()
        
        # Liquidity metric: Average $ volume / Average absolute return %
        # Higher number means more liquid (more $ needed to move price 1%)
        liquidity = avg_dollar_volume / (avg_abs_return * 100)
        # Clip extreme values
        liquidity = np.clip(liquidity, 0, liquidity.quantile(0.99))
        features_df[f"{ticker}_Liquidity"] = liquidity
        
        # 5. Volatility (20-day rolling std of returns)
        volatility = daily_returns.rolling(window=20, min_periods=5).std() * np.sqrt(252)  # Annualized
        # Clip extreme values
        volatility = np.clip(volatility, 0, volatility.quantile(0.99))
        features_df[f"{ticker}_Volatility"] = volatility
        
        return True
    else:
        return False

# Process tickers in batches to avoid fragmentation
batch_size = 25
total_processed = 0

for i in range(0, len(tickers), batch_size):
    batch_tickers = tickers[i:i+batch_size]
    print(f"Processing batch {i//batch_size + 1}/{(len(tickers) + batch_size - 1)//batch_size} ({len(batch_tickers)} tickers)")
    
    batch_success = 0
    for ticker in batch_tickers:
        success = calculate_ticker_features(ticker, df, features_df)
        if success:
            batch_success += 1
    
    total_processed += batch_success
    print(f"  Successfully processed {batch_success}/{len(batch_tickers)} tickers in this batch")
    
print(f"Total tickers processed: {total_processed}/{len(tickers)}")

# Calculate market-wide features using robust methods
print("Calculating market-wide features...")

# Get all return columns
return_cols = [col for col in features_df.columns if col.endswith('_Return')]

# Create an equally-weighted market return
if return_cols:
    # Use a more efficient method to calculate means
    returns_matrix = features_df[return_cols].values
    # Replace inf/NaN with 0 for calculation
    returns_matrix = np.nan_to_num(returns_matrix, nan=0.0, posinf=0.0, neginf=0.0)
    # Calculate row means
    market_returns = np.mean(returns_matrix, axis=1)
    features_df['Market_Return'] = market_returns
    
    # Calculate market volatility (20-day rolling std of market return)
    market_vol = pd.Series(market_returns).rolling(window=20, min_periods=5).std() * np.sqrt(252)
    features_df['Market_Volatility'] = market_vol

# Calculate average RSI across all stocks
rsi_cols = [col for col in features_df.columns if col.endswith('_RSI')]
if rsi_cols:
    rsi_matrix = features_df[rsi_cols].values
    rsi_matrix = np.nan_to_num(rsi_matrix, nan=50.0)  # Replace NaN with neutral RSI
    features_df['Average_RSI'] = np.mean(rsi_matrix, axis=1)

# Calculate average liquidity across all stocks
liquidity_cols = [col for col in features_df.columns if col.endswith('_Liquidity')]
if liquidity_cols:
    liq_matrix = features_df[liquidity_cols].values
    liq_matrix = np.nan_to_num(liq_matrix, nan=0.0)
    features_df['Market_Liquidity'] = np.mean(liq_matrix, axis=1)

# Calculate percentage of stocks above their 200-day MA
ma_cols = [col for col in features_df.columns if col.endswith('_Price_to_MA200')]
if ma_cols:
    ma_matrix = features_df[ma_cols].values
    ma_matrix = np.nan_to_num(ma_matrix, nan=0.0)
    features_df['Stocks_Above_MA200'] = np.mean(ma_matrix > 0, axis=1) * 100

# Remove rows with NaN values in the beginning of the time series
# (due to rolling windows, we'll have NaN values for the first 200 days)
print(f"Shape before removing initial NaN rows: {features_df.shape}")
features_df = features_df.dropna(subset=['Market_Return', 'Market_Volatility'])
print(f"Shape after removing initial NaN rows: {features_df.shape}")

# Check for any remaining NaN values
nan_count = features_df.isnull().sum().sum()
print(f"Remaining NaN values: {nan_count}")

# If there are remaining NaNs, fill them
if nan_count > 0:
    # Fill NaNs with forward fill then backward fill
    features_df = features_df.fillna(method='ffill').fillna(method='bfill')
    
    # Check if all NaNs are filled
    remaining_nans = features_df.isnull().sum().sum()
    print(f"NaNs after filling: {remaining_nans}")

# Create visualization of key market-wide features with outlier handling
plt.figure(figsize=(14, 10))

# Plot 1: Market Return
plt.subplot(2, 2, 1)
# Handle extreme outliers
market_ret = features_df['Market_Return'] * 100
market_ret = np.clip(market_ret, market_ret.quantile(0.001), market_ret.quantile(0.999))
plt.plot(features_df['Date_x'], market_ret)
plt.title('Daily Market Return (%)')
plt.grid(True)

# Plot 2: Market Volatility
plt.subplot(2, 2, 2)
# Handle extreme outliers
market_vol = features_df['Market_Volatility'] * 100
market_vol = np.clip(market_vol, market_vol.quantile(0.001), market_vol.quantile(0.999))
plt.plot(features_df['Date_x'], market_vol)
plt.title('Market Volatility (%, Annualized)')
plt.grid(True)

# Plot 3: Average RSI
plt.subplot(2, 2, 3)
plt.plot(features_df['Date_x'], features_df['Average_RSI'])
plt.axhline(y=70, color='r', linestyle='--')
plt.axhline(y=30, color='g', linestyle='--')
plt.title('Average RSI')
plt.grid(True)

# Plot 4: Percentage of Stocks Above 200-day MA
plt.subplot(2, 2, 4)
plt.plot(features_df['Date_x'], features_df['Stocks_Above_MA200'])
plt.axhline(y=50, color='k', linestyle='--')
plt.title('Stocks Above 200-day MA (%)')
plt.grid(True)

plt.tight_layout()
plt.savefig('market_features.png')
print("✅ Created visualization of market features: 'market_features.png'")

# Save features to CSV
output_file = "engineered_features.csv"
features_df.to_csv(output_file, index=False)
print(f"✅ Saved engineered features to {output_file}")

# Print summary of created features
print("\nFeature Engineering Summary:")
print("-" * 40)

# Group features by type
return_features = [col for col in features_df.columns if '_Return' in col]
ma_features = [col for col in features_df.columns if '_MA200' in col or '_to_MA200' in col]
rsi_features = [col for col in features_df.columns if '_RSI' in col]
liquidity_features = [col for col in features_df.columns if '_Liquidity' in col]
volatility_features = [col for col in features_df.columns if '_Volatility' in col]
market_features = ['Market_Return', 'Market_Volatility', 'Average_RSI', 'Market_Liquidity', 'Stocks_Above_MA200']
macro_features = [col for col in features_df.columns if col in ['Inflation', 'Unemployment Rate']]

print(f"Date range: {features_df['Date_x'].min()} to {features_df['Date_x'].max()}")
print(f"Total rows: {len(features_df)}")
print(f"Return features: {len(return_features)}")
print(f"Moving average features: {len(ma_features)}")
print(f"RSI features: {len(rsi_features)}")
print(f"Liquidity features: {len(liquidity_features)}")
print(f"Volatility features: {len(volatility_features)}")
print(f"Market-wide features: {len(market_features)}")
print(f"Macro features: {len(macro_features)}")
print(f"Total features: {len(features_df.columns)}")

print("\nThe dataset is now ready for regime clustering!")