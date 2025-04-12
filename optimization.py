import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import minimize
import itertools
from datetime import timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Load data with regimes
file_path = "big_data/full_dataset_with_regimes.csv"
df = pd.read_csv(file_path)
df['Date_x'] = pd.to_datetime(df['Date_x'])
print(f"Loaded dataset with shape: {df.shape}")

# Get list of tickers from column names
def get_tickers(df):
    # Get columns ending with '_Return'
    return_cols = [col for col in df.columns if col.endswith('_Return')]
    # Extract ticker names
    tickers = [col.split('_')[0] for col in return_cols 
               if not col.startswith('Market') and not col.startswith('Average')]
    return tickers

tickers = get_tickers(df)
print(f"Found {len(tickers)} tickers for optimization")

# Define parameters
risk_appetites = ['risk_averse', 'risk_neutral', 'risk_loving']
holding_durations = [63, 126, 252]  # Approx 3 months, 6 months, 1 year in trading days
regime_ids = sorted(df['smoothed_regime'].unique())

print(f"Number of regimes: {len(regime_ids)}")
print(f"Risk appetites: {risk_appetites}")
print(f"Holding durations (trading days): {holding_durations}")

# Define risk constraints based on risk appetite (as multipliers of min variance portfolio risk)
risk_constraints = {
    'risk_averse': 1.2,      # 20% more risk than minimum variance
    'risk_neutral': 2.0,     # Twice the risk of minimum variance
    'risk_loving': 3.0       # Three times the risk of minimum variance
}

# Create rolling returns for each holding duration
print("Calculating rolling returns for different holding durations...")
for duration in holding_durations:
    for ticker in tickers:
        col_name = f"{ticker}_Return"
        if col_name in df.columns:
            # Calculate rolling cumulative returns
            df[f"{ticker}_Return_{duration}d"] = df[col_name].rolling(window=duration).sum()

# Mean-Variance optimization function
def optimize_portfolio(returns, risk_appetite, cov_matrix=None):
    """
    Optimize portfolio weights using mean-variance optimization
    
    Parameters:
    - returns: pandas Series of expected returns for each asset
    - risk_appetite: one of 'risk_averse', 'risk_neutral', 'risk_loving'
    - cov_matrix: covariance matrix of returns
    
    Returns:
    - weights: optimal portfolio weights
    - expected_return: expected portfolio return
    - expected_risk: expected portfolio risk (std dev)
    """
    n_assets = len(returns)
    
    if cov_matrix is None:
        # If no covariance matrix provided, assume diagonal matrix for simplicity
        cov_matrix = np.diag(np.ones(n_assets) * 0.01)
    
    # Function to minimize negative Sharpe Ratio (for risk-neutral)
    # or negative return subject to risk constraint (for risk_averse/loving)
    def neg_sharpe_ratio(weights):
        weights = np.array(weights)
        portfolio_return = np.sum(returns * weights)
        portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        # Avoid division by zero
        if portfolio_std_dev == 0:
            return 0
        
        return -portfolio_return / portfolio_std_dev
    
    # Function to minimize negative return
    def neg_return(weights):
        return -np.sum(returns * weights)
    
    # Function to calculate portfolio variance
    def portfolio_variance(weights):
        return np.dot(weights.T, np.dot(cov_matrix, weights))
    
    # Constraint that weights sum to 1
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    # Bounds for each weight (0 to 1)
    bounds = tuple((0, 1) for _ in range(n_assets))
    
    # Initial guess (equal weights)
    initial_weights = np.ones(n_assets) / n_assets
    
    # Find minimum variance portfolio first
    min_var_result = minimize(
        portfolio_variance, 
        initial_weights, 
        method='SLSQP', 
        bounds=bounds, 
        constraints=constraints
    )
    
    min_var_risk = np.sqrt(min_var_result['fun'])
    
    # Set target risk based on risk appetite
    if risk_appetite == 'risk_neutral':
        # Maximize Sharpe ratio for risk-neutral
        result = minimize(
            neg_sharpe_ratio, 
            initial_weights, 
            method='SLSQP', 
            bounds=bounds, 
            constraints=constraints
        )
    else:
        # Set risk constraint based on risk appetite
        risk_multiplier = risk_constraints[risk_appetite]
        target_risk = min_var_risk * risk_multiplier
        
        # Add risk constraint
        risk_constraint = {
            'type': 'ineq',
            'fun': lambda x: target_risk**2 - portfolio_variance(x)
        }
        
        # Maximize return subject to risk constraint
        result = minimize(
            neg_return, 
            initial_weights, 
            method='SLSQP', 
            bounds=bounds, 
            constraints=[constraints, risk_constraint]
        )
    
    # Get optimized weights
    weights = result['x']
    
    # Calculate expected return and risk
    expected_return = np.sum(returns * weights)
    expected_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    
    return weights, expected_return, expected_risk

