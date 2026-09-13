import pandas as pd
import numpy as np
import os
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

def process_temperature():
    script_dir = os.path.dirname(__file__)
    dataset_dir = os.path.join(script_dir, "../DataSet")
    temp_csv_path = os.path.join(dataset_dir, "Maharashtra/External Factors/Temprature.csv")
    main_csv_path = os.path.join(dataset_dir, "main.csv")
    
    if not os.path.exists(temp_csv_path):
        print(f"File not found: {temp_csv_path}")
        return

    print("Loading Temprature.csv...")
    # Load and clean data (handle junk at end)
    df_temp = pd.read_csv(temp_csv_path)
    
    # Drop rows where YEAR is NaN
    df_temp = df_temp.dropna(subset=['YEAR'])
    
    # Convert columns to numeric, coercing errors
    cols = ['YEAR', 'ANNUAL', 'JAN-FEB', 'MAR-MAY', 'JUN-SEP', 'OCT-DEC']
    for col in cols:
        df_temp[col] = pd.to_numeric(df_temp[col], errors='coerce')
        
    df_temp = df_temp.dropna(subset=['YEAR'])
    df_temp['YEAR'] = df_temp['YEAR'].astype(int)
    
    # Check if 2022 exists
    if 2022 not in df_temp['YEAR'].values:
        print("2022 data missing. preparing for imputation...")
        # Append 2022 row
        new_row = pd.DataFrame({'YEAR': [2022], 'ANNUAL': [np.nan], 
                                'JAN-FEB': [np.nan], 'MAR-MAY': [np.nan],
                                'JUN-SEP': [np.nan], 'OCT-DEC': [np.nan]})
        df_temp = pd.concat([df_temp, new_row], ignore_index=True)
        
    # Impute
    print("Imputing missing values using IterativeImputer...")
    imputer = IterativeImputer(random_state=42)
    # fit on all columns
    df_imputed_array = imputer.fit_transform(df_temp[cols])
    df_imputed = pd.DataFrame(df_imputed_array, columns=cols)
    df_imputed['YEAR'] = df_imputed['YEAR'].astype(int)
    
    # Extract 2021 and 2022 data for quick lookup
    temp_2021 = df_imputed[df_imputed['YEAR'] == 2021].iloc[0]
    temp_2022 = df_imputed[df_imputed['YEAR'] == 2022].iloc[0]
    
    print("\nTemperature Data (Season-wise):")
    print(f"2021: {temp_2021.to_dict()}")
    print(f"2022: {temp_2022.to_dict()}")
    
    # --- Merge into main.csv ---
    if not os.path.exists(main_csv_path):
        print(f"Error: {main_csv_path} not found.")
        return
        
    print("\nUpdating main.csv...")
    df_main = pd.read_csv(main_csv_path)
    
    # Helper to map Month to Season Column
    def get_temperature(row):
        year = row['Year']
        month = row['Month']
        
        # Select appropriate year data
        if year == 2021:
            data = temp_2021
        elif year == 2022:
            data = temp_2022
        elif year == 2023: # Use 2022 data for 2023
            data = temp_2022
        else:
            return None # Should not happen for this dataset
            
        # Map Month to Season
        if month in ['January', 'February']:
            return data['JAN-FEB']
        elif month in ['March', 'April', 'May']:
            return data['MAR-MAY']
        elif month in ['June', 'July', 'August', 'September']:
            return data['JUN-SEP']
        elif month in ['October', 'November', 'December']:
            return data['OCT-DEC']
        else:
            return None

    df_main['Temperature'] = df_main.apply(get_temperature, axis=1)
    
    # Save
    df_main.to_csv(main_csv_path, index=False)
    print(f"Successfully updated main.csv with Temperature data.")
    print("First 5 rows:")
    print(df_main[['Year', 'Month', 'Temperature']].head())
    
    # Check for NaNs
    print(f"\nMissing values in Temperature column: {df_main['Temperature'].isnull().sum()}")

if __name__ == "__main__":
    process_temperature()
