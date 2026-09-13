import pandas as pd
import os

def create_main_csv():
    # Define the dataset directory relative to this script
    script_dir = os.path.dirname(__file__)
    dataset_dir = os.path.join(script_dir, "../DataSet")
    
    print(f"\nAggregating data from {dataset_dir}...")
    
    data_rows = []

    # Walk through the directory structure
    for root, dirs, files in os.walk(dataset_dir):
        # Check if both processed files exist
        if "processed_prices.csv" in files and "processed_arrivals.csv" in files:
            prices_path = os.path.join(root, "processed_prices.csv")
            arrivals_path = os.path.join(root, "processed_arrivals.csv")
            
            # Extract metadata from path
            # Structure: .../DataSet/{State}/{Commodity}/{Year}/{Month}/...
            try:
                # Get relative path from dataset_dir to handle varying absolute paths
                rel_path = os.path.relpath(root, dataset_dir)
                path_parts = rel_path.split(os.sep)
                
                # We expect at least 4 parts: State, Commodity, Year, Month
                if len(path_parts) >= 4:
                    state = path_parts[0]
                    commodity = path_parts[1] 
                    year = path_parts[2]
                    month = path_parts[3]

                    # Filter out placeholder directories if any (though unlikely with new structure)
                    if commodity.lower().startswith("commodity"):
                        continue
                    
                    # Read CSVs
                    df_prices = pd.read_csv(prices_path)
                    df_arrivals = pd.read_csv(arrivals_path)
                    
                    # Ensure minimal columns exist
                    # Prices: Market(0), Current(1), Prev(2)
                    # Arrivals: Market(0), Current(1), Prev(2)
                    if len(df_prices.columns) >= 3 and len(df_arrivals.columns) >= 3:
                         # Rename columns for merging and clarity
                         # We assume Market is the first column in both
                         market_col_prices = df_prices.columns[0]
                         market_col_arrivals = df_arrivals.columns[0]
                         
                         # Rename to standard names for merge
                         df_prices = df_prices.rename(columns={
                             df_prices.columns[0]: 'Market',
                             df_prices.columns[1]: 'Current_Month price',
                             df_prices.columns[2]: 'Prev_Month price'
                         })
                         
                         df_arrivals = df_arrivals.rename(columns={
                             df_arrivals.columns[0]: 'Market',
                             df_arrivals.columns[1]: 'Current_Month arrivals',
                             df_arrivals.columns[2]: 'Prev_Month arrivals'
                         })
                         
                         # Select only necessary columns
                         df_prices_clean = df_prices[['Market', 'Current_Month price', 'Prev_Month price']]
                         df_arrivals_clean = df_arrivals[['Market', 'Current_Month arrivals', 'Prev_Month arrivals']]
                         
                         # Merge on Market
                         merged_df = pd.merge(df_prices_clean, df_arrivals_clean, on='Market', how='inner')
                         
                         for _, row in merged_df.iterrows():
                             data_rows.append({
                                 "State": state,
                                 "Commodity": commodity,
                                 "Year": year,
                                 "Month": month,
                                 "Market": row['Market'],
                                 "Current_Month price": row['Current_Month price'],
                                 "Prev_Month price": row['Prev_Month price'],
                                 "Current_Month arrivals": row['Current_Month arrivals'],
                                 "Prev_Month arrivals": row['Prev_Month arrivals']
                             })

            except Exception as e:
                print(f"Error processing {root}: {e}")

    # Create DataFrame and save
    if data_rows:
        # Define column order
        columns = ["State", "Commodity", "Year", "Month", "Market", 
                   "Current_Month price", "Prev_Month price", 
                   "Current_Month arrivals", "Prev_Month arrivals"]
        main_df = pd.DataFrame(data_rows, columns=columns)
        
        output_path = os.path.join(dataset_dir, "main.csv")
        main_df.to_csv(output_path, index=False)
        print(f"\nSuccessfully created main.csv at {output_path}")
        print("First 5 rows:")
        print(main_df.head())
        print(f"\nTotal rows: {len(main_df)}")
    else:
        print("\nNo merged data found.")

if __name__ == "__main__":
    create_main_csv()
