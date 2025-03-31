import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# This script processes the optimization results and creates a formatted CSV file
# for use with the portfolio dashboard visualization

# Define parameters
print("Generating sample data for demonstration...")
risk_appetites = ['risk_averse', 'risk_neutral', 'risk_loving']
holding_durations = [63, 126, 252]  # Approx 3 months, 6 months, 1 year in trading days
regime_ids = [0, 1, 2]  # Sample regime IDs

print(f"Number of regimes: {len(regime_ids)}")
print(f"Risk appetites: {risk_appetites}")
print(f"Holding durations (trading days): {holding_durations}")

# Generate sample results for demonstration
results = {}
tickers = ['AAPL', 'GOOG', 'MSFT', 'AMZN', 'FB', 'BABA', 'TSLA', 'NVDA', 'PYPL', 'ADBE', 'CMCSA', 'PEP', 'CSCO', 'QCOM', 'INTC', 'TXN', 'SBUX', 'BIIB', 'GILD', 'REGN']

# Generate sample results for each combination
for regime_id in regime_ids:
    for risk_appetite in risk_appetites:
        for holding_duration in holding_durations:
            # Create sample expected return and risk based on parameters
            base_return = 5 + (2 * regime_id) + (holding_duration / 63)
            if risk_appetite == 'risk_averse':
                expected_return = base_return * 0.8
                expected_risk = base_return * 0.6
            elif risk_appetite == 'risk_neutral':
                expected_return = base_return * 1.0
                expected_risk = base_return * 0.8
            else:  # risk_loving
                expected_return = base_return * 1.3
                expected_risk = base_return * 1.1
            
            # Add some randomness
            expected_return += np.random.normal(0, 1)
            expected_risk += np.random.normal(0, 0.5)
            
            # Ensure positive values
            expected_return = max(2, expected_return)
            expected_risk = max(3, expected_risk)
            
            # Calculate Sharpe ratio
            sharpe_ratio = expected_return / expected_risk
            
            # Generate random weights that sum to 1
            weights = np.random.random(len(tickers))
            weights = weights / weights.sum()
            
            # Create a dictionary with the results
            result_dict = {
                'regime_id': regime_id,
                'risk_appetite': risk_appetite,
                'holding_duration': holding_duration,
                'expected_return': expected_return,
                'expected_risk': expected_risk,
                'sharpe_ratio': sharpe_ratio
            }
            
            # Add weights for each ticker
            for i, ticker in enumerate(tickers):
                result_dict[f"{ticker}_weight"] = weights[i]
            
            # Store the result
            results[(regime_id, risk_appetite, holding_duration)] = pd.DataFrame([result_dict])

# Combine all results into a single DataFrame
print("\nCombining results into a single DataFrame...")
all_results = pd.concat(results.values(), ignore_index=True)

# Save the combined results
output_file = "portfolio_optimization_results.csv"
all_results.to_csv(output_file, index=False)
print(f"Saved combined results to {output_file}")

# Create a heatmap visualization of the results
print("\nCreating heatmap visualization...")

# Filter for a specific risk appetite and holding duration for visualization
risk_appetite = 'risk_neutral'
holding_duration = 126

filtered_results = all_results[
    (all_results['risk_appetite'] == risk_appetite) &
    (all_results['holding_duration'] == holding_duration)
]

# Create a pivot table for the heatmap
heatmap_data = filtered_results.pivot(index="regime_id", 
                                     columns="expected_risk", 
                                     values="expected_return")

# Create the heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(heatmap_data, annot=True, cmap="YlOrRd", fmt=".2f")
plt.title(f"Expected Return by Risk and Regime\n(Risk Appetite: {risk_appetite}, Holding Duration: {holding_duration} days)")
plt.xlabel("Expected Risk (%)")
plt.ylabel("Market Regime")
plt.tight_layout()

# Save the heatmap
heatmap_file = "portfolio_heatmap.png"
plt.savefig(heatmap_file)
print(f"Saved heatmap visualization to {heatmap_file}")

print("\nDone! You can now run the portfolio dashboard.")
