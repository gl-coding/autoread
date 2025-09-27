from openai import OpenAI
from dotenv import load_dotenv
import os,sys,time,multiprocessing

# 先加载环境变量
load_dotenv()

client = OpenAI(
    base_url="https://api.deepseek.com/",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

class Prompt:
    @staticmethod
    def correct_article(topic):
        completion = client.chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL"),
            messages=[
                {
                        "role": "system",
                        "content": "你是一个英文专业词汇书文本校对助手。输入文本是《傲慢与偏见》的英文原著识别结果，请严格按照以下要求处理文本：\
                            1. 任务要求：\
                                - 逐行修改原文内容\
                                - 修正错误单词，确保每个单词都是正确的\
                                - 修正错误标点符号，确保标点符号正确\
                                - 修正错误语法，确保语法正确\
                                - 删除与上下文没有联系的识别结果\
                            2. 输入文本： {text}\
                            3. 输出格式要求：\
                                - 原文内容\
                                - ==============================\
                                - 修改后的内容\
                            4. 注意：\
                                - 必须严格按照上述格式输出\
                                - 原文部分必须完全复制输入文本\
                                - 不要添加任何额外的解释或说明，包括额外的[原文内容]、[修改后的内容]\
                    ".format(text=topic)
                },
                {
                        "role": "user",
                        "content": "请帮我校对“" + topic + "”这篇文章的识别结果"
                }
            ]
        )

        res = completion.choices[0].message.content
        return res

    @staticmethod
    def correct_words_book(topic):
        completion = client.chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL"),
            messages=[
                {
                        "role": "system",
                        "content": "你是一个英文专业词汇书文本校对助手。输入文本是一个英文专业词汇书的识别结果，请严格按照以下要求处理文本：\
                            1. 任务要求：\
                                - 逐行修改原文内容\
                                - 修正错误单词，确保每个单词都是正确的\
                                - 添加或修正标点符号，单词和词性都正确\
                                - 针对单词的音标修正音标，确保音标正确\
                                - 去掉一些内容，如：”随时阅读“、”review“、”加入书架“等\
                            2. 输入文本： {text}\
                            3. 输出格式要求：\
                                - 原文内容\
                                - ==============================\
                                - 修改后的内容\
                            4. 注意：\
                                - 必须严格按照上述格式输出\
                                - 原文部分必须完全复制输入文本\
                                - 不要添加任何额外的解释或说明，包括额外的[原文内容]、[修改后的内容]\
                    ".format(text=topic)
                },
                {
                        "role": "user",
                        "content": "请帮我校对“" + topic + "”这篇文章的识别结果"
                }
            ]
        )

        res = completion.choices[0].message.content
        return res

    @staticmethod
    def trans_words(topic):
        completion = client.chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL"),
            messages=[
                {
                        "role": "system",
                        "content": "你是一位英文翻译助手，擅长将英文单词、短语或句子翻译成中文，如果有多个意思，请用“，”分割。\
                        1. 输入文本： {text}\
                        2. 输出格式要求：\
                            - 只输出翻译后的文本，不要添加任何额外的解释或说明/no_think\
                        ".format(text=topic)
                },
                {
                        "role": "user",
                        "content": "请帮我翻译“" + topic + "”"
                }
            ]
        )

        res = completion.choices[0].message.content
        return res
