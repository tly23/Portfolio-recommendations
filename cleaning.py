# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 15:00:59 2025

@author: clark
"""
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# Load wide-form dataset
file_path = "wide_form_data.csv"
df = pd.read_csv(file_path)

# Ensure Date_x is in datetime format
df['Date_x'] = pd.to_datetime(df['Date_x'])
df = df[df['Date_x'] >= '2010-07-01']

# Print initial dataset information
print(f"Initial dataset shape: {df.shape} (rows, columns)")

# Add day of week for analysis
df['day_of_week'] = df['Date_x'].dt.day_name()

# Check nulls by day of week
nulls_by_day = df.groupby('day_of_week')[df.columns[~df.columns.isin(['Date_x', 'day_of_week', 'Month', 'Quarter'])]].apply(
    lambda x: x.isnull().sum().sum() / (len(x) * len(x.columns)) * 100
)
print("\nPercentage of nulls by day of week:")
print(nulls_by_day.sort_values(ascending=False))

# Step 1: Remove weekend rows
weekend_mask = df['day_of_week'].isin(['Saturday', 'Sunday'])
weekday_df = df[~weekend_mask].copy()
print(f"\nStep 1: Removing weekend rows")
print(f"Removed {weekend_mask.sum()} weekend rows")
print(f"New shape: {weekday_df.shape}")

# Visualize nulls by day after weekend removal
plt.figure(figsize=(10, 5))
nulls_by_day.sort_values().plot(kind='bar', color='skyblue')
plt.title('Percentage of Nulls by Day of Week')
plt.ylabel('Null Percentage (%)')
plt.tight_layout()
plt.savefig('charts/cleaning_charts/nulls_by_day.png')
print("✅ Created visualization of nulls by day: 'charts/cleaning_charts/nulls_by_day.png'")

# Step 2: Check for US market holidays
# Identify days with high percentage of nulls that might be holidays
weekday_df['null_percentage'] = weekday_df.isnull().mean(axis=1) * 100
potential_holidays = weekday_df[weekday_df['null_percentage'] > 80]
if len(potential_holidays) > 0:
    print(f"\nPotential market holidays found: {len(potential_holidays)} days")
    print("Sample of potential holidays:")
    print(potential_holidays[['Date_x', 'day_of_week', 'null_percentage']].head())
    
    # Remove these potential holidays
    weekday_df = weekday_df[weekday_df['null_percentage'] <= 80]
    print(f"After removing potential holidays: {weekday_df.shape}")

# Step 3: Handle remaining nulls
# Identify columns with high null percentages
null_percentages = weekday_df.isnull().mean() * 100
high_null_cols = null_percentages[null_percentages > 20].index.tolist()

# Remove columns with too many nulls
if high_null_cols:
    print(f"\nRemoving {len(high_null_cols)} columns with >20% nulls")
    weekday_df = weekday_df.drop(columns=high_null_cols)

# Identify numeric columns for imputation
date_cols = ['Date_x', 'day_of_week', 'Month', 'Quarter', 'null_percentage']
numeric_cols = weekday_df.select_dtypes(include=['float64', 'int64']).columns
numeric_cols = [col for col in numeric_cols if col not in date_cols]

# Impute remaining nulls using forward fill then backward fill (time series appropriate)
print("\nImputing remaining nulls in numeric columns...")
for col in numeric_cols:
    if weekday_df[col].isnull().any():
        # First try forward fill (most recent value)
        weekday_df[col] = weekday_df[col].ffill()#.fillna(method='ffill')
        # Then backward fill for any remaining (beginning of series)
        weekday_df[col] = weekday_df[col].bfill()#.fillna(method='bfill')

# Check if we still have nulls
remaining_nulls = weekday_df[numeric_cols].isnull().sum().sum()
if remaining_nulls > 0:
    print(f"Warning: {remaining_nulls} nulls remain after forward/backward fill")
    print("Using median imputation for any remaining nulls...")
    imputer = SimpleImputer(strategy='median')
    weekday_df[numeric_cols] = imputer.fit_transform(weekday_df[numeric_cols])

# Step 4: Prepare for K-means clustering
# Standardize numeric features (essential for K-means)
print("\nStandardizing numeric features for K-means...")
scaler = StandardScaler()
weekday_df[numeric_cols] = scaler.fit_transform(weekday_df[numeric_cols])

# Drop columns we don't need for clustering
columns_to_drop = ['day_of_week', 'null_percentage']
final_df = weekday_df.drop(columns=[col for col in columns_to_drop if col in weekday_df.columns])

# Final check
print(f"\nFinal dataset shape: {final_df.shape} (rows, columns)")
print(f"Number of features for clustering: {len(numeric_cols)}")
print(f"Numeric columns sample: {numeric_cols[:5]}...")
print(f"Date range: {final_df['Date_x'].min()} to {final_df['Date_x'].max()}")

# Save the clean dataset
final_df.to_csv("clean_weekday_data.csv", index=False)
print("\n✅ Clean dataset saved to 'clean_weekday_data.csv'")

# Create a small report of dataset characteristics
stocks = set()
metrics = set()
for col in numeric_cols:
    if '_' in col:
        parts = col.split('_')
        stock = parts[0]
        metric = '_'.join(parts[1:])
        stocks.add(stock)
        metrics.add(metric)

print(f"\nDataset contains {len(stocks)} stocks with {len(metrics)} metrics per stock")
print(f"Sample stocks: {list(stocks)[:5]}...")
print(f"Metrics: {list(metrics)}")

# Create visualization of remaining data completeness
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.hist(final_df['Date_x'].dt.year, bins=20)
plt.title('Distribution by Year')
plt.xlabel('Year')
plt.ylabel('Count')

plt.subplot(1, 2, 2)
plt.hist(final_df['Date_x'].dt.month, bins=12)
plt.title('Distribution by Month')
plt.xlabel('Month')
plt.ylabel('Count')

plt.tight_layout()
plt.savefig('charts/cleaning_charts/data_distribution.png')
print("✅ Created visualization of data distribution: 'charts/cleaning_charts/data_distribution.png'")

print("\nThe dataset is now ready for K-means clustering!")