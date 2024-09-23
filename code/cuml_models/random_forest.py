from cuml.ensemble import RandomForestRegressor as cuRFR
from cuml.ensemble import RandomForestClassifier as cuRFC
from cuml.preprocessing import LabelEncoder
import cupy as cp
import cudf
from .metrics import get_metrics, get_rf_metrics

def make_rf_prediction(df, target_column, feature_column):
    # Create a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    
    # Check if the feature column is categorical
    is_feature_categorical = df_copy[feature_column].dtype == 'object'
    is_target_categorical = df_copy[target_column].dtype == 'object'
    
    try:
        if is_feature_categorical:
            le_feature = LabelEncoder()
            encoded_feature = le_feature.fit_transform(df_copy[feature_column])
            df_copy[feature_column] = encoded_feature
        
        if is_target_categorical:
            le_target = LabelEncoder()
            encoded_target = le_target.fit_transform(df_copy[target_column])
            df_copy[target_column] = encoded_target
    except Exception as e:
        print(f"Error encoding columns: {str(e)}")
        return None, None, None, None, None, None, None, None
    
    # Select the feature column and target column
    X = df_copy[[feature_column]]
    y = df_copy[target_column]
    
    try:
        if is_target_categorical:
            model = cuRFC()
        else:
            model = cuRFR()
        model.fit(X, y)
        future_pred = model.predict(X)
    except Exception as e:
        print(f"Error fitting the model: {str(e)}")
        return None, None, None, None, None, None, None, None
    
    try:
        future_df = cudf.DataFrame({
            feature_column: df_copy[feature_column],
            target_column: future_pred
        })
    except Exception as e:
        print(f"Error creating future dataframe: {str(e)}")
        return None, None, None, None, None, None, None, None
    
    try:
        y_cupy = cp.asarray(y)
        future_pred_cupy = cp.asarray(future_pred)
        
        mask = ~(cp.isnan(y_cupy) | cp.isnan(future_pred_cupy))
        y_cupy = y_cupy[mask]
        future_pred_cupy = future_pred_cupy[mask]
    except Exception as e:
        print(f"Error converting to cupy array or removing NaN values: {str(e)}")
        return None, None, None, None, None, None, None, None
    
    try:
        if is_target_categorical:
            accuracy, precision, recall, f1 = get_rf_metrics(y_cupy, future_pred_cupy)
            return future_df, feature_column, target_column, accuracy, precision, recall, f1, is_target_categorical
        else:
            mse, mae, r2, msle = get_metrics(y_cupy, future_pred_cupy)
            return future_df, feature_column, target_column, mse, mae, r2, msle, is_target_categorical
    except Exception as e:
        print(f"Error calculating metrics: {str(e)}")
        return None, None, None, None, None, None, None, None