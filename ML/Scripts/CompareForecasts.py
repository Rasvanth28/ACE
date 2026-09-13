import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

def compare_forecasts():
    script_dir = os.path.dirname(__file__)
    dataset_dir = os.path.join(script_dir, "../DataSet")
    main_csv_path = os.path.join(dataset_dir, "main.csv")
    json_path = os.path.join(script_dir, "../JSON output/forecast_report.json")
    output_dir = os.path.join(script_dir, "../") # Root of ML folder as requested for CSV
    
    # 1. Load Actual Data (2022 Jan-Mar)
    try:
        df_main = pd.read_csv(main_csv_path)
    except FileNotFoundError:
        print("Error: main.csv not found.")
        return

    # Filter for Jan-Mar 2022
    month_map = {
        'January': 1, 'February': 2, 'March': 3
    }
    
    df_actual = df_main[
        (df_main['Year'] == 2022) & 
        (df_main['Month'].isin(['January', 'February', 'March']))
    ].copy()
    
    if df_actual.empty:
        print("Warning: No actual data found for Jan-Mar 2022 in main.csv")
        return

    # Select relevant columns
    df_actual = df_actual[['Market', 'Month', 'Current_Month price']]
    df_actual.rename(columns={'Current_Month price': 'Actual_Price'}, inplace=True)
    
    # 2. Load Predicted Data from JSON
    try:
        with open(json_path, 'r') as f:
            forecast_data = json.load(f)
    except FileNotFoundError:
        print("Error: forecast_report.json not found.")
        return

    # Extract Forecasts
    predictions = []
    
    # Market-level predictions
    for mkt in forecast_data['market_details']:
        market_name = mkt['market_name']
        for forecast in mkt['forecast_series']:
            predictions.append({
                'Market': market_name,
                'Month': forecast['month'],
                'Predicted_Price': forecast['price']
            })
            
    df_pred = pd.DataFrame(predictions)
    
    # 3. Merge Data
    df_comparison = pd.merge(df_actual, df_pred, on=['Market', 'Month'], how='inner')
    
    # Save to CSV
    output_csv_path = os.path.join(output_dir, "prediction.csv")
    df_comparison.to_csv(output_csv_path, index=False)
    print(f"Comparison data saved to: {output_csv_path}")
    
    # 4. Visualization
    sns.set_style("whitegrid")
    
    # Identify top 3 markets (e.g., those present in the first few rows of merged data)
    unique_markets = df_comparison['Market'].unique()
    selected_markets = unique_markets[:3] # Pick first 3
    
    plt.figure(figsize=(14, 8))
    
    # Define Month Order for plotting
    month_order = ['January', 'February', 'March']
    df_comparison['Month'] = pd.Categorical(df_comparison['Month'], categories=month_order, ordered=True)
    df_comparison = df_comparison.sort_values('Month')
    
    colors = sns.color_palette("husl", len(selected_markets) + 1)
    
    # Plot Selected Markets
    for idx, market in enumerate(selected_markets):
        subset = df_comparison[df_comparison['Market'] == market]
        
        # Actual - Solid Line
        plt.plot(subset['Month'], subset['Actual_Price'], marker='o', linestyle='-', 
                 label=f'{market} (Actual)', color=colors[idx], linewidth=2)
        
        # Predicted - Dotted Line
        plt.plot(subset['Month'], subset['Predicted_Price'], marker='x', linestyle=':', 
                 label=f'{market} (Predicted)', color=colors[idx], linewidth=2)

    # Plot State Summary (Average)
    # Calculate actual state average for these months
    state_avg_actual = df_comparison.groupby('Month')['Actual_Price'].mean()
    state_avg_pred = df_comparison.groupby('Month')['Predicted_Price'].mean()
    
    # Actual State Avg - Thick Solid Black
    plt.plot(state_avg_actual.index, state_avg_actual.values, marker='s', linestyle='-', 
             label='State Average (Actual)', color='black', linewidth=3)
             
    # Predicted State Avg - Thick Dotted Black
    plt.plot(state_avg_pred.index, state_avg_pred.values, marker='d', linestyle=':', 
             label='State Average (Predicted)', color='black', linewidth=3)
    
    plt.title("Actual vs Predicted Wheat Prices (Jan-Mar 2022)", fontsize=16)
    plt.ylabel("Price (₹/Quintal)", fontsize=12)
    plt.xlabel("Month", fontsize=12)
    plt.legend()
    plt.tight_layout()
    
    output_plot_path = os.path.join(output_dir, "forecast_comparison.png")
    plt.savefig(output_plot_path, dpi=300)
    print(f"Comparison plot saved to: {output_plot_path}")
    plt.close()

if __name__ == "__main__":
    compare_forecasts()
