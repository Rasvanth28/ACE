import pandas as pd
import os

def add_rainfall_lag():
    script_dir = os.path.dirname(__file__)
    dataset_dir = os.path.join(script_dir, "../DataSet")
    main_csv_path = os.path.join(dataset_dir, "main.csv")

    print("Loading main.csv...")
    df = pd.read_csv(main_csv_path)

    # Encode Month to ensure correct sorting
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    df['Month_Num'] = df['Month'].map(month_map)
    
    # Sort: Market, Year, Month
    df = df.sort_values(by=['Market', 'Year', 'Month_Num']).reset_index(drop=True)

    print("Creating Rainfall Lag Feature...")
    # Shift Rainfall_mm by 1 within each Market group
    df['Rainfall_Lag'] = df.groupby('Market')['Rainfall_mm'].shift(1)

    print(f"Missing values before filling: {df['Rainfall_Lag'].isnull().sum()}")

    # Fill missing values (Backfill for the first month, e.g., Jan 2021 gets Feb 2021's Lag / Jan 2021 Rainfall depending on interpretation, 
    # but strictly backfilling the Lag column means taking the next valid Lag. 
    # User said: "if there is any missing data , just append the previous value to it" -> this usually means forward fill.
    # But for the *first* value, there is no previous value. 
    # For Jan 2021, the lag is Dec 2020 (missing).
    # "append previous value" in the context of "if find data on march fill it with feb" describes the lagging process itself.
    # For the edge case of Jan 2021, we will use backfill as agreed in the plan (since forward fill is impossible for index 0).
    df['Rainfall_Lag'] = df['Rainfall_Lag'].bfill()

    print(f"Missing values after filling: {df['Rainfall_Lag'].isnull().sum()}")

    # Drop helper column
    df = df.drop(columns=['Month_Num'])

    print(f"Saving updated main.csv to {main_csv_path}...")
    df.to_csv(main_csv_path, index=False)
    print("Success!")

    # Verification preview
    print("\nPreview of first 5 rows with Rainfall Lag:")
    print(df[['Year', 'Month', 'Market', 'Rainfall_mm', 'Rainfall_Lag']].head())

if __name__ == "__main__":
    add_rainfall_lag()
