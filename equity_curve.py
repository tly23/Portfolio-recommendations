# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 20:14:37 2025

@author: clark
"""
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import time



def build_dynamic_portfolios(allocation_file, regime_file, start_date='2010-07-01', end_date= None, 
                             horizon='252 days', output_folder='output'):
    """
    Build dynamic portfolios that switch allocations based on market regimes.
    
    Parameters:
    allocation_file (str): Path to the CSV file with portfolio allocations
    regime_file (str): Path to the CSV file with market regime classifications
    start_date (str): Start date for historical data
    end_date (str): End date for historical data, defaults to today
    horizon (str): Time horizon to use (e.g., '252 days')
    output_folder (str): Folder to save outputs
    
    Returns:
    tuple: (dynamic_portfolios, spy_returns)
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Read allocation data
    print("Reading allocation data...")
    allocations = pd.read_csv(allocation_file)
    
    # Check the first column name and rename to 'ticker' if needed
    first_col_name = allocations.columns[0]
    if first_col_name == '' or first_col_name.isspace() or first_col_name == 'Unnamed: 0':
        allocations = allocations.rename(columns={allocations.columns[0]: 'ticker'})
    else:
        allocations = allocations.rename(columns={first_col_name: 'ticker'})
    
    print(f"Column names after renaming: {list(allocations.columns)[:5]}...")
    
    # Read market regime data
    print("Reading market regime data...")
    regimes = pd.read_csv(regime_file)
    regimes['Date'] = pd.to_datetime(regimes['Date_x'])
    regimes = regimes.set_index('Date')
    regimes = regimes.sort_index()
    
    # Define risk profiles
    risk_profiles = ['Risk Averse', 'Risk Neutral', 'Risk Loving']
    
    # Download SPY and TLT data for benchmark and 60/40 strategy
    print("Downloading SPY and TLT data...")
    benchmark_data = yf.download(['SPY', 'TLT'], start=start_date, end=end_date)
    
    # Calculate daily returns for SPY and TLT - use Close if Adj Close not available
    price_column = 'Adj Close' if 'Adj Close' in benchmark_data.columns else 'Close'
    benchmark_returns = benchmark_data[price_column].pct_change().dropna()
    
    # Extract SPY returns
    spy_returns = benchmark_returns['SPY']
    
    # Calculate 60/40 portfolio returns (60% SPY, 40% TLT)
    portfolio_6040_returns = 0.6 * benchmark_returns['SPY'] + 0.4 * benchmark_returns['TLT']
    
    # Get unique tickers from allocations
    tickers = allocations['ticker'].tolist()
    
    # Download historical data for all tickers
    print(f"Downloading historical data for {len(tickers)} securities...")
    
    # Download in batches to avoid potential API limitations
    batch_size = 50
    all_price_data = []
    
    for i in range(0, len(tickers), batch_size):
        batch_tickers = tickers[i:i+batch_size]
        print(f"Downloading batch {i//batch_size + 1}/{(len(tickers) + batch_size - 1)//batch_size}...")
        
        # Retry mechanism for yfinance downloads
        max_retries = 3
        for retry in range(max_retries):
            try:
                # Download both Close and Adj Close
                batch_download = yf.download(' '.join(batch_tickers), start=start_date, end=end_date)
                
                # Check if Adj Close is available, otherwise use Close
                if 'Adj Close' in batch_download.columns:
                    batch_data = batch_download['Adj Close']
                else:
                    print("Warning: 'Adj Close' not available, using 'Close' prices instead")
                    batch_data = batch_download['Close']
                
                # Handle single ticker case
                if not isinstance(batch_data, pd.DataFrame):  # If only one ticker, convert to DataFrame
                    batch_data = pd.DataFrame({batch_tickers[0]: batch_data})
                
                all_price_data.append(batch_data)
                break
            except Exception as e:
                print(f"Error downloading batch (retry {retry+1}/{max_retries}): {e}")
                if retry == max_retries - 1:
                    print(f"Failed to download batch after {max_retries} retries")
                    # Create an empty DataFrame for this batch
                    batch_data = pd.DataFrame(index=benchmark_data.index)
                    for ticker in batch_tickers:
                        batch_data[ticker] = np.nan
                    all_price_data.append(batch_data)
                time.sleep(2)  # Wait before retrying
    
    # Combine all batches
    if len(all_price_data) > 0:
        prices = pd.concat(all_price_data, axis=1)
    else:
        print("No data was downloaded!")
        return None, spy_returns
    
    # Calculate daily returns
    returns = prices.pct_change().dropna()
    
    # Align data (returns, spy_returns, regimes) to have common dates
    common_dates = returns.index.intersection(regimes.index).intersection(spy_returns.index).intersection(portfolio_6040_returns.index)
    returns = returns.loc[common_dates]
    aligned_regimes = regimes.loc[common_dates]
    spy_aligned = spy_returns.loc[common_dates]
    portfolio_6040_aligned = portfolio_6040_returns.loc[common_dates]
    
    # Extract portfolio weights for each regime and risk profile (using specified horizon)
    weights = {}
    for regime in [0, 1, 2]:
        for risk in risk_profiles:
            # Create column name based on regime, risk, and horizon
            col_name = f"Regime {regime} - {risk} - {horizon}"
            if col_name in allocations.columns:
                weights[(regime, risk)] = allocations.set_index('ticker')[col_name]
            else:
                print(f"Warning: Column {col_name} not found in allocations")
    
    # Build dynamic portfolios for each risk profile
    dynamic_portfolios = {}
    
    for risk in risk_profiles:
        # Create empty Series to store portfolio returns
        portfolio_returns = pd.Series(index=common_dates, dtype=float)
        
        # Calculate returns for each date based on appropriate regime
        for date in common_dates:
            # Get current regime
            current_regime = aligned_regimes.loc[date, 'regime']
            
            # Get weights for current regime and risk profile
            if (current_regime, risk) in weights:
                current_weights = weights[(current_regime, risk)]
                
                # Calculate returns for this date
                date_returns = returns.loc[date]
                
                # Get only tickers with data and weights
                valid_tickers = list(set(current_weights.index) & set(date_returns.index) & 
                                     set(date_returns.dropna().index))
                
                if len(valid_tickers) > 0:
                    # Normalize weights for valid tickers
                    regime_weights = current_weights[valid_tickers]
                    regime_weights = regime_weights / regime_weights.sum()
                    
                    # Calculate weighted return
                    weighted_return = (date_returns[valid_tickers] * regime_weights).sum()
                    portfolio_returns[date] = weighted_return
                else:
                    # No valid data for this date
                    portfolio_returns[date] = np.nan
            else:
                # No weights defined for this regime/risk combination
                portfolio_returns[date] = np.nan
        
        # Store the portfolio returns
        dynamic_portfolios[f"Dynamic {risk}"] = portfolio_returns
    
    # Add 60/40 portfolio returns
    dynamic_portfolios["60/40 SPY-TLT"] = portfolio_6040_aligned
    
    # Convert dynamic_portfolios to DataFrame
    df_dynamic = pd.DataFrame(dynamic_portfolios)
    
    # Handle any NaNs (forward-fill is a reasonable approach for missing daily returns)
    df_dynamic = df_dynamic.fillna(method='ffill')
    
    # Calculate cumulative returns for each portfolio and SPY
    # Find earliest date with complete data
    earliest_valid_date = df_dynamic.dropna().index[0]
    df_dynamic = df_dynamic.loc[earliest_valid_date:]
    spy_final = spy_aligned.loc[earliest_valid_date:]
    
    # Convert to cumulative returns (equity curves)
    dynamic_equity_curves = (1 + df_dynamic).cumprod() * 100  # Normalize to 100
    spy_equity_curve = (1 + spy_final).cumprod() * 100  # Normalize to 100
    
    # Combine into single DataFrame
    all_equity_curves = dynamic_equity_curves.copy()
    all_equity_curves['SPY'] = spy_equity_curve
    
    # Save to CSV
    try:
        csv_path = os.path.join(output_folder, 'dynamic_equity_curves.csv')
        all_equity_curves.to_csv(csv_path)
        print(f"Dynamic equity curves saved to {csv_path}")
    except Exception as e:
        print(f"Error saving equity curves to CSV: {e}")
        # Try to save to current directory as fallback
        try:
            fallback_path = 'dynamic_equity_curves.csv' 
            all_equity_curves.to_csv(fallback_path)
            print(f"Dynamic equity curves saved to fallback location: {fallback_path}")
        except Exception as e2:
            print(f"Failed to save equity curves: {e2}")
    
    # Create plot
    try:
        plt.figure(figsize=(12, 8))
        
        # Define colors for better visualization
        colors = {
            'Dynamic Risk Averse': 'blue',
            'Dynamic Risk Neutral': 'green',
            'Dynamic Risk Loving': 'red',
            '60/40 SPY-TLT': 'purple',
            'SPY': 'black'
        }
        
        # Plot portfolio curves
        for col in dynamic_equity_curves.columns:
            plt.plot(dynamic_equity_curves[col], label=col, color=colors.get(col, None))
        
        # Plot SPY
        plt.plot(spy_equity_curve, label='SPY', color=colors['SPY'], linewidth=2, linestyle='--')
        
        # Add regime background shading
        prev_date = earliest_valid_date
        prev_regime = aligned_regimes.loc[earliest_valid_date, 'regime']
        regime_colors = {0: 'lightblue', 1: 'lightgreen', 2: 'lightsalmon'}
        regime_dates = []
        
        for date, row in aligned_regimes.loc[earliest_valid_date:].iterrows():
            if row['regime'] != prev_regime:
                # Regime changed, add shading for previous period
                regime_dates.append((prev_date, date, prev_regime))
                prev_date = date
                prev_regime = row['regime']
        
        # Add the last regime period
        regime_dates.append((prev_date, aligned_regimes.index[-1], prev_regime))
        
        # Apply shading
        for start_date, end_date, regime in regime_dates:
            plt.axvspan(start_date, end_date, alpha=0.2, color=regime_colors[regime], 
                      label=f'Regime {regime}' if f'Regime {regime}' not in plt.gca().get_legend_handles_labels()[1] else "")
        
        # Add labels and title
        plt.title("Dynamic Regime-Based Portfolios vs Benchmarks (Normalized to 100)", fontsize=14)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Try to save the plot to the output folder
        try:
            plot_path = os.path.join(output_folder, "dynamic_portfolio_comparison.png")
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            print(f"Comparison plot saved to {plot_path}")
        except Exception as e:
            print(f"Error saving plot to {output_folder}: {e}")
            # Try to save to current directory as fallback
            try:
                fallback_path = os.path.join('.', "dynamic_portfolio_comparison.png")
                plt.savefig(fallback_path, dpi=300, bbox_inches='tight')
                print(f"Comparison plot saved to fallback location: {fallback_path}")
            except Exception as e2:
                print(f"Failed to save plot: {e2}")
        
        plt.close()
    except Exception as e:
        print(f"Error creating plot: {e}")
    
    # Calculate performance metrics
    metrics = calculate_performance_metrics(dynamic_equity_curves, spy_equity_curve, output_folder)
    
    return all_equity_curves, metrics