# Function to run optimization for specific regime, risk appetite, and holding duration
def optimize_by_regime(df, regime_id, risk_appetite, holding_duration):
    """
    Optimize portfolio for specific market regime, risk appetite, and holding duration
    
    Parameters:
    - df: dataframe with return data and regime classifications
    - regime_id: ID of the market regime to optimize for
    - risk_appetite: one of 'risk_averse', 'risk_neutral', 'risk_loving'
    - holding_duration: holding period in trading days
    
    Returns:
    - weights_dict: dictionary mapping tickers to optimal weights
    - portfolio_stats: dictionary with portfolio statistics
    """
    # Filter data for the specific regime
    regime_data = df[df['smoothed_regime'] == regime_id].copy()
    
    # Get returns for the specific holding duration
    return_columns = [f"{ticker}_Return_{holding_duration}d" for ticker in tickers]
    
    # Filter out any columns that don't exist
    return_columns = [col for col in return_columns if col in regime_data.columns]
    
    # Drop NaN values
    returns_df = regime_data[return_columns].dropna()
    
    # If not enough data, return empty results
    if len(returns_df) < 30:
        print(f"Warning: Not enough data for regime {regime_id}, holding duration {holding_duration}")
        return {}, {}
    
    # Calculate mean returns and covariance matrix
    mean_returns = returns_df.mean()
    cov_matrix = returns_df.cov()
    
    # Extract ticker names from return column names
    opt_tickers = [col.split('_Return')[0] for col in return_columns]
    
    # Run optimization
    try:
        weights, expected_return, expected_risk = optimize_portfolio(
            mean_returns, risk_appetite, cov_matrix
        )
        
        # Create dictionary mapping tickers to weights
        weights_dict = {ticker: weight for ticker, weight in zip(opt_tickers, weights)}
        
        # Calculate annualized statistics
        annual_factor = 252 / holding_duration
        annual_return = expected_return * annual_factor
        annual_risk = expected_risk * np.sqrt(annual_factor)
        sharpe_ratio = annual_return / annual_risk if annual_risk > 0 else 0
        
        # Calculate portfolio statistics
        portfolio_stats = {
            'expected_return': expected_return,
            'expected_risk': expected_risk,
            'annual_return': annual_return,
            'annual_risk': annual_risk,
            'sharpe_ratio': sharpe_ratio,
            'n_assets': len(weights[weights > 0.01])  # Number of assets with >1% allocation
        }
        
        return weights_dict, portfolio_stats
    except Exception as e:
        print(f"Error optimizing portfolio for regime {regime_id}, risk {risk_appetite}, duration {holding_duration}: {e}")
        return {}, {}

# Function to create parameter combinations
def get_parameter_combinations():
    return list(itertools.product(regime_ids, risk_appetites, holding_durations))

# Run optimization for all combinations
print("Running portfolio optimization for all combinations...")
results = {}
portfolio_weights = {}

for regime_id, risk_appetite, holding_duration in get_parameter_combinations():
    print(f"Optimizing for: Regime {regime_id}, {risk_appetite}, {holding_duration} days...")
    
    # Create key for this parameter combination
    key = f"regime_{regime_id}_{risk_appetite}_{holding_duration}d"
    
    # Run optimization
    weights, stats = optimize_by_regime(df, regime_id, risk_appetite, holding_duration)
    
    # Store results
    results[key] = stats
    portfolio_weights[key] = weights

# Convert results to DataFrame for analysis
results_df = pd.DataFrame.from_dict(results, orient='index')

# Create a new MultiIndex manually - fix for the error
# First, parse the keys to extract components
indices = []
for key in results_df.index:
    parts = key.split('_')
    regime = parts[1]
    risk = '_'.join(parts[2:-1])  # In case risk has underscores
    duration = parts[-1].replace('d', '')
    indices.append((regime, risk, duration))

# Create proper MultiIndex
results_df.index = pd.MultiIndex.from_tuples(indices, names=['regime', 'risk_appetite', 'holding_duration'])

# Display summary of results
print("\nPortfolio Optimization Results Summary:")
if not results_df.empty:
    print(results_df[['annual_return', 'annual_risk', 'sharpe_ratio', 'n_assets']])
