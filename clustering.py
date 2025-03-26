# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 15:47:21 2025

@author: Jia Qi Xiao
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.signal import savgol_filter
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Load the engineered features dataset
file_path = "engineered_features.csv"
df = pd.read_csv(file_path)
df['Date_x'] = pd.to_datetime(df['Date_x'])
print(f"Loaded dataset with shape: {df.shape}")

# Select features for clustering
# We'll focus on market-wide metrics to identify market regimes
regime_features = [
    'Market_Return', 'Market_Volatility', 'Average_RSI',
    'Market_Liquidity', 'Stocks_Above_MA200',
    'Inflation', 'Unemployment Rate'
]

# Ensure all selected features exist in the dataset
regime_features = [col for col in regime_features if col in df.columns]
print(f"Using {len(regime_features)} features for regime clustering:")
print(regime_features)

# Create feature matrix
X = df[regime_features].copy()

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print("Features standardized")

# Optional: Dimensionality reduction with PCA
# This can help visualize the clusters and improve clustering quality
print("\nPerforming PCA for dimensionality reduction...")
pca = PCA(n_components=0.90)  # Capture 90% of variance
X_pca = pca.fit_transform(X_scaled)

print(f"Reduced from {X_scaled.shape[1]} features to {X_pca.shape[1]} principal components")
print(f"Explained variance ratio: {pca.explained_variance_ratio_}")
print(f"Total explained variance: {sum(pca.explained_variance_ratio_)*100:.2f}%")

# Determine optimal number of clusters using silhouette scores
print("\nDetermining optimal number of clusters...")
silhouette_scores = []
k_range = range(2, 11)  # Try between 2 and 10 clusters

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_pca)
    silhouette_avg = silhouette_score(X_pca, cluster_labels)
    silhouette_scores.append(silhouette_avg)
    print(f"For n_clusters = {k}, the silhouette score is {silhouette_avg:.3f}")

# Plot silhouette scores
plt.figure(figsize=(10, 6))
plt.plot(k_range, silhouette_scores, 'o-')
plt.xlabel('Number of clusters (k)')
plt.ylabel('Silhouette Score')
plt.title('Silhouette Score Method for Optimal k')
plt.grid(True)
plt.savefig('silhouette_scores.png')
print("✅ Saved silhouette scores plot to 'silhouette_scores.png'")

# Select optimal k (highest silhouette score)
optimal_k = k_range[np.argmax(silhouette_scores)]
print(f"\nOptimal number of clusters: {optimal_k}")

# Perform final clustering with optimal k
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df['regime'] = kmeans.fit_predict(X_pca)
print(f"Clustered data into {optimal_k} market regimes")

# Count observations in each regime
regime_counts = df['regime'].value_counts().sort_index()
print("\nNumber of days in each regime:")
for regime, count in regime_counts.items():
    print(f"Regime {regime}: {count} days ({count/len(df)*100:.1f}%)")

# Create a smoothed regime time series (to reduce regime flickering)
# This uses a Savitzky-Golay filter for smoothing
regime_time_series = pd.Series(index=df['Date_x'], data=df['regime'].values)
window_length = 21  # ~1 month of trading days
poly_order = 3  # polynomial order for smoothing

