# -*- coding: utf-8 -*-
"""
Created on Sat Apr 12 16:25:44 2025

@author: clark
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def classify_portfolio_assets(csv_path):
    """
    Classify assets in a portfolio CSV file into 7 major asset classes and calculate weights.
    
    Parameters:
    -----------
    csv_path : str
        Path to the CSV file containing portfolio allocations
    
    Returns:
    --------
    pd.DataFrame
        A DataFrame containing the weights for each asset class in different regimes
    """
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Define the 7 major asset classes and their constituent tickers
    asset_classes = {
        "MAG7": ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'GOOG', 'META', 'TSLA'],
        "Bonds": ['TLT', 'SHY', 'IEF', 'AGG', 'LQD', 'HYG', 'MUB', 'TIP', 'BIL', 'BND'],
        "Commodities": ['GLD', 'USO', 'SLV', 'OIL', 'DBC', 'GSC', 'BNO', 'UNG', 'XLE', '^VIX'],
        "Crypto": ['BITO', 'GBTC', 'COIN', 'MSTR'],
        "Market_Indices": ['SPY', 'QQQ', 'DIA', 'IWM', 'VWO', 'EEM', 'FXI', 'EWJ', 'EWZ', 'ILF', 'VTI',
                         'XLB', 'XLF', 'XLI', 'XLK', 'XLU', 'XLV', 'XLY', 'XLRE'],
        "Low_Beta_Stocks": [
            # Consumer Staples
            'PG', 'KO', 'PEP', 'WMT', 'COST', 'MO', 'PM', 'KMB', 'CLX', 'GIS', 'K', 'CPB', 'CAG', 
            'HRL', 'SJM', 'KR', 'HSY', 'MKC', 'CL', 'STZ',
            # Utilities
            'DUK', 'SO', 'NEE', 'D', 'AEP', 'XEL', 'ED', 'ES', 'PEG', 'EXC', 'WEC', 'CMS', 'PCG', 
            'NI', 'CNP', 'AEE', 'ETR', 'FE', 'SRE', 'AWK',
            # Healthcare 
            'JNJ', 'PFE', 'MRK', 'ABBV', 'ABT', 'LLY', 'BMY', 'UNH', 'CVS', 'MDT', 'GILD', 'AMGN', 
            'BIIB', 'VRTX', 'REGN', 'BSX', 'ZTS', 'DHR', 'TMO', 'ISRG',
            # Telecommunications
            'VZ', 'T', 'TMUS', 'CMCSA', 'CHTR', 'LUMN', 'DISH',
            # Real Estate
            'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'O', 'AVB', 'EQR', 'DLR', 'SPG', 'WELL', 'VTR', 
            'BXP', 'ARE', 'REG', 'UDR', 'HST', 'VICI'
        ],
        "High_Beta_Growth_Stocks": [
            # Technology (excluding MAG7)
            'ADBE', 'AMAT', 'AMD', 'AVGO', 'CSCO', 'IBM', 'INTC', 'ORCL', 'QCOM', 'TXN', 'CRM', 
            'NFLX', 'PYPL', 'MU', 'LRCX', 'KLAC', 'PANW', 'SNOW', 'CDNS', 'SNPS', 'INTU',
            # Consumer Discretionary (excluding AMZN, TSLA)
            'HD', 'MCD', 'NKE', 'SBUX', 'LOW', 'TGT', 'BKNG', 'MAR', 'EXPE', 'RCL', 'CCL', 'MGM', 
            'LVS', 'WYNN', 'F', 'GM', 'LUV', 'UAL', 'DAL',
            # Financials
            'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'BLK', 'AXP', 'V', 'MA', 'SCHW', 'USB', 'PNC', 
            'TRV', 'AIG', 'MET', 'PRU', 'MMC', 'AON', 'CB', 'BK', 'SPGI',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'OXY', 'PSX', 'MPC', 'VLO', 'HAL', 'KMI', 'WMB', 
            'OKE', 'DVN', 'APA',
            # Industrials
            'GE', 'HON', 'MMM', 'UNP', 'UPS', 'CAT', 'DE', 'LMT', 'BA', 'GD', 'NOC', 'WM', 'CSX', 
            'NSC', 'EMR', 'ETN', 'ITW', 'CMI', 'FDX', 'URI',
            # Materials
            'LIN', 'APD', 'SHW', 'FCX', 'NEM', 'NUE', 'DOW', 'DD', 'ECL', 'PPG', 'IP', 'ALB', 
            'MLM', 'VMC', 'BALL', 'CF'
        ],
        "Other_Stocks": []  # Will be filled with stocks not in the other categories
    }
    
    # Create a mapping from ticker to asset class
    asset_to_class = {}
    
    # First, map the explicitly defined assets to their classes
    for class_name, assets in asset_classes.items():
        for asset in assets:
            if asset in df.iloc[:, 0].values:
                asset_to_class[asset] = class_name
    
    # Assign all remaining assets to Other_Stocks
    for asset in df.iloc[:, 0].values:
        if asset not in asset_to_class:
            asset_to_class[asset] = "Other_Stocks"
    
    # Print asset counts by class
    asset_counts = {class_name: sum(1 for asset in asset_to_class if asset_to_class[asset] == class_name) 
                   for class_name in asset_classes.keys()}
    print("Asset counts by class:")
    for class_name, count in asset_counts.items():
        print(f"{class_name}: {count}")
    
    # Now calculate weights for each asset class for each allocation column
    # Get all columns except the first (which contains asset names)
    allocation_columns = df.columns[1:]
    
    # Initialize a DataFrame to store the results
    results = pd.DataFrame(index=asset_classes.keys(), columns=allocation_columns)
    
    # For each allocation scenario
    for column in allocation_columns:
        # Create a dictionary to store the sum of weights for each asset class
        class_weights = {class_name: 0.0 for class_name in asset_classes.keys()}
        
        # Sum up weights for each asset class
        for i, asset in enumerate(df.iloc[:, 0]):
            asset_class = asset_to_class.get(asset, "Other_Stocks")
            weight = df.loc[i, column]
            
            # Add the weight to the appropriate asset class
            if pd.notna(weight):  # Check for NaN values
                class_weights[asset_class] += weight
        
        # Normalize weights to sum to 100%
        total_weight = sum(class_weights.values())
        if total_weight > 0:
            for class_name in class_weights:
                class_weights[class_name] /= total_weight
        
        # Store the results
        for class_name, weight in class_weights.items():
            results.loc[class_name, column] = weight
    
    return results

def analyze_portfolio_allocations(csv_path):
    """
    Analyze portfolio allocations across different regimes, risk profiles, and time horizons.
    
    Parameters:
    -----------
    csv_path : str
        Path to the CSV file containing portfolio allocations
    """
    # Classify assets and calculate weights
    weights_df = classify_portfolio_assets(csv_path)
    
    # Print overall average weights per asset class
    average_weights = weights_df.mean(axis=1)
    print("\nAverage weights across all regimes and risk profiles:")
    for asset_class, weight in average_weights.items():
        print(f"{asset_class}: {weight:.2%}")
    
    # Extract regime, risk profile, and time horizon from column names
    # Format: "Regime X - Risk Y - Z days"
    regimes = set()
    risk_profiles = set()
    time_horizons = set()
    
    for column in weights_df.columns:
        parts = column.split(' - ')
        regimes.add(parts[0])
        risk_profiles.add(parts[1])
        time_horizons.add(parts[2])
    
    # Create DataFrames for analysis by regime, risk profile, and time horizon
    regime_df = pd.DataFrame(index=weights_df.index, columns=sorted(regimes))
    risk_profile_df = pd.DataFrame(index=weights_df.index, columns=sorted(risk_profiles))
    time_horizon_df = pd.DataFrame(index=weights_df.index, columns=sorted(time_horizons))
    
    # Calculate average weights for each dimension
    for column in weights_df.columns:
        parts = column.split(' - ')
        regime = parts[0]
        risk_profile = parts[1]
        time_horizon = parts[2]
        
        for asset_class in weights_df.index:
            # Add to regime average (initialize if not yet set)
            if pd.isna(regime_df.loc[asset_class, regime]):
                regime_df.loc[asset_class, regime] = weights_df.loc[asset_class, column]
            else:
                regime_df.loc[asset_class, regime] += weights_df.loc[asset_class, column]
            
            # Add to risk profile average
            if pd.isna(risk_profile_df.loc[asset_class, risk_profile]):
                risk_profile_df.loc[asset_class, risk_profile] = weights_df.loc[asset_class, column]
            else:
                risk_profile_df.loc[asset_class, risk_profile] += weights_df.loc[asset_class, column]
            
            # Add to time horizon average
            if pd.isna(time_horizon_df.loc[asset_class, time_horizon]):
                time_horizon_df.loc[asset_class, time_horizon] = weights_df.loc[asset_class, column]
            else:
                time_horizon_df.loc[asset_class, time_horizon] += weights_df.loc[asset_class, column]
    
    # Divide by the number of entries to get the average
    for regime in regimes:
        regime_count = sum(1 for col in weights_df.columns if col.startswith(regime))
        regime_df[regime] /= regime_count
    
    for risk_profile in risk_profiles:
        risk_count = sum(1 for col in weights_df.columns if f" - {risk_profile} - " in col)
        risk_profile_df[risk_profile] /= risk_count
    
    for time_horizon in time_horizons:
        time_count = sum(1 for col in weights_df.columns if col.endswith(time_horizon))
        time_horizon_df[time_horizon] /= time_count
    
    # Print summary results
    print("\nAverage weights by regime:")
    print(regime_df.round(4))
    
    print("\nAverage weights by risk profile:")
    print(risk_profile_df.round(4))
    
    print("\nAverage weights by time horizon:")
    print(time_horizon_df.round(4))
    
    # Create and save visualizations
    plt.figure(figsize=(15, 10))
    
    # Plot average weights across all scenarios
    plt.subplot(2, 2, 1)
    average_weights.plot(kind='bar', color='skyblue')
    plt.title('Average Asset Class Weights')
    plt.ylabel('Weight')
    plt.xticks(rotation=45)
    
    # Plot by regime
    plt.subplot(2, 2, 2)
    regime_df.T.plot(kind='bar', figsize=(10, 6))
    plt.title('Asset Allocation by Regime')
    plt.xlabel('Regime')
    plt.ylabel('Weight')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
    
    # Plot by risk profile
    plt.subplot(2, 2, 3)
    risk_profile_df.T.plot(kind='bar')
    plt.title('Asset Allocation by Risk Profile')
    plt.xlabel('Risk Profile')
    plt.ylabel('Weight')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
    
    # Plot by time horizon
    plt.subplot(2, 2, 4)
    time_horizon_df.T.plot(kind='bar')
    plt.title('Asset Allocation by Time Horizon')
    plt.xlabel('Time Horizon (days)')
    plt.ylabel('Weight')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
    
    plt.tight_layout()
    plt.savefig('charts/asset_class_allocation_charts/portfolio_allocations_analysis.png')
    
    weights_df.index.name = 'Asset Class'
    
    # Add weights column
    average_weights_df = weights_df.mean(axis=1)
    weights_df['weights'] = average_weights_df
    
    print("\nPortfolio weight:")
    print(weights_df['weights'])

    print("\nTotal portfolio weight:")
    print(sum(weights_df['weights']))

    weights_df =(weights_df['weights']*100).round(2)
    weights_df = weights_df.astype(float).round(2)

    return weights_df, regime_df, risk_profile_df, time_horizon_df

def create_stacked_bar_chart(df, title, filename):
    """
    Create a stacked bar chart to visualize asset allocations.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing weights by asset class
    title : str
        Title for the chart
    filename : str
        Filename to save the chart
    """
    plt.figure(figsize=(12, 8))
    
    # Transpose the dataframe for plotting
    df_plot = df.T
    
    # Create the stacked bar chart
    ax = df_plot.plot(kind='bar', stacked=True, figsize=(14, 8), 
                     colormap='tab10')
    
    # Add labels and title
    plt.title(title, fontsize=16)
    plt.xlabel('Category', fontsize=12)
    plt.ylabel('Allocation Weight', fontsize=12)
    
    # Add a legend with better positioning
    plt.legend(title='Asset Class', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Add value labels on each segment
    for i, (name, values) in enumerate(df_plot.iterrows()):
        bottom = 0
        for j, v in enumerate(values):
            if v > 0.02:  # Only show label if segment is large enough
                plt.text(i, bottom + v/2, f'{v:.1%}', ha='center', va='center',
                        fontsize=9, color='white', fontweight='bold')
            bottom += v
    
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

if __name__ == "__main__":
    # Path to the CSV file
    csv_path = "big_data/portfolio_allocations.csv"
    
    # Run the analysis
    weights_df, regime_df, risk_profile_df, time_horizon_df = analyze_portfolio_allocations(csv_path)
    
    # Save results to CSV files
    weights_df.to_csv("output/asset_class_weights.csv")
    # regime_df.to_csv("weights_by_regime.csv")
    risk_profile_df.to_csv("output/weights_by_risk_profile.csv")
    # time_horizon_df.to_csv("weights_by_time_horizon.csv")
    
    # Create additional visualizations
    create_stacked_bar_chart(regime_df, 'Asset Allocation by Market Regime', 'charts/asset_class_allocation_charts/regime_allocations.png')
    create_stacked_bar_chart(risk_profile_df, 'Asset Allocation by Risk Profile', 'charts/asset_class_allocation_charts/risk_profile_allocations.png')
    create_stacked_bar_chart(time_horizon_df, 'Asset Allocation by Time Horizon', 'charts/asset_class_allocation_charts/time_horizon_allocations.png')
    
    # Print summary of what categories we defined
    print("\nAsset Class Definitions:")
    print("1. MAG7: Major tech companies (Apple, Microsoft, Amazon, Nvidia, Google, Meta, Tesla)")
    print("2. Bonds: Fixed income securities")
    print("3. Commodities: Gold, oil, and other physical assets")
    print("4. Crypto: Bitcoin and crypto-related assets")
    print("5. Market Indices: Index ETFs and sector ETFs")
    print("6. Low Beta Stocks: Defensive sectors (Utilities, Consumer Staples, Healthcare, etc.)")
    print("7. High Beta Growth Stocks: Cyclical sectors (Technology ex-MAG7, Consumer Discretionary, etc.)")
    
    print("\nAnalysis complete. Results saved to CSV files and visualizations saved as PNG files.")