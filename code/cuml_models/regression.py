import cudf
import cupy as cp
from cuml.linear_model import LinearRegression
from .metrics import get_metrics
from cuml.preprocessing import LabelEncoder

def make_prediction(df, target_column, feature_column):
    # Create a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()
    
    # Check if the feature column is categorical
    is_feature_categorical = df_copy[feature_column].dtype == 'object'
    
    try:
        if is_feature_categorical:
            le_feature = LabelEncoder()
            encoded_feature = le_feature.fit_transform(df_copy[feature_column])
            df_copy[feature_column] = encoded_feature
          
    except Exception as e:
        print(f"Error encoding feature column: {str(e)}")
    
       
   
    # Select the feature column and target column
    X = df_copy[[feature_column]]
    y = df_copy[target_column]

    try:
        clf = LinearRegression(copy_X=True)
        clf.fit(X, y)
        fc = clf.predict(X)
    except Exception as e:
        print(f"Error fitting the model: {str(e)}")
        return None, None, None, None, None, None, None
    
    try:
        future_df = cudf.DataFrame({
            feature_column: df_copy[feature_column],
            target_column: fc
        })
    except Exception as e:
        print(f"Error creating future dataframe: {str(e)}")
        return None, None, None, None, None, None, None
    
    try:
        y_cupy = y.to_cupy()
        fc_cupy = cp.asarray(fc)
    except Exception as e:
        print(f"Error converting to cupy array: {str(e)}")
        return None, None, None, None, None, None, None
    
    try:
        mask = ~(cp.isnan(y_cupy) | cp.isnan(fc_cupy))
        y_cupy = y_cupy[mask]
        fc_cupy = fc_cupy[mask]
    except Exception as e:
        print(f"Error removing NaN values: {str(e)}")
        return None, None, None, None, None, None, None
    
    
    if len(y_cupy) > 0 and len(fc_cupy) > 0:
        mse, mae, r2, msle = get_metrics(y_cupy, fc_cupy)
    else:
        print("Unable to calculate metrics due to insufficient data")
        mse = mae = r2 = msle = None

    if is_feature_categorical:
        future_df[feature_column] = le_feature.inverse_transform(future_df[feature_column])
      
        
    return future_df, feature_column, target_column, mse, mae, r2, msle