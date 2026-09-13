import pandas as pd
import os

def add_price_velocity():
    script_dir = os.path.dirname(__file__)
    dataset_dir = os.path.join(script_dir, "../DataSet")
    main_csv_path = os.path.join(dataset_dir, "main.csv")

    print("Loading main.csv...")
    df = pd.read_csv(main_csv_path)

    print("Calculating Price Velocity...")
    # Formula: Price_Velocity = Prev_Month price - Prev_2_Month price
    df['Price_Velocity'] = df['Prev_Month price'] - df['Prev_2_Month price']

    # Insert 'Price_Velocity' to the right of 'Prev_2_Month price'
    if 'Prev_2_Month price' in df.columns:
        col_index = df.columns.get_loc('Prev_2_Month price') + 1
        # Pop the column to move it
        velocity_col = df.pop('Price_Velocity')
        df.insert(col_index, 'Price_Velocity', velocity_col)
    else:
        print("Warning: 'Prev_2_Month price' column not found. Appending 'Price_Velocity' at the end.")

    print(f"Saving updated main.csv to {main_csv_path}...")
    df.to_csv(main_csv_path, index=False)
    print("Success!")

    # Verification preview
    print("\nPreview of first 5 rows with Price Velocity:")
    print(df[['Prev_Month price', 'Prev_2_Month price', 'Price_Velocity']].head())

if __name__ == "__main__":
    add_price_velocity()
