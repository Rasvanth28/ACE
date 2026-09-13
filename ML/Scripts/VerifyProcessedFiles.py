import os

def verify_files():
    script_dir = os.path.dirname(__file__)
    base_dir = os.path.join(script_dir, "DataSet/Maharashtra/Wheat")
    
    years = ["2021", "2022"]
    # List of all possible month folder names we've encountered or expect
    # This list is used to find the directory. 
    # We will walk the directory to find the actual folders present.
    
    missing_files = []
    
    print("Verifying processed files...")

    for year in years:
        year_dir = os.path.join(base_dir, year)
        if not os.path.exists(year_dir):
            print(f"Year directory not found: {year_dir}")
            continue
            
        # Get all subdirectories (months) in the year folder
        month_dirs = [d for d in os.listdir(year_dir) if os.path.isdir(os.path.join(year_dir, d))]
        
        for month in month_dirs:
            month_path = os.path.join(year_dir, month)
            
            # Check for processed_prices.csv
            prices_path = os.path.join(month_path, "processed_prices.csv")
            if not os.path.exists(prices_path):
                missing_files.append(f"MISSING: {prices_path}")
            
            # Check for processed_arrivals.csv
            arrivals_path = os.path.join(month_path, "processed_arrivals.csv")
            if not os.path.exists(arrivals_path):
                missing_files.append(f"MISSING: {arrivals_path}")

    if missing_files:
        print("\nFound missing files:")
        for missing in missing_files:
            print(missing)
    else:
        print("\nAll processed files are present in the existing month directories.")

if __name__ == "__main__":
    verify_files()
