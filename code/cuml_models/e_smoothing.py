import cudf
import cupy as cp
from cuml import ExponentialSmoothing
import numpy as np
import pandas as pd
from .metrics import get_metrics

def make_timeseries_prediction(df, target_column, feature_column, periods_to_predict):
    try:
        numeric_cols = df.select_dtypes(include=[cp.number]).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        for col in datetime_cols:
            if feature_column in col:
                feature_column = col
                break
            else:
                return "Feature column not found in datetime columns." 
            
        df = df.dropna().drop_duplicates()
        
        if target_column not in numeric_cols:
            df[target_column] = df[target_column].astype(cp.float32)
            numeric_cols = df.select_dtypes(include=[cp.number]).columns.tolist()
            if target_column not in numeric_cols:
                raise ValueError(f"Target column '{target_column}' must be numeric.")
        
        if not datetime_cols:
            raise ValueError("No datetime column found in the DataFrame.")
        
        datetime_column = feature_column
        
        # Set the datetime column as index and sort
        df = df.set_index(datetime_column).sort_index()
        
        # Resample to daily frequency, using the last value of each day
        df_daily = df.resample('D').last().dropna()
        
        # Prepare the data
        y = df_daily[target_column].to_cupy()

        # Determine seasonal_periods (assuming daily data, adjust as needed)
        seasonal_periods = 7  # for weekly seasonality

        # Create and fit the model
        model = ExponentialSmoothing(y, seasonal_periods=seasonal_periods)
        model.fit()

        # Get components for past predictions
        level = model.get_level()
        trend = model.get_trend()
        season = model.get_season()
        past_pred = cp.asnumpy(level + trend + season)

        # Make future predictions
        future_pred = cp.asnumpy(model.forecast(periods_to_predict))

        try:
            past_df = df_daily[[target_column]].copy()
            
            # Ensure past_pred length matches past_df
            if len(past_pred) > len(past_df):
                past_pred = past_pred[-len(past_df):]
            elif len(past_pred) < len(past_df):
                past_pred = np.pad(past_pred, (len(past_df) - len(past_pred), 0), 'constant', constant_values=np.nan)
            
            past_df['Prediction'] = past_pred
        except Exception as e:
            print(f"Error creating past predictions DataFrame: {str(e)}")
            return None, None

        try:
            last_date = df_daily.index[-1].astype('datetime64[ns]')
           
            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods_to_predict, freq='D')

            future_index = cudf.Series(future_dates)
            
            future_df = cudf.DataFrame(index=future_index)
            
            future_df[target_column] = cudf.Series([cudf.NA] * len(future_pred), dtype=cp.float32, index=future_index)
            
            future_df['Prediction'] = cudf.Series(future_pred, dtype=cp.float32, index=future_index)

        except Exception as e:
            print(f"Error creating future predictions DataFrame: {str(e)}")
            return None, None

        past_df.index = cudf.DatetimeIndex(past_df.index.astype('datetime64[ns]'))
        
        past_df.index.name = 'Datetime'
        future_df.index.name = 'Datetime'
        
        try:
            for col in past_df.columns:
                past_df[col] = past_df[col].astype(cp.float32)
            for col in future_df.columns:
                future_df[col] = future_df[col].astype(cp.float32)
        except  Exception as e:
            print(f"Error converting column types to float32: {str(e)}")
            return None, None
            
        # Replace NaN values with cudf.NA to ensure consistency
        past_df = past_df.fillna(cudf.NA)
        future_df = future_df.fillna(cudf.NA)
        
        score = model.score()
        print(f"Model score: {score}")
        
         # Convert y and past_pred to cupy arrays for metrics calculation
        y_cupy = cp.array(y, dtype=cp.float32)
        past_pred_cupy = cp.array(past_pred, dtype=cp.float32)
        
        # Remove any NaN values before calculating metrics
        mask = ~(cp.isnan(y_cupy) | cp.isnan(past_pred_cupy))
        y_cupy = y_cupy[mask]
        past_pred_cupy = past_pred_cupy[mask]
        
        if len(y_cupy) > 0 and len(past_pred_cupy) > 0:
            mse, mae, r2, msle = get_metrics(y_cupy, past_pred_cupy)
            
        else:
            print("Unable to calculate metrics due to insufficient data")
            
       
        return past_df, future_df, mse, mae, r2, msle

    
    

    except Exception as e:
        print(f"Error in make_timeseries_prediction: {str(e)}")
        return None, None
    

    