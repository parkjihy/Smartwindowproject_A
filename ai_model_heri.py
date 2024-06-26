# -*- coding: utf-8 -*-
"""ai_model_smartwindow

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NI-HqeLy4hB52BDHe4wGcRCjxR_-qXOz
"""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pickle
import os
import datetime
import shutil

def minmax_scaler(tgt_arr, min_var=None, max_var=None):
    if min_var is None:
        min_var = min(tgt_arr)
    if max_var is None:
        max_var = max(tgt_arr)
    tgt_df = (tgt_arr - min_var) / (max_var - min_var) * 10000
    return tgt_df

def fit_model(model, data, input_col, output_col):
    try:
        temp_arr = data.copy()
        X = temp_arr[input_col]
        y = temp_arr[output_col]
        train_x, test_x, train_y, test_y = train_test_split(X, y, test_size=0.2, shuffle=True, random_state=42)
        model.fit(train_x._get_numeric_data(), train_y)
        return model
    except Exception as e:
        print(f"Error fitting the model: {str(e)}")
        return None

def save_model(model, model_path = './ai_model_heri.pkl'):
    model.save_model(model_path)

def load_model(model_path = './ai_model_heri.pkl'):
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    return model

def train_model(model, data_dir = './data_for_train_heri.csv', input_col=['month', 'hour', 'minute', 'day', 'smart_plug', 'motion', 'light1', 'light2', 'temp', 'out_lux'], output_col=['state'], epochs=50):
    try:
        data = pd.read_csv(data_dir)
        X = data[input_col]
        y = data[output_col]
        train_x, test_x, train_y, test_y = train_test_split(X, y, test_size=0.2, shuffle=True, random_state=42)
        model.fit(train_x, train_y, verbose=True, eval_set=[(test_x._get_numeric_data(), test_y)], eval_metric='rmse')
        backup_string = datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.move(data_dir, data_dir[:-4] + '_backup_' + backup_string + '.csv')
        return model
    except Exception as e:
        print(f"Error retraining the model: {str(e)}")
        return None

def predict_model(model, input_arr):
    if input_arr[0] >= 6 and input_arr[0] <= 8 and input_arr[5] == 0:
        return 1
    else:
        return model.predict([input_arr])[0]

def save_train_data_byline(data_arr, filedir = './data_for_train_heri.csv'):
    if os.path.exists(filedir) == False:
        f = open(filedir, 'w')
        f.write(
            'month,hour,minute,day,smart_plug,motion,light1,light2,temp,out_lux,state\n')
        f.close()

    f = open(filedir, 'a')
    f.write(
        str(data_arr[0]) + ',' +
        str(data_arr[1]) + ',' +
        str(data_arr[2]) + ',' +
        str(data_arr[3]) + ',' +
        str(data_arr[4]) + ',' +
        str(data_arr[5]) + ',' +
        str(data_arr[6]) + ',' +
        str(data_arr[7]) + ',' +
        str(data_arr[8]) + ',' +
        str(data_arr[9]) + ',' +
        str(data_arr[10]) + ',' + "\n"
    )
    f.close()

def load_model_and_predict(input):
    model = load_model('./ai_model_heri.pkl')
    return predict_model(model, input)

def load_model_and_train():
    model = load_model('./ai_model_heri.pkl')
    train_model(model)
    save_model(model)