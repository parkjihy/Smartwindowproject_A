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


# MinMax Scaling 프로세스
def minmax_scaler(tgt_arr, min_var=None, max_var=None):
    if min_var is None:
        min_var = min(tgt_arr)
    if max_var is None:
        max_var = max(tgt_arr)
    tgt_df = (tgt_arr - min_var) / (max_var - min_var) * 10000
    return tgt_df

# 모델 학습
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

# 모델 세이브
def save_model(model, model_path):
    try:
        model.save_model(model_path)
        print(f"Model saved to {model_path}")
    except Exception as e:
        print(f"Error saving the model: {str(e)}")

# 모델 로드
def load_random_forest_regression_model(model_path):
    try:
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        return model
    except Exception as e:
        print(f"Error loading the Random Forest regression model: {str(e)}")
        return None

# 재학습 함수
def retrain_RF_regression_model(loaded_model, data, input_col, output_col, epochs=50):
    try:
        temp_arr = data.copy()
        X = temp_arr[input_col]
        y = temp_arr[output_col]
        train_x, test_x, train_y, test_y = train_test_split(X, y, test_size=0.2, shuffle=True, random_state=42)
        loaded_model.fit(train_x, train_y, verbose=True, eval_set=[(test_x._get_numeric_data(), test_y)], eval_metric='rmse')
        return loaded_model
    except Exception as e:
        print(f"Error retraining the model: {str(e)}")
        return None

# 예측 함수
def predict_and_save_results(model, data, input_col, output_col, result_csv_path):
    try:
        temp_data = data.copy()

        # 조건에 따라 state 예측 또는 1로 설정
        mask = (temp_data['month'] >= 6) & (temp_data['month'] <= 8) & (temp_data['living_motion'] == 0) & (temp_data['bedroom_motion'] == 0) & (temp_data['kitchen_motion'] == 0)
        temp_data.loc[mask, 'state'] = 1

        # 조건에 맞지 않는 데이터 추출
        predict_data = temp_data[~mask]

        # 예측을 위한 입력 데이터
        X_predict = predict_data[input_col]

        # 예측 수행
        predictions = model.predict(X_predict)

        # 예측 결과를 데이터프레임에 추가
        predict_data['state'] = predictions

        # 결과를 CSV 파일로 저장
        predict_data.to_csv(result_csv_path, index=False)
        print(f"Predictions saved to {result_csv_path}")
    except Exception as e:
        print(f"Error making predictions and saving results: {str(e)}")

if __name__ == "__main__":
    colname_arr = ['month', 'hour', 'minute', 'living_motion', 'bedroom_motion', 'kitchen_motion', 'temp', 'out_lux', 'light', 'state']
    input_col = ['month', 'hour', 'minute', 'living_motion', 'bedroom_motion', 'kitchen_motion', 'temp', 'out_lux', 'light']
    output_col = ['state']
    model_load_dir = '/gdrive/MyDrive/01. smart/2023/result_models/random_forest_model.pkl'
      # 테스트 예측 수행시 결과 엑셀파일을 저장할 경로
    result_dir = '/gdrive/MyDrive/01. smart/2023/result_xg/rf_result4.csv'
    data = pd.read_excel('/gdrive/MyDrive/01. smart/2023/data_09/total_09.xlsx', engine='openpyxl')
    sliced_data = data[colname_arr]

    # 모델 로드
    loaded_model = load_random_forest_regression_model(model_load_dir)

    # 재학습 (새로운 데이터로)
    #shuffled_data = shuffle(sliced_data)
    # 처음 50개 행 추출
    #first_50_rows = shuffled_data[:50]
    #retrained_model = retrain_xgboost_regression_model(loaded_model, sliced_data, input_col, output_col, epochs=50)

    # 예측 및 결과 저장
    predict_and_save_results(loaded_model, sliced_data, input_col, output_col, result_dir )