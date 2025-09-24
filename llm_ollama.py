import requests
import json
import argparse

def correct_text(text: str, model_name: str = "llama3.1") -> str:
    """
    使用AI模型对文本进行纠错和标点优化
    :param text: 输入文本
    :param model_name: 模型名称
    :return: 修正后的文本
    """
    # 定义 API 端点
    url = "http://localhost:11434/api/generate"
    
    # prompt = "判断「{}」和「{}」这两个词条是否是用户的换词需求。如果是换词需求，判断用户换词意图。\
    #     换词需求：用户在搜索引擎中搜索「{}」，但是由于搜索结果内容不满足用户需求，用户调整了搜索词，进行了二次搜索，搜索的是「{}」。\
    #     换词意图：\
    #         1.替换，用户希望同义词替换后进行搜索; \
    #         2.细化，用户希望搜索同一人物\\主题\\事件下更详细的信息; \
    #         3.泛化，用户希望搜索同一人物\\主题\\事件下更广泛的信息; \
    #         4.纠错，用户希望搜索纠正后的文本，纠错的query必须有文本相似度，或者语义相似; \
    #         5.其他，用户希望搜索不同人物\\主题\\事件的信息; \
    #     请首先判断用户是不是围绕一个主题进行了换词搜索，如果进行了换词搜索，给出用户换词意图，以及换词的原因。\
    #     返回结果为一个json,数据格式如下{{query1: '词条1', query2: '词条2', is_switch: 是否换词,0表示不是,1表示是, explain: 解释, intent: 换词意图: 替换, 细化, 泛化, 纠错, 其他}}"
    # prompt = prompt.format(query1, query2, query1, query1, query2)
    # 构建提示词
    prompt = "你是一个专业的文本校对助手。请严格按照以下要求处理文本：\
            1. 任务要求：\
                - 修正错别字和语法错误\
                - 添加或修正标点符号\
                - 保持原文的意思不变\
            2. 输入文本： {text}\
            3. 输出格式要求：\
                你必须严格按照以下格式输出，不要添加任何其他内容：\
            【原文】\
                {text}\
            【修改后】\
                <在这里给出修改后的文本>\
            【修改说明】\
                <说明主要修改的内容>\
            4. 注意：\
                - 必须严格按照上述格式输出\
                - 原文部分必须完全复制输入文本\
                - 修改后部分给出修改后的文本\
                - 修改说明部分列出所有修改的内容\
                - 不要添加任何额外的解释或说明\
            ".format(text=text)

    # 定义请求数据
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": True
    }

    try:
        # 发送 POST 请求
        response = requests.post(url, json=data, stream=True)
        response.raise_for_status()
        
        # 处理响应
        print("正在处理...\n")
        for line in response.text.splitlines():
            if line:
                result = json.loads(line)
                print(result.get("response", ""), end="", flush=True)
        print("\n")
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="文本纠错和标点优化工具")
    parser.add_argument("--text", type=str, help="需要处理的文本")
    parser.add_argument("--model", default="llama3.1", help="使用的模型名称")
    parser.add_argument("--file", type=str, help="输入文本文件路径")
    
    args = parser.parse_args()
    
    # 获取输入文本
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"读取文件失败: {str(e)}")
            return
    elif args.text:
        text = args.text
    else:
        text = input("请输入需要处理的文本：\n")
    
    # 处理文本
    correct_text(text, args.model)

if __name__ == "__main__":
    main()