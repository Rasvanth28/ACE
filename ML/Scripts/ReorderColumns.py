import pandas as pd
import os

def reorder_columns():
    script_dir = os.path.dirname(__file__)
    dataset_dir = os.path.join(script_dir, "../DataSet")
    main_csv_path = os.path.join(dataset_dir, "main.csv")

    print("Loading main.csv...")
    df = pd.read_csv(main_csv_path)

    # Desired Column Order from User Request (Mapped to actual column names)
    # User Request: State , Commodity , Year , Month, Market, Current_Month price , Prev_Month price , Prev_2_Month price , Current_Month arrivals, Prev_Month arrivals , Prev_2_Months arrivals, Rainfall_mm, Rainfal_lag,Diesel price , irrigation_water, Area, Production, Yield , msp , temprature
    
    desired_order = [
        'State',
        'Commodity',
        'Year',
        'Month',
        'Market',
        'Current_Month price',
        'Prev_Month price',
        'Prev_2_Month price',
        'Price_Velocity',
        'Current_Month arrivals',
        'Prev_Month arrivals',
        'Prev_2_Month arrivals',  # Correspond to 'Prev_2_Months arrivals'
        'Rainfall_mm',
        'Rainfall_Lag',           # Correspond to 'Rainfal_lag'
        'Diesel_Price_Rs_per_Litre', # Correspond to 'Diesel price'
        'Irrigation_Water_Usage_MCM', # Correspond to 'irrigation_water'
        'Area',
        'Production',
        'Yield',
        'msp',
        'Temperature'             # Correspond to 'temprature'
    ]

    # Verify all columns exist
    missing_cols = [col for col in desired_order if col not in df.columns]
    if missing_cols:
        print(f"Error: The following target columns are missing in main.csv: {missing_cols}")
        print(f"Available columns: {list(df.columns)}")
        return

    print("Reordering columns...")
    df = df[desired_order]

    print(f"Saving reordered main.csv to {main_csv_path}...")
    df.to_csv(main_csv_path, index=False)
    print("Success!")
    
    # Validation
    print("\nVerified Column Order:")
    print(list(df.columns))

if __name__ == "__main__":
    reorder_columns()
