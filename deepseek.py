import json
import configparser
from openai import OpenAI

def process_json(input_json):
    # 解析输入的JSON数据
    data = input_json
    
    # 初始化结果字典
    result = {
        "paragraphs_result": []
    }
    
    # 遍历paragraphs_result
    for paragraph in data["paragraphs_result"]:
        words_result_idx = paragraph["words_result_idx"]
        
        # 获取第一个单词的top和left
        first_word_idx = words_result_idx[0]
        first_word = data["words_result"][first_word_idx]
        top = first_word["location"]["top"]
        left = first_word["location"]["left"]
        
        # 创建新的组
        new_group = {
            "words": [data["words_result"][idx]["words"] for idx in words_result_idx],
            "top": top,
            "left": left
        }
        
        # 将新组添加到结果中
        result["paragraphs_result"].append(new_group)
    # 返回新的JSON字符串
    return json.dumps(result, ensure_ascii=False, indent=4)

# Please install OpenAI SDK first: `pip3 install openai`

def deepseek_AI_sort(text,main_window = None):

        # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = config['YUTORI_TRANS_CONFIG']['deepseek_api_key']
    if not api_key:
        print("no api key")
        return

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    system_prompt = """You are a professional, accurate, and intelligent text processing engine.
Users will send you texts that have been segmented and stored in JSON format. These texts have undergone OCR and may contain "sorting errors", "recognition errors", and "omissions".
For each set of texts, you need to correct them, remove erroneous parts, fill in missing parts, and reorder them to ensure that the resulting segments are correctly expressed.
Fill in the entire text that you believe is correct into JSON and return it to the user.
For example:
{"paragraphs_result": [{"words": ["cat.", "am", "I"], "top": 1, "left": 1},{"words": ["Y0u", "are", "mouse."], "top": 2, "left": 2}]}
Output:
{"paragraphs_result": [{"words": ["I am cat."], "top": 1, "left": 1},{"words": ["You are mouse."], "top": 2, "left": 2}]}
For Japanese requests, combining the text from the END to the BEGIN can result in higher accuracy.
You can only output in JSON format. No explanations or comments are allowed."""

    user_prompt = text

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    # print(json.loads(response.choices[0].message.content))
    # main_window.output_text_ctrl.AppendText(response.choices[0].message.content)
    return response.choices[0].message.content

def deepseek_AI_trans(text,main_window = None):

        # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')

    api_key = config['YUTORI_TRANS_CONFIG']['deepseek_api_key']
    if not api_key:
        print("no api key")
        return

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    system_prompt = """You are a professional, accurate, and intelligent translation engine.
Users will send you several segments stored in JSON format. You need to translate all the segments contained in them into Chinese, fill them back into JSON, and return them to the user. You need to make the translated segments conform to Chinese expression habits, adjust the tone and style, and consider the cultural connotations and regional differences of certain words, that is, to create a translation that is both loyal to the spirit of the original work and in line with the culture and reader's aesthetic of the target language.
For example:
{"paragraphs_result": [{"words": ["I am cat."], "top": 1, "left": 1},{"words": ["You are mouse."], "top": 2, "left": 2}]}
Output:
{"paragraphs_result": [{"words": ["我是猫。"], "top": 1, "left": 1},{"words": ["你是老鼠。"], "top": 2, "left": 2}]}
You can only use JSON output. Do not include any explanations or comments."""

    user_prompt = text

    try:
        json.loads(user_prompt)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in user_prompt: {e}")
        return

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    # print(json.loads(response.choices[0].message.content))
    # main_window.output_text_ctrl.AppendText(response.choices[0].message.content)
    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    # deepseek_AI_sort("{\"paragraphs_result\": [{\"words\": [\"am\", \"I\", \"cat.\"], \"top\": 1, \"left\": 1},{\"words\": [\"Y0u\", \"are\", \"mouse.\"], \"top\": 2, \"left\": 2}]}")
    deepseek_AI_trans("{\"paragraphs_result\": [{\"I am cat.\"], \"top\": 1, \"left\": 1},{\"words\": [\"You are mouse.\"], \"top\": 2, \"left\": 2}]}")