def calculate_performance_metrics(portfolio_returns, spy_returns, output_folder='output'):
    """
    Calculate performance metrics for all portfolios.
    
    Parameters:
    portfolio_returns (DataFrame): Portfolio returns
    spy_returns (Series): SPY returns (already as equity curve)
    output_folder (str): Folder to save outputs
    """
    # Add SPY to portfolio returns
    combined_returns = portfolio_returns.copy()
    combined_returns['SPY'] = spy_returns
    
    # Convert to percentage change
    pct_change = combined_returns.pct_change().dropna()
    
    # Calculate metrics
    metrics = pd.DataFrame(index=combined_returns.columns)
    
    # Calculate annualized return
    total_days = len(pct_change)
    years = total_days / 252
    
    # Terminal value divided by initial value, annualized
    metrics['Annualized Return (%)'] = (
        (combined_returns.iloc[-1] / combined_returns.iloc[0]) ** (1/years) - 1
    ) * 100
    
    # Calculate annualized volatility
    metrics['Annualized Volatility (%)'] = pct_change.std() * np.sqrt(252) * 100
    
    # Calculate Sharpe ratio (assuming risk-free rate of 0%)
    metrics['Sharpe Ratio'] = metrics['Annualized Return (%)'] / metrics['Annualized Volatility (%)']
    
    # Calculate maximum drawdown
    rolling_max = combined_returns.cummax()
    drawdown = (combined_returns / rolling_max - 1) * 100
    metrics['Maximum Drawdown (%)'] = drawdown.min()
    
    # Calculate total return
    metrics['Total Return (%)'] = (combined_returns.iloc[-1] / combined_returns.iloc[0] - 1) * 100
    
    # Save to CSV
    csv_path = os.path.join(output_folder, 'dynamic_performance_metrics.csv')
    metrics.to_csv(csv_path)
    print(f"Performance metrics saved to {csv_path}")
    
    return metrics

def main():
    """Main function to execute the script."""
    # Set the file paths
    allocation_file = 'portfolio_allocations.csv'
    regime_file = 'market_regimes.csv'
  
    end_date = datetime.today().strftime('%Y-%m-%d')
    # Create a more robust output directory
    output_dir = 'output'
    # Ensure all paths are valid
    if not os.path.exists(allocation_file):
        print(f"Warning: Allocation file '{allocation_file}' not found.")
        allocation_file = input("Please enter the path to your allocation CSV file: ")
    
    if not os.path.exists(regime_file):
        print(f"Warning: Regime file '{regime_file}' not found.")
        regime_file = input("Please enter the path to your market regimes CSV file: ")
    
    # Build dynamic portfolios
    try:
        equity_curves, metrics = build_dynamic_portfolios(
            allocation_file=allocation_file,
            regime_file=regime_file,
            horizon='252 days',  # Use 252 days horizon as specified
            output_folder=output_dir,
            end_date = end_date
        )
        
        if equity_curves is not None:
            print("\nPerformance Metrics:")
            print(metrics)
            print("\nProcessing complete!")
        else:
            print("Failed to build dynamic portfolios")
    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()