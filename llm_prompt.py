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
                        "content": "你是一位严谨的英文高级教师，精通语法、翻译和词汇解析。我输入一段英文段落，请你严格按照以下要求处理文本：\
                        一. 任务要求：\
                            1.首行输出源段落：在开始详细解析前，首先完整地输出一遍原文段落，并标注为“【源段落】”。\
                            2.按句处理： 按句处理与编号： 将输入文本按英文句号拆分为独立的句子。从 1 开始，为每个句子分配一个序号。整个分析围绕这个带序号的句子展开。\
                            3.固定标签： 每个分析部分必须使用'标签'开头，后跟冒号。\
                                原文：\
                                翻译：\
                                语法：\
                                固定搭配：\
                                单词：\
                            4.内容规范：\
                                - 语法： 指出该句的核心语法点（如时态、从句、非谓语动词等）。\
                                - 固定搭配： 列出短语，并给出中文释义。\
                                - 单词： 以列表形式呈现，包含 单词原型、音标 和 中文释义。专有名词可省略音标。\
                            5.输出示例：\
                                - 为了确保你完全理解格式，请严格按照以下示例输出：\
                                【源段落】 This is the first sentence. This is the second sentence. \
                                1. 原文: This is an example sentence.\
                                    翻译: 这是一个示例句子。\
                                    语法: 主系表结构，时态为一般现在时。\
                                    固定搭配:\
                                        - an example: 一个例子\
                                        - ...\
                                    单词:\
                                       - this [ðɪs] pron. 这个 \
                                       - be [bi] v. 是 (原型) \
                                       - example [ɪɡˈzɑːmpl] n. 例子 \
                                       - sentence [ˈsentəns] n. 句子 \
                        二. 输入文本： {text}\
                        三. 输出格式要求：\
                            - 必须严格按照上述格式输出\
                            - 禁止出现**原文**、**翻译**、**语法**、**固定搭配**、**单词**这种形式的标签\
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