# Function to smooth regime assignments
def smooth_regimes(regimes, window_length=21, iterations=3):
    """
    Smooth regime assignments to reduce flickering
    Uses a mode-based rolling window approach
    """
    smoothed = regimes.copy()
    
    for _ in range(iterations):
        # For each point, count neighboring regimes and take the most common
        for i in range(len(smoothed)):
            start = max(0, i - window_length//2)
            end = min(len(smoothed), i + window_length//2 + 1)
            
            # Get window values and find most common
            window = smoothed[start:end]
            counts = np.bincount(window)
            
            # Set to most common value in window
            smoothed[i] = np.argmax(counts)
    
    return smoothed

# Smooth the regimes to reduce flickering
df['smoothed_regime'] = smooth_regimes(df['regime'].values)
print("Created smoothed regime assignments")

# Plot the regimes over time
plt.figure(figsize=(15, 10))

# Plot 1: Original Regime Assignments
plt.subplot(2, 1, 1)
plt.scatter(df['Date_x'], df['regime'], c=df['regime'], cmap='viridis', 
            alpha=0.7, s=10, marker='o')
plt.colorbar(label='Regime')
plt.title('Market Regimes Over Time (Original)')
plt.ylabel('Regime')
plt.grid(True, alpha=0.3)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.gca().xaxis.set_major_locator(mdates.YearLocator())

# Plot 2: Smoothed Regime Assignments
plt.subplot(2, 1, 2)
plt.scatter(df['Date_x'], df['smoothed_regime'], c=df['smoothed_regime'], 
            cmap='viridis', alpha=0.7, s=10, marker='o')
plt.colorbar(label='Regime')
plt.title('Market Regimes Over Time (Smoothed)')
plt.xlabel('Date')
plt.ylabel('Regime')
plt.grid(True, alpha=0.3)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
plt.gca().xaxis.set_major_locator(mdates.YearLocator())

plt.tight_layout()
plt.savefig('market_regimes_timeline.png')
print("✅ Saved regime timeline plot to 'market_regimes_timeline.png'")

# Analyze characteristics of each regime
regime_analysis = df.groupby('smoothed_regime')[regime_features].mean()

# Calculate average returns during each regime (using a 20-day forward window)
df['forward_return_20d'] = df['Market_Return'].rolling(window=20).sum().shift(-20)
regime_returns = df.groupby('smoothed_regime')['forward_return_20d'].mean() * 100  # as percentage

# Combine regime characteristics with returns
regime_analysis['Avg_20d_Forward_Return_%'] = regime_returns

print("\nRegime Characteristics:")
print(regime_analysis)

# Plot regime characteristics heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(regime_analysis, annot=True, cmap='coolwarm', center=0, fmt='.2f')
plt.title('Market Regime Characteristics')
plt.tight_layout()
plt.savefig('regime_characteristics.png')
print("✅ Saved regime characteristics heatmap to 'regime_characteristics.png'")

# Plot typical feature values by regime
plt.figure(figsize=(15, 10))
for i, feature in enumerate(regime_features):
    plt.subplot(3, 3, i+1)
    
    # Use box plots to show distribution of values in each regime
    sns.boxplot(x='smoothed_regime', y=feature, data=df)
    plt.title(f'{feature} by Regime')
    plt.xlabel('Regime')
    plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('regime_feature_distributions.png')
print("✅ Saved regime feature distributions to 'regime_feature_distributions.png'")

# Visualize transitions between regimes with sankey diagram
try:
    import plotly.graph_objects as go
    from plotly.offline import plot
    
    # Create transition counts
    transitions = np.zeros((optimal_k, optimal_k))
    
    # Get current day's regime and next day's regime
    current_regimes = df['smoothed_regime'].values[:-1]
    next_regimes = df['smoothed_regime'].values[1:]
    
    # Count transitions
    for i in range(len(current_regimes)):
        transitions[current_regimes[i], next_regimes[i]] += 1
    
    # Create source, target and value lists for sankey
    source = []
    target = []
    value = []
    
    for i in range(optimal_k):
        for j in range(optimal_k):
            if transitions[i, j] > 0:
                source.append(i)
                target.append(j)
                value.append(transitions[i, j])
    
    # Create the sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=[f"Regime {i}" for i in range(optimal_k)],
            color="blue"
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )])
    
    fig.update_layout(title_text="Regime Transitions", font_size=10)
    plot(fig, filename='regime_transitions.html', auto_open=False)
    print("✅ Saved regime transitions visualization to 'regime_transitions.html'")
except:
    print("Note: Plotly library not available, skipping transition diagram")

# Save results
df[['Date_x', 'regime', 'smoothed_regime']].to_csv('market_regimes.csv', index=False)
print("✅ Saved regime assignments to 'market_regimes.csv'")

# Save the full dataset with regime assignments
df.to_csv('full_dataset_with_regimes.csv', index=False)
print("✅ Saved full dataset with regime assignments to 'full_dataset_with_regimes.csv'")

print("\nRegime clustering complete!")