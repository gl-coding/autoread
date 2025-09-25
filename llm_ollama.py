import requests
import json, os, time
import argparse

# 定义 API 端点
url = "http://localhost:11434/api/generate"

class Prompt:
    @staticmethod
    def correct_text(text: str) -> str:
        # 构建提示词
        prompt = "你是一个英文专业词汇书文本校对助手。输入文本是一个英文专业词汇书的识别结果，请严格按照以下要求处理文本：\
                1. 任务要求：\
                    - 逐行修改原文内容\
                    - 修正错误单词，确保每个单词都是正确的\
                    - 添加或修正标点符号，单词和词性都正确\
                    - 针对单词的音标修正音标，确保音标正确\
                2.举例：\
                    原文：【同义】respondv 反应\
                    修改后：【同义】respond v. 反应\
                3. 输入文本： {text}\
                4. 输出格式要求：\
                    你必须严格按照以下格式输出，不要添加任何其他内容：\
                    【原文】===========\
                        {text}\
                    【修改后】===========\
                        <在这里给出修改后的文本>\
                5. 注意：\
                    - 必须严格按照上述格式输出\
                    - 原文部分必须完全复制输入文本\
                    - 不要添加任何额外的解释或说明\
                ".format(text=text)
        return prompt

prompt = Prompt()

def request_ollama(prompt: str, model_name: str = "llama3.1", stream: bool = True, url: str = "http://localhost:11434/api/generate") -> str:
    start_time = time.time()
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": stream
    }
    response = requests.post(url, json=data, stream=stream)
    res_text = ""
    for line in response.text.splitlines():
        if line:
            result = json.loads(line)
            res_text += result.get("response", "")
    end_time = time.time()
    print(f"耗时: {end_time - start_time}秒")
    return res_text

def main():
    parser = argparse.ArgumentParser(description="文本纠错和标点优化工具")
    parser.add_argument("--text", type=str, help="需要处理的文本")
    parser.add_argument("--model", default="llama3.1", help="使用的模型名称")
    parser.add_argument("--prompt", default="", help="使用的提示词")
    
    args = parser.parse_args()
    
    if os.path.exists(args.text):
        with open(args.text, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = args.text
    
    # 处理文本
    if args.prompt:
        prompt_func = args.prompt
        #根据prompt_func执行相应的函数
        prompt_text = getattr(prompt, prompt_func)(text)
        response = request_ollama(prompt_text, args.model, True, url)
        print(response)

if __name__ == "__main__":
    main()