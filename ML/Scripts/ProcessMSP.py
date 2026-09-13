import pandas as pd
import numpy as np
from pypdf import PdfReader
import os
import re
from sklearn.linear_model import LinearRegression

def process_msp():
    script_dir = os.path.dirname(__file__)
    dataset_dir = os.path.join(script_dir, "../DataSet")
    pdf_path = os.path.join(dataset_dir, "Maharashtra/External Factors/msp.pdf")
    main_csv_path = os.path.join(dataset_dir, "main.csv")
    
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    # --- Step 1: Extract Text from PDF ---
    print("Reading PDF...")
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
        
    # --- Step 2: Parse Wheat MSP ---
    # Looking for line: "15 Wheat 2015 2125 2275 2425 2585"
    # Column headers in PDF: 2022-23, 2023-24, 2024-25, 2025-26, 2026-27
    # So 2015 corresponds to 2022-23 (Marketing Season usually is Year+1 for Rabi? No, typically listed as Year-Year+1)
    # Let's re-verify headers from inspection output:
    # "RABI CROPS RMS 2022-23 RMS 2023-24 RMS 2024-25 RMS 2025-26 RMS 2026-27"
    # "15 Wheat 2015 2125 2275 2425 2585"
    
    # So:
    # 2022-23 -> 2015
    # 2023-24 -> 2125
    # 2024-25 -> 2275
    # 2025-26 -> 2425
    # 2026-27 -> 2585
    
    # Our data in main.csv has "Year".
    # Prices for "2022" (calendar year) likely fall under RMS 2022-23 (marketed in early 2022).
    # Prices for "2021" (calendar year) likely fall under RMS 2021-22.
    
    # We DO NOT have 2021-22 in the PDF.
    # We have years: 2022, 2023, 2024, 2025, 2026 (taken as the start year of the RMS pair)
    years_x = np.array([2022, 2023, 2024, 2025, 2026]).reshape(-1, 1)
    msp_y = np.array([2015, 2125, 2275, 2425, 2585])
    
    print(f"Extracted MSP Data points: \nYears: {years_x.flatten()}\nMSP: {msp_y}")
    
    # --- Step 3: Predict 2021 ---
    print("Predicting 2021 MSP using Linear Regression...")
    model = LinearRegression()
    model.fit(years_x, msp_y)
    
    # Predict for 2021
    msp_2021_pred = model.predict([[2021]])[0]
    print(f"Predicted MSP for 2021: {msp_2021_pred:.2f}")
    
    # Values to use
    msp_2021 = msp_2021_pred
    msp_2022 = 2015 # From PDF directly
    msp_2023 = 2125 # From PDF directly (RMS 2023-24)
    
    print(f"Using - 2021: {msp_2021:.2f}, 2022: {msp_2022}, 2023: {msp_2023}")

    # --- Step 4: Update main.csv ---
    if not os.path.exists(main_csv_path):
        print(f"Error: {main_csv_path} not found.")
        return
        
    print("Updating main.csv...")
    df_main = pd.read_csv(main_csv_path)
    
    # Function to assign MSP based on Year
    def get_msp(year):
        if year == 2021:
            return msp_2021
        elif year == 2022:
            return msp_2022
        elif year == 2023:
            return msp_2023
        else:
            return None
            
    df_main['msp'] = df_main['Year'].apply(get_msp)
    
    # Save
    df_main.to_csv(main_csv_path, index=False)
    print(f"Successfully updated main.csv with MSP data.")
    print("First 5 rows:")
    print(df_main[['Year', 'Month', 'msp']].head())
    
    # Check for NaNs
    print(f"\nMissing values in msp column: {df_main['msp'].isnull().sum()}")

if __name__ == "__main__":
    process_msp()