else:
    print("No valid optimization results found.")

# Create visualization of portfolio performance metrics
if not results_df.empty:
    # Create subplots
    fig, axes = plt.subplots(len(regime_ids), 3, figsize=(18, 6*len(regime_ids)))
    
    # Handle case with only one regime
    if len(regime_ids) == 1:
        axes = np.array([axes])
    
    # Plot for each regime
    for i, regime_id in enumerate(regime_ids):
        # Get data for this regime
        try:
            regime_data = results_df.xs(str(regime_id), level='regime')
            
            # Expected Return by risk appetite and holding duration
            ax1 = axes[i, 0]
            for risk in risk_appetites:
                try:
                    risk_data = regime_data.xs(risk, level='risk_appetite')
                    ax1.plot(risk_data.index, risk_data['annual_return']*100, 'o-', label=risk)
                except (KeyError, ValueError) as e:
                    print(f"Warning: Could not plot data for regime {regime_id}, risk {risk}: {e}")
            
            ax1.set_title(f'Regime {regime_id}: Annual Return (%)')
            ax1.set_xlabel('Holding Duration (days)')
            ax1.set_ylabel('Annual Return (%)')
            ax1.grid(True)
            ax1.legend()
            
            # Expected Risk by risk appetite and holding duration
            ax2 = axes[i, 1]
            for risk in risk_appetites:
                try:
                    risk_data = regime_data.xs(risk, level='risk_appetite')
                    ax2.plot(risk_data.index, risk_data['annual_risk']*100, 'o-', label=risk)
                except (KeyError, ValueError) as e:
                    print(f"Warning: Could not plot data for regime {regime_id}, risk {risk}: {e}")
            
            ax2.set_title(f'Regime {regime_id}: Annual Risk (%)')
            ax2.set_xlabel('Holding Duration (days)')
            ax2.set_ylabel('Annual Risk (%)')
            ax2.grid(True)
            ax2.legend()
            
            # Sharpe Ratio by risk appetite and holding duration
            ax3 = axes[i, 2]
            for risk in risk_appetites:
                try:
                    risk_data = regime_data.xs(risk, level='risk_appetite')
                    ax3.plot(risk_data.index, risk_data['sharpe_ratio'], 'o-', label=risk)
                except (KeyError, ValueError) as e:
                    print(f"Warning: Could not plot data for regime {regime_id}, risk {risk}: {e}")
            
            ax3.set_title(f'Regime {regime_id}: Sharpe Ratio')
            ax3.set_xlabel('Holding Duration (days)')
            ax3.set_ylabel('Sharpe Ratio')
            ax3.grid(True)
            ax3.legend()
            
        except (KeyError, ValueError) as e:
            print(f"Warning: Could not process data for regime {regime_id}: {e}")
    
    plt.tight_layout()
    plt.savefig('charts/optimization_charts/portfolio_performance_by_regime.png')
    print("✅ Saved portfolio performance visualization to 'charts/optimization_charts/portfolio_performance_by_regime.png'")

# Create weight visualizations for each combination
print("\nCreating visualizations of portfolio weights...")

# Number of top holdings to show in visuals
n_top_holdings = 10

# Prepare a folder for weight visuals
import os
if not os.path.exists('portfolio_weights'):
    os.makedirs('portfolio_weights')

# Create a summary of top holdings
top_holdings_summary = {}

# Generate weight visualizations for each portfolio
for params, weights in portfolio_weights.items():
    if not weights:  # Skip empty portfolios
        continue
        
    # Convert to DataFrame for easier handling
    weights_df = pd.DataFrame(list(weights.items()), columns=['Ticker', 'Weight'])
    weights_df = weights_df.sort_values('Weight', ascending=False)
    
    # Store summary of top holdings
    top_holdings_summary[params] = weights_df.head(n_top_holdings)['Ticker'].tolist()
    
    # Create bar chart of weights
    plt.figure(figsize=(12, 8))
    plt.barh(weights_df['Ticker'].head(n_top_holdings), 
             weights_df['Weight'].head(n_top_holdings) * 100)
    plt.xlabel('Weight (%)')
    plt.ylabel('Ticker')
    plt.title(f'Top {n_top_holdings} Holdings - {params}')
    plt.grid(True, axis='x')
    plt.tight_layout()
    plt.savefig(f'charts/portfolio_weights/{params}_weights.png')
    plt.close()

