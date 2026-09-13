import pandas as pd
import numpy as np
import os
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

def add_lag_features():
    script_dir = os.path.dirname(__file__)
    dataset_dir = os.path.join(script_dir, "../DataSet")
    main_csv_path = os.path.join(dataset_dir, "main.csv")

    print("Loading main.csv...")
    df = pd.read_csv(main_csv_path)

    # Encode Month to ensure correct sorting and use in imputation
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    # Handle potential typos just in case, though they should be fixed
    df['Month_Num'] = df['Month'].map(month_map)
    
    # Sort to ensure shift works correctly: Market, Year, Month
    df = df.sort_values(by=['Market', 'Year', 'Month_Num']).reset_index(drop=True)

    print("Creating 2-Month Lag Features...")
    # Shift 'Prev_Month price' by 1 to get 'Prev_2_Month price'
    # Prev_Month price at time T is Price at T-1.
    # We want Price at T-2.
    # So shrinking Prev_Month price (T-1) by 1 gives Price at (T-2).
    # Group by Market to avoid shifting across different markets
    df['Prev_2_Month price'] = df.groupby('Market')['Prev_Month price'].shift(1)
    df['Prev_2_Month arrivals'] = df.groupby('Market')['Prev_Month arrivals'].shift(1)

    print(f"Missing values before imputation:\n{df[['Prev_2_Month price', 'Prev_2_Month arrivals']].isnull().sum()}")

    # Prepare for Imputation
    # Columns to use as predictors and targets
    # We excluded non-numeric columns like State, Commodity, Market, Month names
    numeric_cols = [
        'Year', 'Month_Num', 
        'Current_Month price', 'Prev_Month price', 'Prev_2_Month price',
        'Current_Month arrivals', 'Prev_Month arrivals', 'Prev_2_Month arrivals',
        'Rainfall_mm', 'Diesel_Price_Rs_per_Litre', 'Irrigation_Water_Usage_MCM',
        'Area', 'Production', 'Yield', 'msp', 'Temperature'
    ]
    
    # Ensure all numeric columns are actually numeric
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    imputation_data = df[numeric_cols].copy()

    print("Imputing missing lag values (IterativeImputer)...")
    imputer = IterativeImputer(max_iter=10, random_state=0)
    imputed_values = imputer.fit_transform(imputation_data)
    
    imputed_df = pd.DataFrame(imputed_values, columns=numeric_cols)

    # Assign back the imputed columns
    df['Prev_2_Month price'] = imputed_df['Prev_2_Month price']
    df['Prev_2_Month arrivals'] = imputed_df['Prev_2_Month arrivals']

    print(f"Missing values after imputation:\n{df[['Prev_2_Month price', 'Prev_2_Month arrivals']].isnull().sum()}")

    # Drop helper column
    df = df.drop(columns=['Month_Num'])

    print(f"Saving updated main.csv to {main_csv_path}...")
    df.to_csv(main_csv_path, index=False)
    print("Success!")

    # Verification preview
    print("\nPreview of first 5 rows with lags:")
    print(df[['Year', 'Month', 'Market', 'Current_Month price', 'Prev_Month price', 'Prev_2_Month price']].head())

if __name__ == "__main__":
    add_lag_features()
