from cuml.metrics.regression import mean_squared_error, mean_absolute_error, r2_score, mean_squared_log_error
from cuml.metrics.accuracy import accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score
from cuml.metrics import confusion_matrix
import numpy as np
import cupy as cp

def get_mse(y_true, y_pred):
    return mean_squared_error(y_true, y_pred)

def get_mae(y_true, y_pred):
    return mean_absolute_error(y_true, y_pred)

def get_r2(y_true, y_pred):
    return r2_score(y_true, y_pred)


def get_msle(y_true, y_pred):
    return mean_squared_log_error(y_true, y_pred)

def get_metrics(y_true, y_pred):
    # Convert input arrays to supported data types
    supported_dtypes = ['float32', 'float64', 'int32', 'int64']
    if y_true.dtype not in supported_dtypes:
        y_true = y_true.astype('float64')
    if y_pred.dtype not in supported_dtypes:
        y_pred = y_pred.astype('float64')

    try:
        mse = get_mse(y_true, y_pred)
        mae = get_mae(y_true, y_pred)
        r2 = get_r2(y_true, y_pred)
        msle = get_msle(y_true, y_pred)
    except Exception as e:
        print(f"Error calculating metrics: {str(e)}")
        return None, None, None, None

    try:
        mse  = round(float(mse), 8)
        mae  = round(float(mae), 8)
        r2   = round(float(r2), 8)
        msle = round(float(msle), 8)
    except Exception as e:
        print(f"Error rounding metrics: {str(e)}")
        return None, None, None, None

    return mse, mae, r2, msle


def get_confusion_matrix(y_true, y_pred):

    matrix = confusion_matrix(y_true.astype(np.int32), y_pred.astype(np.int32))
    return matrix
    
def get_rf_metrics(y_true, y_pred):
    y_true = cp.asnumpy(y_true)
    y_pred = cp.asnumpy(y_pred)
    
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted', labels=np.unique(y_pred))
    recall = recall_score(y_true, y_pred, average='weighted', labels=np.unique(y_pred))
    f1 = f1_score(y_true, y_pred, average='weighted', labels=np.unique(y_pred))
    
    return accuracy, precision, recall, f1