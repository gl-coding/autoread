from openai import OpenAI
from dotenv import load_dotenv
import os,sys,time,multiprocessing,time

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

    @staticmethod
    def trans_segment(topic):
        completion = client.chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL"),
            messages=[
                {
                        "role": "system",
                        "content": "你是一位英文高级教师，擅长将英文段落、句子、短语、单词翻译成中文，并能给出很好的解释，你也精通语法。我输入一段英文段落，请你严格按照以下要求处理文本：\
                        1. 任务要求：\
                            1. 每一个句话都给出翻译，标注“翻译”，原文标注原文\
                            2. 给出每一句话中涉及的语法知识，标注“语法”\
                            2. 给出每一句话中所有出现的短语、固定搭配的解释，标注“固定搭配”\
                            3. 给出每一句话中出现的所有单词的音标和释义，如果有原型给出单词原型，标注“单词”\
                            4. 务必确保所有的句子、短语、固定搭配、单词都有覆盖\
                        2. 输入文本： {text}\
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

if __name__ == "__main__":
    st = time.time()
    prompt = Prompt()
    res = prompt.trans_segment("INTRODUCTION How This Book Came to Be In the early summer of 2004, I got a phone call from Steve Jobs. He had been scattershot friendly to me over the years, with occasional bursts of intensity, especially when he was launching a new product that he wanted on the cover of Time or featured on CNN, places where I’d worked. But now that I was no longer at either of those places, I hadn’t heard from him much. We talked a bit about the Aspen Institute, which I had recently joined, and I invited him to speak at our summer campus in Colorado. He’d be happy to come, he said, but not to be onstage. He wanted instead to take a walk so that we could talk. That seemed a bit odd. I didn’t yet know that taking a long walk was his preferred way to have a serious conversation. It turned out that he wanted me to write a biography of him. I had recently published one on Benjamin Franklin and was writing one about Albert Einstein, and my initial reaction was to wonder, half jokingly, whether he saw himself as the natural successor in that sequence. Because I assumed that he was still in the middle of an oscillating career that had many more ups and downs left, I demurred. Not now, I said. Maybe in a decade or two, when you retire. I had known him since 1984, when he came to Manhattan to have lunch with Time’s editors and extol his new Macintosh. He was petulant even then, attacking a Time correspondent for having wounded him with a story that was too revealing. But talking to him afterward, I found myself rather captivated, as so many others have been over the years, by his engaging intensity. We stayed in touch, even after he was ousted from Apple. When he had something to pitch, such as a NeXT computer or Pixar movie, the beam of his charm would suddenly refocus on me, and he would take me to a sushi restaurant in Lower Manhattan to tell me that whatever he was touting was the best thing he had ever produced. I liked him. When he was restored to the throne at Apple, we put him on the cover of Time, and soon thereafter he began offering me his ideas for a series we were doing on the most influential people of the century. He had launched his “Think Different” campaign, featuring iconic photos of some of the same people we were considering, and he found the endeavor of assessing historic influence fascinating. After I had deflected his suggestion that I write a biography of him, I heard from him every now and then. At one point I emailed to ask if it was true, as my daughter had told me, that the Apple logo was an homage to Alan Turing, the British computer pioneer who broke the German wartime codes and then committed suicide by biting into a cyanide-laced apple. He replied that he wished he had thought of that, but hadn’t. That started an exchange about the early history of Apple, and I found myself gathering string on the subject, just in case I ever decided to do such a book. When my Einstein biography came out, he came to a book event in Palo Alto and pulled me aside to suggest, again, that he would make a good subject.")
    print(res)
    print(f"耗时: {time.time() - st}秒")