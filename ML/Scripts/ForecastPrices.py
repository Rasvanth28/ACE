import pandas as pd
import numpy as np
import json
import os
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score
import sys

import matplotlib.pyplot as plt
import seaborn as sns

def save_plots(train_loss, val_loss, train_r2, val_r2, output_dir):
    """Generates and saves Matplotlib/Seaborn plots for Loss and Accuracy."""
    sns.set_style("whitegrid")
    
    epochs = range(1, len(train_loss) + 1)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Loss (MSE)
    sns.lineplot(x=epochs, y=train_loss, ax=ax1, label='Training Loss', color='blue')
    sns.lineplot(x=epochs, y=val_loss, ax=ax1, label='Validation Loss', color='orange')
    ax1.set_title('Training vs Validation Loss (MSE)')
    ax1.set_xlabel('Iterations (Estimators)')
    ax1.set_ylabel('Mean Squared Error')
    ax1.legend()
    
    # Plot 2: Accuracy (R2)
    sns.lineplot(x=epochs, y=train_r2, ax=ax2, label='Training R²', color='green')
    sns.lineplot(x=epochs, y=val_r2, ax=ax2, label='Validation R²', color='red')
    ax2.set_title('Training vs Validation Accuracy ($R^2$ Score)')
    ax2.set_xlabel('Iterations (Estimators)')
    ax2.set_ylabel('$R^2$ Score')
    ax2.legend()
    
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, "forecast_plots.png")
    plt.savefig(output_path, dpi=300)
    print(f"Plots saved to: {output_path}")
    
    # Optional: Try to show if supported (though likely headless)
    # plt.show() 
    plt.close()

