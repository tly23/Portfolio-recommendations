import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

# Set page configuration
st.set_page_config(page_title="Portfolio Recommendations", layout="wide")

# Load the dataset with optimized portfolios
try:
    file_path = "full_dataset_with_regimes.csv"
    df = pd.read_csv(file_path)
    df['Date_x'] = pd.to_datetime(df['Date_x'])
    
    # Load optimization results
    portfolio_results = pd.read_csv("portfolio_optimization_results.csv")
    
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please make sure the optimization has been run and the files exist.")
    data_loaded = False

# Page title and description
st.title("Portfolio Recommendation Dashboard")
st.markdown("""
This dashboard helps you visualize optimized portfolios based on your risk profile and investment horizon.
The heatmap shows the risk-return tradeoff across different market regimes.
""")

# Sidebar for user inputs
st.sidebar.header("Portfolio Preferences")

# Risk appetite selection
risk_appetite = st.sidebar.selectbox(
    "Select your risk profile:",
    options=["risk_averse", "risk_neutral", "risk_loving"],
    format_func=lambda x: {
        "risk_averse": "Risk Averse (Conservative)",
        "risk_neutral": "Risk Neutral (Balanced)",
        "risk_loving": "Risk Loving (Aggressive)"
    }[x]
)

# Holding duration selection
holding_duration = st.sidebar.selectbox(
    "Select your investment horizon:",
    options=[63, 126, 252],
    format_func=lambda x: {
        63: "3 Months (Short-term)",
        126: "6 Months (Medium-term)",
        252: "1 Year (Long-term)"
    }[x]
)

