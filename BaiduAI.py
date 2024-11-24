import requests
import time
import configparser
import requests
import base64
import json

def get_baidu_access_token(client_id, client_secret, force_request=False, main_window = None):
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')

    # 检查是否存在BAIDU_AI_ACCESS_TOKEN节
    if 'BAIDU_AI_ACCESS_TOKEN' not in config:
        config['BAIDU_AI_ACCESS_TOKEN'] = {}

    # 检查上次请求时间
    last_request_time = config['BAIDU_AI_ACCESS_TOKEN'].get('last_request_time', 0)
    current_time = int(time.time())
    if not force_request and current_time - int(last_request_time) < 10 * 60:
        return config['BAIDU_AI_ACCESS_TOKEN']['access_token']

    if main_window:
        main_window.output_text_ctrl.AppendText("正在请求Access Token……\n")

    # 构建请求参数
    params = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    # 发送请求
    response = requests.post('https://aip.baidubce.com/oauth/2.0/token', data=params)
    response_json = response.json()

    # 检查响应
    if 'access_token' in response_json:
        access_token = response_json['access_token']
        expires_in = response_json['expires_in']

        # 更新配置文件
        config['BAIDU_AI_ACCESS_TOKEN']['access_token'] = access_token
        config['BAIDU_AI_ACCESS_TOKEN']['last_request_time'] = str(current_time)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        return access_token
    else:
        # 处理错误
        error_code = response_json.get('error', 'unknown_error')
        error_description = response_json.get('error_description', 'Unknown error')
        if main_window:
            main_window.output_text_ctrl.AppendText(f"Error: {error_code} - {error_description}")
        else:
            raise Exception(f"Error: {error_code} - {error_description}")
        
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def map_language_to_api_param(language):
    language_map = {
        "English": "ENG",
        "Chinese": "CHN_ENG",
        "Japanese": "JAP",
        "Korean": "KOR"
    }
    return language_map.get(language, "CHN_ENG")  # 默认返回中文

def perform_baidu_ocr(image_path, source_language="CHN_ENG", main_window = None):

    api_language = map_language_to_api_param(source_language)

        # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')

    # 从配置文件中获取client_id和client_secret
    client_id = config['YUTORI_TRANS_CONFIG']['baidu_ai_ocr_app_key']
    client_secret = config['YUTORI_TRANS_CONFIG']['baidu_ai_ocr_secrct_key']

    # 调用函数获取access_token
    try:
        access_token = get_baidu_access_token(client_id, client_secret,main_window = main_window)
    except Exception as e:
        main_window.output_text_ctrl.AppendText(f"Error: {e}")
    
    # 构建请求URL
    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general?access_token={access_token}"
    
    # 读取并编码图片
    image_base64 = encode_image_to_base64(image_path)
    
    # 构建请求体
    payload = {
        "image": image_base64,
        "language_type": api_language,
        "paragraph": "true"
    }
    
    # 发送POST请求
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    # 解析响应
    try:
        response_json = response.json()
        if 'error_code' in response_json:
            main_window.output_text_ctrl.AppendText(f"Error {response_json['error_code']}: {response_json['error_msg']}")
        return response_json
    except json.JSONDecodeError:
        main_window.output_text_ctrl.AppendText("Failed to decode response from Baidu OCR API")

if __name__ == "__main__":
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')

    # 从配置文件中获取client_id和client_secret
    client_id = config['YUTORI_TRANS_CONFIG']['baidu_ai_ocr_app_key']
    client_secret = config['YUTORI_TRANS_CONFIG']['baidu_ai_ocr_secrct_key']

    # 调用函数获取access_token
    try:
        access_token = get_baidu_access_token(client_id, client_secret, force_request=True)
        print(f"Access Token: {access_token}")
    except Exception as e:
        print(f"Error: {e}")