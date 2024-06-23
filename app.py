from flask import Flask, render_template, jsonify, request
import requests
from time import sleep
from main import run
import threading
import json
import traceback
import datetime

app = Flask(__name__)

def get_json_data(dir):
    with open(dir, "r") as json_file:
        data = json.load(json_file)
        # 추가 절차 : json에서 operation_type을 따라 roomtype을 변경함.
        if data['coeff_dict']['operation_type_livingroom'] == 'energy_saving_mode_temperature':
            data['coeff_dict']['roomtype_livingroom'] = 'temperature'
        else:
            data['coeff_dict']['roomtype_livingroom'] = 'lux'

        if data['coeff_dict']['operation_type_bedroom1'] == 'energy_saving_mode_temperature':
            data['coeff_dict']['roomtype_bedroom1'] = 'temperature'
        else:
            data['coeff_dict']['roomtype_bedroom1'] = 'lux'

        if data['coeff_dict']['operation_type_bedroom2'] == 'energy_saving_mode_temperature':
            data['coeff_dict']['roomtype_bedroom2'] = 'temperature'
        else:
            data['coeff_dict']['roomtype_bedroom2'] = 'lux'

        if data['coeff_dict']['operation_type_bedroom3'] == 'energy_saving_mode_temperature':
            data['coeff_dict']['roomtype_bedroom3'] = 'temperature'
        else:
            data['coeff_dict']['roomtype_bedroom3'] = 'lux'

        return data['coeff_dict'], data['sensor_bypass_dict'], data['sensor_customize_dict'], data['data_report_dict']


@app.before_first_request
def activate_job():
    def run_job():
        while True:
            try:
                run()
            except:
                print("error")
                traceback.print_exc()
            sleep(60)
    thread = threading.Thread(target=run_job)
    thread.start()


@app.route('/')
def home():
    name = "ha"
    return render_template('test.html', name=name)


@app.route('/ui', methods=['POST'])
def ui():
    web_json = request.get_json()

    json_dir = "C:/dataknit_windowcontroller/data_heri.json"

    # 보험
    # if os.path.exists(new_json_dir) == True:
    #     coeff_dict, sensor_bypass_dict, sensor_customize_dict = get_json_data(new_json_dir)
    # else:
    #     coeff_dict, sensor_bypass_dict, sensor_customize_dict = get_json_data(json_dir)

    coeff_dict, sensor_bypass_dict, sensor_customize_dict, data_report_dict = get_json_data(json_dir)

    room_name = web_json['location']
    # coeff_dict 업데이트
    coeff_dict['operation_type_' + room_name] = web_json['operation_type']
    coeff_dict['E_o_set_' + room_name] = int(web_json['E_o_set'])
    coeff_dict['E_i_set_' + room_name] = int(web_json['E_i_set'])
    coeff_dict['T_i_set_' + room_name] = float(web_json['T_i_set'])
    coeff_dict['S_plug_set_' + room_name] = float(web_json['S_plug_set'])
    coeff_dict['summertime_' + room_name] = [
        int(web_json['summertime_start'].split('-')[1] + web_json['summertime_start'].split('-')[2]),
        int(web_json['summertime_end'].split('-')[1] + web_json['summertime_end'].split('-')[2])]
    if web_json['operation_type'] == 'energy_saving_mode_temperature':
        coeff_dict['roomtype_' + room_name] = 'temperature'
    elif web_json['operation_type'] == 'energy_saving_mode_lux':
        coeff_dict['roomtype_' + room_name] = 'lux'
    else:
        coeff_dict['roomtype_' + room_name] = 'lux'

    # sensor_bypass_dict 업데이트
    sensor_bypass_dict['lux_pass_' + room_name] = web_json['E_o_bypass']
    sensor_bypass_dict['temperature_pass_' + room_name] = web_json['T_i_bypass']
    sensor_bypass_dict['motion_pass_' + room_name] = web_json['Mo_bypass']
    sensor_bypass_dict['smartplug_pass_' + room_name] = web_json['S_plug_bypass']

    # sensor_customize_dict 업데이트
    sensor_customize_dict['lux_custom_' + room_name] = int(web_json['E_o'])
    sensor_customize_dict['temperature_custom_' + room_name] = float(web_json['T_i'])
    sensor_customize_dict['motion_custom_' + room_name] = int(web_json['Mo'])
    sensor_customize_dict['smartplug_custom_' + room_name] = float(web_json['S_plug'])

    # json_new 로 저장
    with open(json_dir, 'w') as file_output:
        json.dump({
            'coeff_dict': coeff_dict,
            'sensor_bypass_dict': sensor_bypass_dict,
            'sensor_customize_dict': sensor_customize_dict,
            'data_report_dict': data_report_dict
        }, file_output, indent=4)

    return jsonify(result="success", result2="SUCCESS")


@app.route('/get_json', methods=['POST'])
def get_json():

    json_dir = "C:/dataknit_windowcontroller/data_heri.json"
    result_json_dir = "C:/dataknit_windowcontroller/data_heri.json"

    coeff_dict, sensor_bypass_dict, sensor_customize_dict, data_report_dict = get_json_data(result_json_dir)
    result_json = {
        'coeff_dict': coeff_dict,
        'sensor_bypass_dict': sensor_bypass_dict,
        'sensor_customize_dict': sensor_customize_dict,
        'data_report_dict': data_report_dict
    }

    coeff_dict, sensor_bypass_dict, sensor_customize_dict, data_report_dict = get_json_data(json_dir)
    result = {
        'coeff_dict': coeff_dict,
        'sensor_bypass_dict': sensor_bypass_dict,
        'sensor_customize_dict': sensor_customize_dict,
        'data_report_dict': data_report_dict,
        'result_json': result_json
    }

    return jsonify(json.dumps(result))


@app.route('/window', methods=['POST'])
def window():
    web_json = request.get_json()
    # 입력값으로 창 제어
    from main import window_control, get_window_sensor, refresh_window
    import time
    # if web_json['window'] == 10:
    #     control_value = 9
    # else:
    #     control_value = web_json['window']
    window_control(web_json['location'], web_json['window'])
    # 창 제어 이후 값을 가져와 재출력
    # 새로고침 제어를 post한 뒤 5초정도를 대기함
    refresh_window()
    time.sleep(5)
    res_window = get_window_sensor(web_json['location'])
    web_json['window'] = json.loads(res_window['state'].replace("'", '"'))['value']
    return jsonify(json.dumps(web_json))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # app.run(debug=False, host='0.0.0.0', port=7890)
    app.run('203.255.176.198', port=7890, debug=False)