# Display current market regime if data is loaded
if data_loaded:
    # Get the most recent regime
    latest_date = df['Date_x'].max()
    current_regime = df[df['Date_x'] == latest_date]['smoothed_regime'].values[0]
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Current Market Information")
    st.sidebar.markdown(f"**Current Market Regime:** Regime {current_regime}")
    
    # Filter portfolio results for the selected risk appetite and holding duration
    filtered_results = portfolio_results[
        (portfolio_results['risk_appetite'] == risk_appetite) &
        (portfolio_results['holding_duration'] == holding_duration)
    ]
    
    # Main content area - split into two columns
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Portfolio Risk-Return Heatmap")
        
        # Create heatmap data
        heatmap_data = filtered_results.pivot(index="expected_risk", 
                                             columns="expected_return", 
                                             values="sharpe_ratio")
        
        # Create a custom colorscale that highlights the best Sharpe ratios
        colorscale = [
            [0, 'rgb(255,255,255)'],      # White for low values
            [0.3, 'rgb(255,220,220)'],     # Light red
            [0.5, 'rgb(255,150,150)'],     # Medium red
            [0.7, 'rgb(255,100,100)'],     # Stronger red
            [0.85, 'rgb(255,50,50)'],      # Even stronger red
            [1, 'rgb(200,0,0)']            # Deep red for high values
        ]
        
        # Create the heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale=colorscale,
            colorbar=dict(title="Sharpe Ratio"),
            hoverongaps=False,
            hovertemplate='Return: %{x:.2f}%<br>Risk: %{y:.2f}%<br>Sharpe Ratio: %{z:.2f}<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title=f"Portfolio Risk-Return Tradeoff by Market Regime",
            xaxis_title="Expected Return (%)",
            yaxis_title="Expected Risk (%)",
            height=500,
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        # Add markers for each regime's optimal portfolio
        for regime in filtered_results['regime_id'].unique():
            regime_data = filtered_results[filtered_results['regime_id'] == regime]
            best_portfolio = regime_data.loc[regime_data['sharpe_ratio'].idxmax()]
            
            fig.add_trace(go.Scatter(
                x=[best_portfolio['expected_return']],
                y=[best_portfolio['expected_risk']],
                mode='markers+text',
                marker=dict(symbol='star', size=15, color='gold', line=dict(width=2, color='black')),
                text=[f"Regime {regime}"],
                textposition="top center",
                name=f"Regime {regime} Optimal",
                hovertemplate='Regime %{text}<br>Return: %{x:.2f}%<br>Risk: %{y:.2f}%<extra></extra>'
            ))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        st.markdown("""
        **How to read this chart:**
        - Each point on the heatmap represents a possible portfolio allocation
        - The color intensity indicates the Sharpe ratio (risk-adjusted return)
        - Stars mark the optimal portfolio for each market regime
        - Hover over any point to see detailed metrics
        """)
    
    with col2:
        st.subheader("Optimal Portfolio Details")
        
        # Allow user to select a market regime
        selected_regime = st.selectbox(
            "Select Market Regime for Portfolio Details:",
            options=sorted(filtered_results['regime_id'].unique()),
            format_func=lambda x: f"Regime {x}" + (" (Current)" if x == current_regime else "")
        )
        
        # Get the best portfolio for the selected regime
        regime_portfolios = filtered_results[filtered_results['regime_id'] == selected_regime]
        best_portfolio = regime_portfolios.loc[regime_portfolios['sharpe_ratio'].idxmax()]
        
        # Display portfolio metrics
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric("Expected Return", f"{best_portfolio['expected_return']:.2f}%")
            st.metric("Sharpe Ratio", f"{best_portfolio['sharpe_ratio']:.2f}")
        with metrics_col2:
            st.metric("Expected Risk", f"{best_portfolio['expected_risk']:.2f}%")
            st.metric("Holding Period", f"{holding_duration} days")
        
        # Display portfolio allocation
        st.subheader("Portfolio Allocation")
        
        # Get the portfolio weights
        weights = {}
        for col in portfolio_results.columns:
            if col.endswith('_weight'):
                ticker = col.split('_weight')[0]
                weight = best_portfolio[col]
                if weight > 0.01:  # Only show allocations > 1%
                    weights[ticker] = weight
        
        # Create a DataFrame for the weights
        weights_df = pd.DataFrame({
            'Ticker': list(weights.keys()),
            'Weight': list(weights.values())
        }).sort_values('Weight', ascending=False)
        
        # Create a pie chart for the allocation
        fig = px.pie(
            weights_df, 
            values='Weight', 
            names='Ticker',
            title='Portfolio Allocation',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(margin=dict(l=20, r=20, t=30, b=0), height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display the allocation table
        st.dataframe(weights_df.style.format({'Weight': '{:.2%}'}), hide_index=True)
        
        # Add a download button for the portfolio allocation
        csv = weights_df.to_csv(index=False)
        st.download_button(
            label="Download Portfolio Allocation",
            data=csv,
            file_name=f"portfolio_allocation_regime_{selected_regime}_{risk_appetite}_{holding_duration}.csv",
            mime="text/csv"
        )

# If data is not loaded, show a placeholder
if not data_loaded:
    st.info("Please run the optimization script first to generate the necessary data files.")
    
    # Show a sample heatmap as a placeholder
    st.subheader("Sample Portfolio Risk-Return Heatmap (Placeholder)")
    
    # Create sample data
    risk = np.linspace(5, 25, 20)
    returns = np.linspace(2, 15, 20)
    
    # Create a meshgrid for the heatmap
    X, Y = np.meshgrid(returns, risk)
    Z = X / Y  # Simple Sharpe ratio approximation
    
    # Create the heatmap
    fig = go.Figure(data=go.Heatmap(
        z=Z,
        x=returns,
        y=risk,
        colorscale='Reds',
        colorbar=dict(title="Sharpe Ratio"),
        hoverongaps=False
    ))
    
    # Update layout
    fig.update_layout(
        title="Sample Portfolio Risk-Return Tradeoff (Placeholder)",
        xaxis_title="Expected Return (%)",
        yaxis_title="Expected Risk (%)",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    **Note:** This is a placeholder visualization. 
    Run the optimization script to see actual portfolio recommendations based on your data.
    """)
