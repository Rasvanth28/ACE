# Wheat Price Forecasting Model Documentation

## 1. Features Used for Prediction
The model utilizes a combination of historical price data, volume (arrival) data, and external environmental/economic factors to predict future Wheat prices.

### Temporal & Categorical Features:
- **`Year`**: The year of the record (e.g., 2021, 2022).
- **`Month_Num`**: Integer representation of the month (1 for January, 12 for December).
- **`Market_Encoded`**: Label Encoded numerical value representing the specific APMC market.

### Lag Features (Time Series Dynamics):
- **`Prev_Month price`**: The price of Wheat in the same market from the previous month ($t-1$).
- **`Prev_2_Month price`**: The price of Wheat in the same market from two months ago ($t-2$).
- **`Price_Velocity`**: The rate of change in price between the last two months ($Price_{t-1} - Price_{t-2}$). This captures the momentum of price movements.
- **`Current_Month arrivals`**: The quantity of Wheat arriving at the market in the current month.
- **`Prev_Month arrivals`**: The quantity of Wheat arrivals from the previous month.
- **`Rainfall_Lag`**: Rainfall in millimeters from the previous month.

### External Factors:
- **`Rainfall_mm`**: Current month's rainfall.
- **`Diesel_Price_Rs_per_Litre`**: Cost of transportation/fuel.
- **`Irrigation_Water_Usage_MCM`**: Water availability for agriculture.
- **`msp`**: Minimum Support Price set by the government, acting as a price floor.
- **`Temperature`**: Average temperature, affecting crop yield and storage.

---

## 2. Model Used for Data Imputation
Missing data handling is a critical step in our pipeline. We employed **Iterative Imputation (MICE)**.

- **Algorithm**: `sklearn.impute.IterativeImputer`
- **Mechanism**: This method models each feature with missing values as a function of other features. It performs multiple regressions in a round-robin fashion.
- **Why?**: Unlike simple mean/median imputation, MICE preserves the statistical relationships (correlations) between variables (e.g., Price and Arrivals).
- **Application**: Used primarily for filling missing values in `Price` and `Arrival` histograms before feature engineering.

---

## 3. Model Used for Price Prediction
We used a **Gradient Boosting Regressor** for predicting Wheat prices.

- **Algorithm**: `sklearn.ensemble.GradientBoostingRegressor`
- **Configuration**:
    - `n_estimators`: 100 (Number of boosting stages)
    - `learning_rate`: 0.1 (Contribution of each tree)
    - `max_depth`: 5 (Maximum depth of individual regression estimators)
    - `random_state`: 42 (For reproducibility)
- **Recursive Forecasting**: The model predicts one month ahead. For a multi-month horizon (e.g., Jan-Mar), the predicted price for month $t$ is fed back as an input (`Prev_Month price`) for predicting month $t+1$.

---

## 4. Analysis of Training vs Validation Loss and Accuracy
(Based on training on 2021 data and validating on 2022 data)

- **Training Performance**: The model fits the training data (2021) extremely well, with high $R^2$ scores and low MSE loss. This is expected for Gradient Boosting models.
- **Validation (2022) Performance**:
    - **$R^2$ Score**: ~0.30 (approx). This indicates that while the model captures some variance, the shift from 2021 to 2022 dynamics (temporal drift) introduces challenge.
    - **MAPE (Mean Absolute Percentage Error)**: ~7.91%. This is a strong result, meaning on average, the model's price predictions are within ~8% of the actual market price.
- **Loss Curves** (visible in `forecast_plots.png`):
    - **Training Loss**: Decreases steadily as more trees are added.
    - **Validation Loss**: Decreases initially and then stabilizes. This gap indicates some overfitting to the 2021 regime, which is natural given the limited 1-year training window.

---

## 5. JSON Output Structure
The `forecast_report.json` file is structured to be consumed by downstream applications (Web/App UI).

1.  **`report_metadata`**:
    - Contextual info: Commodity (`Wheat`), State (`Maharashtra`), Base Month for prediction, and the Forecast Horizon.
2.  **`state_summary`**:
    - Aggregated view for the entire state.
    - `current_avg_price`: Baseline average across all markets.
    - `forecast_series`: Month-by-month average predicted price for the state.
3.  **`market_details`**:
    - A list of objects, one per market (e.g., "Aurangabad APMC").
    - `current_price`: Last known price.
    - `forecast_series`: Array of 3 objects (Jan, Feb, Mar) containing:
        - `month`: Name of month.
        - `price`: Predicted price.
        - `trend`: "Up" or "Down" vs previous month.
        - `deviation_from_state`: How much this market differs from the state average (%).
    - `risk_score`: A Z-score based metric indicating volatility or extreme pricing.
    - `alert`: "Normal", "Risk Alert", or "High Risk" based on the deviation.

---

## 6. Analysis of Actual vs Predicted Prices
(Based on Jan-Mar 2022 Comparison)

- **State Level Predictability**: The model is highly effective at predicting the **State Average** price. As seen in `forecast_comparison.png`, the predicted state average (Dotted Black Line) follows the actual state average (Solid Black Line) trend very closely.
- **Market Level Variance**: Individual markets show more variance. While the model captures the general direction (seasonality) for most markets, some specific local spikes are smoothed out.
- **Trend Capture**: The model successfully predicted the general price stability/slight increase observed in early 2022 for the majority of markets.

---

## 7. Future Improvements
To enhance model accuracy and robustness, we plan to:

1.  **Expand Training Data**: The current strict split (Train 2021 only) limits the model's exposure to long-term trends. Incorporating pre-2021 data (if available) or using a rolling window approach would significantly improve the $R^2$ score.
2.  **Hyperparameter Tuning**: systematically search for optimal parameters (Grid Search) for `learning_rate` and `max_depth` to better generalize to unseen years.
3.  **Advanced Regressors**: Experiment with **XGBoost**, **LightGBM**, or **CatBoost**, which often handle categorical variables (`Market`) and missing data better than standard Gradient Boosting.
4.  **Ensemble Methods**: Combine predictions from a linear model (ARIMA) and a tree-based model (GBR) to capture both linear trends and non-linear interactions.
5.  **External Features**: Integrate real-time policy data (Export bans, Import duties) and global Wheat indices, which strongly influence local prices.
