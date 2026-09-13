import pandas as pd
import os

def add_external_factors():
    script_dir = os.path.dirname(__file__)
    dataset_dir = os.path.join(script_dir, "../DataSet")
    external_factors_dir = os.path.join(dataset_dir, "Maharashtra/External Factors")
    main_csv_path = os.path.join(dataset_dir, "main.csv")
    
    if not os.path.exists(main_csv_path):
        print(f"Error: {main_csv_path} not found.")
        return

    print("Loading main.csv...")
    df_main = pd.read_csv(main_csv_path)
    
    # Fix Typos in Month Column
    print("Fixing typos in Month column...")
    df_main['Month'] = df_main['Month'].str.strip()
    df_main['Month'] = df_main['Month'].replace({
        'Febraury': 'February',
        'Febraury ': 'February', 
        'Septemeber': 'September',
        'Novemeber': 'November'
    })
    
    # Ensure Year is int
    df_main['Year'] = df_main['Year'].astype(int)

    # Clean existing external factor columns if re-running
    core_columns = [
        "State", "Commodity", "Year", "Month", "Market", 
        "Current_Month price", "Prev_Month price", 
        "Current_Month arrivals", "Prev_Month arrivals"
    ]
    
    # Filter to keep only core columns that exist
    df_main = df_main[[c for c in core_columns if c in df_main.columns]]


    # Load External Factors
    print("Loading external factors...")
    try:
        df_rainfall = pd.read_csv(os.path.join(external_factors_dir, "Rainfall.csv"))
        df_diesel = pd.read_csv(os.path.join(external_factors_dir, "Diesel.csv"))
        df_irrigation = pd.read_csv(os.path.join(external_factors_dir, "Irrigation.csv"))
        df_apy = pd.read_csv(os.path.join(external_factors_dir, "APY.csv"))
    except FileNotFoundError as e:
        print(f"Error loading external factors: {e}")
        return

    # --- Preprocess External Factors ---

    for df in [df_rainfall, df_diesel, df_irrigation]:
        df['Year'] = df['Year'].astype(int)
        df['Month'] = df['Month'].str.strip()
        
    # --- Forward Fill 2022 to 2023 ---
    # Helper to forward fill for 2023 based on 2022
    def forward_fill_2023(df, value_col):
        # Check if 2023 exists
        if 2023 not in df['Year'].unique():
            print(f"Forward filling {value_col} for 2023...")
            df_2022 = df[df['Year'] == 2022].copy()
            df_2022['Year'] = 2023
            return pd.concat([df, df_2022], ignore_index=True)
        return df

    df_rainfall = forward_fill_2023(df_rainfall, 'Rainfall_mm')
    df_diesel = forward_fill_2023(df_diesel, 'Diesel_Price_Rs_per_Litre')
    df_irrigation = forward_fill_2023(df_irrigation, 'Irrigation_Water_Usage_MCM')

    # --- Merge Rainfall, Diesel, Irrigation ---
    
    print("Merging Rainfall data...")
    df_main = pd.merge(df_main, df_rainfall[['Year', 'Month', 'Rainfall_mm']], 
                       on=['Year', 'Month'], how='left')

    print("Merging Diesel data...")
    df_main = pd.merge(df_main, df_diesel[['Year', 'Month', 'Diesel_Price_Rs_per_Litre']], 
                       on=['Year', 'Month'], how='left')

    print("Merging Irrigation data...")
    df_main = pd.merge(df_main, df_irrigation[['Year', 'Month', 'Irrigation_Water_Usage_MCM']], 
                       on=['Year', 'Month'], how='left')

    # --- Process and Merge APY Data ---
    print("Processing and Merging APY data...")
    
    # Filter for Wheat and Total Season
    # Adjust column names if necessary based on inspection (headers seemed to have quotes in previous view)
    # The view_file output showed headers like "Crop", "Season", etc. Pandas handle quotes usually.
    
    # Normalize headers just in case
    df_apy.columns = [c.strip().replace('"', '') for c in df_apy.columns]
    
    wheat_apy = df_apy[(df_apy['Crop'] == 'Wheat') & (df_apy['Season'] == 'Total')]
    
    if not wheat_apy.empty:
        # Extract values for 2021-22 and 2022-23
        # 2021 data <- 2021-22 columns
        area_21 = wheat_apy.iloc[0]['Area-2021-22']
        prod_21 = wheat_apy.iloc[0]['Production-2021-22']
        yield_21 = wheat_apy.iloc[0]['Yield-2021-22']
        
        # 2022 data <- 2022-23 columns
        area_22 = wheat_apy.iloc[0]['Area-2022-23']
        prod_22 = wheat_apy.iloc[0]['Production-2022-23']
        yield_22 = wheat_apy.iloc[0]['Yield-2022-23']
        
        # Map to main dataframe based on Year
        def get_apy_value(year, val_21, val_22):
            if year == 2021:
                return val_21
            elif year == 2022:
                return val_22
            elif year == 2023: # Forward fill 2022 to 2023
                return val_22
            else:
                return None

        # Apply mapping
        df_main['Area'] = df_main['Year'].apply(lambda x: get_apy_value(x, area_21, area_22))
        df_main['Production'] = df_main['Year'].apply(lambda x: get_apy_value(x, prod_21, prod_22))
        df_main['Yield'] = df_main['Year'].apply(lambda x: get_apy_value(x, yield_21, yield_22))
        
    else:
        print("Warning: Wheat data not found in APY.csv")

    # --- Formatting Output ---
    
    # Save updated main.csv
    print(f"Saving updated main.csv to {main_csv_path}...")
    df_main.to_csv(main_csv_path, index=False)
    
    print("\nSuccess! Added external factors and APY data.")
    print("First 5 rows:")
    print(df_main.head())
    
    # Check for NaNs
    new_cols = ['Rainfall_mm', 'Diesel_Price_Rs_per_Litre', 'Irrigation_Water_Usage_MCM', 'Area', 'Production', 'Yield']
    print(f"\nMissing values in new columns:\n{df_main[new_cols].isnull().sum()}")

if __name__ == "__main__":
    add_external_factors()
