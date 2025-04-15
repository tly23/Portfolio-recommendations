from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
from datetime import datetime
import os
from typing import Literal, Dict, List, Any
import calendar

app = FastAPI(title="Financial Data API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_monthly_data(filepath: str, risk_level: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extracts the monthly data for the last year from a CSV file based on risk level.
    
    Args:
        filepath: Path to the CSV file
        risk_level: One of 'risk_loving', 'risk_averse', or 'moderate'
        
    Returns:
        A dictionary with a 'data' key containing the monthly values
    """
    try:
        # Map risk level to CSV column
        column_mapping = {
            "risk_averse": "Dynamic Risk Averse",
            "risk_loving": "Dynamic Risk Loving",
            "moderate": "Dynamic Risk Neutral"
        }
        
        # Ensure the risk level is valid
        if risk_level not in column_mapping:
            raise ValueError(f"Invalid risk level: {risk_level}. Must be one of {list(column_mapping.keys())}")
        
        # Read the CSV file
        df = pd.read_csv(filepath)
        
        # Ensure the Date column exists
        if 'Date' not in df.columns:
            raise ValueError("CSV file must contain a 'Date' column")
        
        # Ensure the required column for the risk level exists
        column_name = column_mapping[risk_level]
        if column_name not in df.columns:
            raise ValueError(f"CSV file must contain a '{column_name}' column")
        
        # Convert Date column to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Sort by date to ensure we have the latest dates at the end
        df = df.sort_values('Date')
        
        # Get the latest date in the dataset
        latest_date = df['Date'].max()
        latest_month = latest_date.month
        latest_year = latest_date.year
        
        # Check if the last month has data for the last day of the month
        last_day_of_month = calendar.monthrange(latest_year, latest_month)[1]
        last_day_date = pd.Timestamp(year=latest_year, month=latest_month, day=last_day_of_month)
        
        # If the last month is incomplete, start from the previous month
        if last_day_date > latest_date:
            # Adjust to the previous month
            if latest_month == 1:
                latest_month = 12
                latest_year -= 1
            else:
                latest_month -= 1
        
        # Calculate the start date (one year before the last complete month)
        if latest_month == 12:
            start_year = latest_year - 1
            start_month = 12
        else:
            start_year = latest_year - 1
            start_month = latest_month + 1
        
        # Initialize result list
        result = []
        
        # Extract data for each month in the one-year period
        current_year = start_year
        current_month = start_month
        
        while (current_year < latest_year) or (current_year == latest_year and current_month <= latest_month):
            # Get the last day of the current month
            last_day = calendar.monthrange(current_year, current_month)[1]
            
            # Find the closest date to the last day of the month
            month_data = df[(df['Date'].dt.year == current_year) & (df['Date'].dt.month == current_month)]
            
            if not month_data.empty:
                # Get the last available day in the month
                last_available_day = month_data['Date'].max()
                last_day_value = month_data[month_data['Date'] == last_available_day][column_name].iloc[0]
                
                # Format the month name
                month_name = datetime(current_year, current_month, 1).strftime('%b %Y')
                
                # Add to result
                result.append({
                    "name": month_name,
                    "value": round(float(last_day_value), 2) if isinstance(last_day_value, (int, float)) else 0.0
                })
            
            # Move to the next month
            if current_month == 12:
                current_month = 1
                current_year += 1
            else:
                current_month += 1
        
        return {"data": result}
    
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing CSV data: {str(e)}")
        raise e

@app.get("/")
def read_root():
    return {"message": "Financial Data API is running"}

@app.get("/api/monthly-data/")
def get_monthly_financial_data(risk_level: Literal["risk_averse", "risk_loving", "moderate"] = Query(...)):
    """
    Get monthly financial data for the last year based on risk level.
    
    Args:
        risk_level: One of 'risk_loving', 'risk_averse', or 'moderate'
        
    Returns:
        A JSON response with monthly financial data
    """
    try:
        # Path to your CSV file - adjust as needed
        csv_path = "./output/line_chart_data.csv"
        
        # Check if the file exists
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail="CSV file not found")
        
        # Get the monthly data
        result = get_monthly_data(csv_path, risk_level)
        
        return JSONResponse(content=result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend_server:app", host="127.0.0.1", port=8000, reload=True)