def forecast_prices():
    script_dir = os.path.dirname(__file__)
    dataset_dir = os.path.join(script_dir, "../DataSet")
    main_csv_path = os.path.join(dataset_dir, "main.csv")
    json_output_dir = os.path.join(script_dir, "../JSON output")
    os.makedirs(json_output_dir, exist_ok=True)

    try:
        df = pd.read_csv(main_csv_path)
    except FileNotFoundError:
        print(json.dumps({"error": "main.csv not found"}))
        return

    # --- Preprocessing ---
    # Encode categorical variables
    le_market = LabelEncoder()
    df['Market_Encoded'] = le_market.fit_transform(df['Market'])
    
    # Month mapping
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    df['Month_Num'] = df['Month'].map(month_map)

    # Features and Target
    # Filter Data: Train on 2021, Predict 2022 (User Request: Ignore 2023)
    df = df[df['Year'] <= 2022]
    
    # Features and Target
    features = [
        'Year', 'Month_Num', 'Market_Encoded',
        'Prev_Month price', 'Prev_2_Month price', 'Price_Velocity',
        'Current_Month arrivals', 'Prev_Month arrivals',
        'Rainfall_mm', 'Rainfall_Lag', 'Diesel_Price_Rs_per_Litre',
        'Irrigation_Water_Usage_MCM', 'msp', 'Temperature'
    ]
    target = 'Current_Month price'

    # Drop rows with NaN
    df_clean = df.dropna(subset=features + [target]).copy()

    # Split for Validation: Train on 2021, Validate on 2022
    train_mask = df_clean['Year'] == 2021
    val_mask = df_clean['Year'] == 2022
    
    X_train = df_clean.loc[train_mask, features]
    y_train = df_clean.loc[train_mask, target]
    
    X_val = df_clean.loc[val_mask, features]
    y_val = df_clean.loc[val_mask, target]

    # --- Model Training ---
    model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    # --- Visualization ---
    train_loss = [mean_squared_error(y_train, y_pred) for y_pred in model.staged_predict(X_train)]
    val_loss = [mean_squared_error(y_val, y_pred) for y_pred in model.staged_predict(X_val)]
    
    train_r2 = [r2_score(y_train, y_pred) for y_pred in model.staged_predict(X_train)]
    val_r2 = [r2_score(y_val, y_pred) for y_pred in model.staged_predict(X_val)]

    # Generate Matplotlib Plots
    save_plots(train_loss, val_loss, train_r2, val_r2, json_output_dir)

    # --- Save Model ---
    import joblib
    model_dir = os.path.join(script_dir, "../Model")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "wheat_price_model.pkl")
    joblib.dump(model, model_path)
    print(f"Trained model saved to: {model_path}")

    # Final Metrics on Validation Set (2022)
    final_preds = model.predict(X_val)
    mape = mean_absolute_percentage_error(y_val, final_preds)
    rmse = np.sqrt(mean_squared_error(y_val, final_preds))
    r2 = r2_score(y_val, final_preds)
    print(f"Final Model Metrics (Validation 2022):\n MAPE: {mape:.4f}\n RMSE: {rmse:.4f}\n R^2: {r2:.4f}\n")

    # --- Recursive Forecasting Logic (Simulating End of 2021) ---
    
    # Get the latest available data point for each market from 2021 to serve as base
    df_latest = df_clean[df_clean['Year'] == 2021].sort_values(['Year', 'Month_Num']).groupby('Market').tail(1)
    
    forecast_results = []
    
    # Forecast for Jan, Feb, Mar 2022
    future_months = [("January", 1, 2022), ("February", 2, 2022), ("March", 3, 2022)]
    
    for idx, row in df_latest.iterrows():
        market_name = row['Market']
        market_encoded = row['Market_Encoded']
        
        # Initial State variables (from Dec 2021)
        current_price = row['Current_Month price'] # T
        prev_price = row['Current_Month price']    # Price at T becomes Prev for T+1
        prev_2_price = row['Prev_Month price']     # Prev for T becomes Prev_2 for T+1
        
        # Arrivals assumptions (Naive forecast: assume constant for simplicity or use lag)
        curr_arrivals = row['Current_Month arrivals']
        prev_arrivals = row['Current_Month arrivals']
        
        # External factors (Assumption: Use latest known values or averages from 2021)
        rainfall = row['Rainfall_mm']
        rainfall_lag = row['Rainfall_mm'] # Rainfall at T becomes lag for T+1
        diesel = row['Diesel_Price_Rs_per_Litre']
        irrigation = row['Irrigation_Water_Usage_MCM']
        msp = row['msp']
        temp = row['Temperature'] # In reality, use season avg
        
        market_forecasts = []
        
        # Recursive Loop for 3 Steps
        for f_month_name, f_month_num, f_year in future_months:
            # 1. Update Derived Features
            price_velocity = prev_price - prev_2_price
            
            # 2. Construct Feature Vector
            input_features = pd.DataFrame([{
                'Year': f_year,
                'Month_Num': f_month_num,
                'Market_Encoded': market_encoded,
                'Prev_Month price': prev_price,
                'Prev_2_Month price': prev_2_price,
                'Price_Velocity': price_velocity,
                'Current_Month arrivals': curr_arrivals, # Naive
                'Prev_Month arrivals': prev_arrivals,
                'Rainfall_mm': rainfall,
                'Rainfall_Lag': rainfall_lag,
                'Diesel_Price_Rs_per_Litre': diesel,
                'Irrigation_Water_Usage_MCM': irrigation,
                'msp': msp,
                'Temperature': temp
            }])
            
            # 3. Predict
            pred_price = model.predict(input_features)[0]
            
            market_forecasts.append({
                "month": f_month_name,
                "price": round(pred_price, 2),
                # Trend vs previous month in recursion
                "trend": "Up" if pred_price > prev_price else "Down"
            })
            
            # 4. Update State for Next Step (Recursion)
            prev_2_price = prev_price
            prev_price = pred_price
            # Arrivals/Rainfall update logic would go here if we had models for them
            rainfall_lag = rainfall 
            
        forecast_results.append({
            "market_name": market_name,
            "current_price": round(row['Current_Month price'], 2),
            "forecast_series": market_forecasts
        })

    # --- Risk Assessment & Aggregation ---
    
    # 1. Calculate Monthly State Averages from Forecasts
    state_monthly_avgs = { m[0]: [] for m in future_months }
    for mkt in forecast_results:
        for f in mkt['forecast_series']:
            state_monthly_avgs[f['month']].append(f['price'])
            
    state_summary_series = []
    final_risk_data = [] # Market details with risk
    
    current_state_avg = np.mean([m['current_price'] for m in forecast_results])
    
    # Calculate Avg per month
    month_stats = {}
    for m, prices in state_monthly_avgs.items():
        avg_price = np.mean(prices)
        std_dev = np.std(prices)
        month_stats[m] = {"avg": avg_price, "std": std_dev}
        
        # Determine trend vs previous (simplified for first month vs current)
        trend = "Stable" # Placeholder logic
        state_summary_series.append({
            "month": m,
            "avg_predicted_price": round(avg_price, 2),
            "trend": trend
        })

    # 2. Risk Scoring per Market
    for mkt in forecast_results:
        # Simple risk score: Average Z-score across the 3 months
        z_scores = []
        deviations = []
        
        for f in mkt['forecast_series']:
            m_stat = month_stats[f['month']]
            # Deviation from state avg
            deviation_pct = ((f['price'] - m_stat['avg']) / m_stat['avg']) * 100
            deviations.append(deviation_pct)
            
            # Z-score
            if m_stat['std'] > 0:
                z = (f['price'] - m_stat['avg']) / m_stat['std']
            else:
                z = 0
            z_scores.append(abs(z))
            
            # Add context to forecast object
            f['deviation_from_state'] = f"{deviation_pct:.2f}%"

        avg_z_score = np.mean(z_scores)
        avg_deviation = np.mean([abs(d) for d in deviations])
        
        alert = "Normal"
        if avg_deviation > 5.0:
            alert = "High Risk" if avg_deviation > 15.0 else "Risk Alert"

        mkt_detail = {
            "market_name": mkt['market_name'],
            "market_type": "APMC", # Static as dataset is APMC
            "current_price": mkt['current_price'],
            "forecast_series": mkt['forecast_series'],
            "risk_score": round(avg_z_score, 2),
            "alert": alert
        }
        final_risk_data.append(mkt_detail)

    # --- JSON Construction ---
    output_json = {
        "report_metadata": {
            "commodity": "Wheat",
            "state": "Maharashtra",
            "base_month": "December 2021",
            "horizon": "3 Months (Jan-Mar 2022)"
        },
        "state_summary": {
            "current_avg_price": round(current_state_avg, 2),
            "forecast_series": state_summary_series
        },
        "market_details": final_risk_data
    }

    # Print JSON to terminal (as requested)
    # Save JSON to file
    # json_output_dir is already defined and created at top of function
    json_file_path = os.path.join(json_output_dir, "forecast_report.json")
    
    with open(json_file_path, "w") as f:
        json.dump(output_json, f, indent=2)
        
    print(f"Forecast report saved to: {json_file_path}")

if __name__ == "__main__":
    forecast_prices()
