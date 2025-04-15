import pandas as pd

# Define the function to process the CSV
def process_csv(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Extract only the date part from the Date column (in case it has time)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    
    # Identify numeric columns (all except Date)
    numeric_columns = df.columns.difference(['Date'])
    
    # Subtract 100 from each numeric column
    for col in numeric_columns:
        df[col] = (df[col] - 100).round(2)
    
    # Save to a new CSV file with original column names preserved
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

# Example usage
if __name__ == "__main__":
    input_file = "output/dynamic_equity_curves.csv"  # Replace with your input file name
    output_file = "output/line_chart_data.csv"  # Replace with your desired output file name
    process_csv(input_file, output_file)