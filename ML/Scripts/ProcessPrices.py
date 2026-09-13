import pandas as pd
import numpy as np
import os
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

def process_prices(file_path):
    """
    Reads a prices CSV file, imputes missing values using IterativeImputer,
    and saves the result to 'processed_prices.csv' in the same directory.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"\nProcessing Prices: {file_path}")

    try:
        # Read the CSV file, skipping the first row as it contains the title
        df = pd.read_csv(file_path, header=1)

        # Columns to process (Indices 1, 2, 3)
        # 1: Price Current Month
        # 2: Price Previous Month
        # 3: Price Previous Year
        # We need to ensure we select columns by position as names might vary slightly
        feature_cols_indices = [1, 2, 3]
        feature_cols = df.columns[feature_cols_indices]
        
        # Convert columns to numeric, coercing errors to NaN (handles '-')
        for col in feature_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Check if imputation is needed
        if df[feature_cols].isnull().values.any():
            print(f"Missing values found. Imputing...")
            
            # Use IterativeImputer
            imputer = IterativeImputer(max_iter=10, random_state=42)
            df[feature_cols] = imputer.fit_transform(df[feature_cols])
        else:
            print("No missing values found.")

        # Save Processed Data
        output_dir = os.path.dirname(file_path)
        output_path = os.path.join(output_dir, "processed_prices.csv")
        df.to_csv(output_path, index=False)
        print(f"Processed prices saved to: {output_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# ... (imports and function definition)

# --- Main Batch Execution ---

if __name__ == "__main__":
    # Define the base directory relative to this script
    script_dir = os.path.dirname(__file__)
    base_dir = os.path.join(script_dir, "../DataSet/Maharashtra/Wheat")
    
    years = ["2021", "2022", "2023"]
    months = [
        "January", "February", "Febraury ", "March", "April", "May", "June", 
        "July", "August", "September", "Septemeber", "October", "November", "Novemeber", "December"
    ]

    print("Starting batch processing for Prices (2021-2022)...")

    for year in years:
        for month in months:
            # Check for directory existence first
            month_dir = os.path.join(base_dir, year, month)
            
            if os.path.exists(month_dir):
                file_path = os.path.join(month_dir, "prices.csv")
                if os.path.exists(file_path):
                    process_prices(file_path)

    print("\nBatch processing for Prices complete.")