# Create a single consolidated PDF with all portfolios
try:
    from matplotlib.backends.backend_pdf import PdfPages
    
    with PdfPages('all_portfolio_weights.pdf') as pdf:
        for params, weights in portfolio_weights.items():
            if not weights:  # Skip empty portfolios
                continue
                
            # Convert to DataFrame for easier handling
            weights_df = pd.DataFrame(list(weights.items()), columns=['Ticker', 'Weight'])
            weights_df = weights_df.sort_values('Weight', ascending=False)
            
            # Create bar chart of weights
            plt.figure(figsize=(12, 8))
            plt.barh(weights_df['Ticker'].head(n_top_holdings), 
                     weights_df['Weight'].head(n_top_holdings) * 100)
            plt.xlabel('Weight (%)')
            plt.ylabel('Ticker')
            plt.title(f'Top {n_top_holdings} Holdings - {params}')
            plt.grid(True, axis='x')
            plt.tight_layout()
            pdf.savefig()
            plt.close()
            
    print("✅ Created consolidated PDF of all portfolio weights: 'all_portfolio_weights.pdf'")
except Exception as e:
    print(f"Note: Could not create PDF: {e}. Individual portfolio visualizations are in the 'portfolio_weights' folder.")

# Save results to CSV files if there are valid results
if not results_df.empty:
    results_df.to_csv('big_data/portfolio_optimization_results.csv')
    print("✅ Saved portfolio optimization results to 'big_data/portfolio_optimization_results.csv'")

# Create a more user-friendly portfolio allocation file
portfolio_allocations = pd.DataFrame()

for params, weights in portfolio_weights.items():
    if not weights:
        continue
        
    # Parse parameters
    parts = params.split('_')
    regime_id = parts[1]
    # Handle case where risk_appetite might have multiple underscores
    duration_part = parts[-1]
    risk_parts = parts[2:-1]
    risk_appetite = '_'.join(risk_parts)
    holding_duration = duration_part.replace('d', '')
    
    # Create a neat identifier
    portfolio_id = f"Regime {regime_id} - {risk_appetite.replace('_', ' ').title()} - {holding_duration} days"
    
    # Convert weights to Series
    weight_series = pd.Series(weights, name=portfolio_id)
    
    # Add to the DataFrame
    portfolio_allocations = pd.concat([portfolio_allocations, weight_series], axis=1)

# Save allocations
if not portfolio_allocations.empty:
    portfolio_allocations.to_csv('big_data/portfolio_allocations.csv')
    print("✅ Saved portfolio allocations to 'big_data/portfolio_allocations.csv'")

# Create a function to get the optimal portfolio based on user inputs
def get_optimal_portfolio(regime_id, risk_appetite, holding_duration):
    """
    Get the optimal portfolio for a specific set of parameters
    
    Parameters:
    - regime_id: market regime ID (0, 1, 2)
    - risk_appetite: 'risk_averse', 'risk_neutral', or 'risk_loving'
    - holding_duration: 63 (3 months), 126 (6 months), or 252 (1 year)
    
    Returns:
    - weights: dictionary of ticker->weight
    - stats: dictionary of portfolio statistics
    """
    key = f"regime_{regime_id}_{risk_appetite}_{holding_duration}d"
    
    if key in portfolio_weights and key in results:
        return portfolio_weights[key], results[key]
    else:
        return {}, {}

# Example usage demonstration
print("\nExample usage of the optimization results:")
if regime_ids:
    current_regime = regime_ids[0]  # Using the first regime as an example
    example_risk = 'risk_neutral'
    example_duration = 126  # 6 months

    weights, stats = get_optimal_portfolio(current_regime, example_risk, example_duration)

    print(f"Optimal portfolio for Regime {current_regime}, {example_risk}, {example_duration} days:")
    if stats:
        print(f"Expected annual return: {stats.get('annual_return', 0)*100:.2f}%")
        print(f"Expected annual risk: {stats.get('annual_risk', 0)*100:.2f}%")
        print(f"Sharpe ratio: {stats.get('sharpe_ratio', 0):.2f}")
        print(f"Number of holdings: {stats.get('n_assets', 0)}")

        # Print top 5 holdings
        if weights:
            sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
            print("\nTop 5 holdings:")
            for ticker, weight in sorted_weights[:5]:
                print(f"{ticker}: {weight*100:.2f}%")
        else:
            print("No valid portfolio found for the example parameters.")
    else:
        print("No valid portfolio statistics found for the example parameters.")
else:
    print("No regime IDs found to demonstrate optimization.")

print("\nPortfolio optimization complete!")