from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

client = OpenAI(
    base_url="https://api.deepseek.com/",
    api_key=os.getenv("DEEPSEEK_API_KEY")
)

def get_variable_name(topic):
    """获取指定主题的变量名建议
    
    Args:
        topic (str): 需要生成变量名的主题
        
    Returns:
        str: 生成的变量名
    """
    completion = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
            {
                "role": "system",
                "content": "你是一位编程专家，擅长规范的编码，总是能给变量起简洁的变量名，符合小写加下划线的命名惯例，变量名长度适中"
            },
            {
                "role": "user",
                "content": f'请帮我生成"{topic}"这个词条的一个变量名，直接输出你最推荐的，不需要有别的输出'
            }
        ]
    )
    
    return completion.choices[0].message.content

def generate_title(content):
    """根据文本内容生成标题
    
    Args:
        content (str): 需要生成标题的文本内容
        
    Returns:
        str: 生成的标题
    """
    completion = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
            {
                "role": "system",
                "content": "你是一位专业的编辑，擅长为文章生成简洁、准确、吸引人的标题。标题应该：\n1. 长度适中（5-15个字）\n2. 准确反映文章内容\n3. 使用中文\n4. 不使用标点符号\n5. 不使用特殊字符"
            },
            {
                "role": "user",
                "content": f'请根据以下内容生成一个标题，直接输出标题，不需要有别的输出：\n\n{content}'
            }
        ]
    )
    
    return completion.choices[0].message.content.strip()

def test_generate_title():
    """测试生成标题功能"""
    # 测试用例1：技术文档
    content1 = """
    PyQt5是一个用于创建图形用户界面的Python库。它提供了丰富的GUI组件，如按钮、文本框、标签等。
    使用PyQt5可以快速开发跨平台的桌面应用程序。PyQt5支持信号槽机制，使得界面交互更加灵活。
    """
    title1 = generate_title(content1)
    print(f"测试用例1 - 技术文档：\n内容：{content1}\n生成的标题：{title1}\n")
    
    # 测试用例2：产品描述
    content2 = """
    这是一款智能家居控制系统，支持语音控制、远程操控、定时任务等功能。
    系统可以控制灯光、空调、电视等家电设备，提供便捷的生活体验。
    """
    title2 = generate_title(content2)
    print(f"测试用例2 - 产品描述：\n内容：{content2}\n生成的标题：{title2}\n")
    
    # 测试用例3：教程内容
    content3 = """
    本教程介绍如何使用Python进行数据分析，包括数据清洗、数据可视化、统计分析等内容。
    通过实例讲解pandas、numpy、matplotlib等库的使用方法。
    """
    title3 = generate_title(content3)
    print(f"测试用例3 - 教程内容：\n内容：{content3}\n生成的标题：{title3}\n")

def main():
    # 测试函数
    topic = "中国农业情况"
    variable_name = get_variable_name(topic)
    print(f"主题: {topic}")
    print(f"生成的变量名: {variable_name}\n")
    
    # 测试标题生成
    print("开始测试标题生成功能...")
    test_generate_title()

if __name__ == "__main__":
    main()
