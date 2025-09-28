from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import platform
from config import DEEPSEEK_EMAIL, DEEPSEEK_PASSWORD
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from markdownify import markdownify as md
import os
from datetime import datetime

from abstract import get_variable_name

def process_markdown_content(content):
    """处理markdown内容，删除复制行并处理代码块语言"""
    # 按行分割内容
    lines = content.split('\n')
    processed_lines = []
    skip_next = False
    next_code_language = None
    in_code_block = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        # 跳过"复制"行
        if line.strip() == "复制":
            skip_next = True
            continue

         # 检查是否是语言标识行
        if not in_code_block and line.strip() in ["markdown", "python", "javascript", "java", \
            "cpp", "c", "csharp", "go", "rust", "swift", "kotlin", "scala", "ruby", "php", "r", \
            "matlab", "sql", "html", "css", "shell", "bash", "powershell", "typescript", "json", 
            "yaml", "xml", "ini", "toml", "diff", "modelfile", "yaml.jinja2", "yaml.j2", "dockerfile"]:
            next_code_language = line.strip()
            skip_next = True
            continue           

        # 处理代码块语言
        if line.strip().startswith('```') :
            in_code_block = not in_code_block
            # 如果有预定义的语言标识，使用它
            if next_code_language and in_code_block:
                processed_lines.append(f"```{next_code_language}")
                next_code_language = None
                continue
                
        processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def save_markdown_content(content, filename=None):
    """保存markdown内容到文件"""
    try:
        # 处理markdown内容
        processed_content = process_markdown_content(content)
        
        # 如果没有指定文件名，使用时间戳创建文件名
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"ai_response_{timestamp}.md"
        
        # 确保输出目录存在
        output_dir = "ai_responses"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 完整的文件路径
        filepath = os.path.join(output_dir, filename)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(processed_content)
            
        print(f"\n回答已保存到文件: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"保存markdown文件时出错: {str(e)}")
        return None

def setup_driver():
    """设置并返回Chrome浏览器驱动"""
    try:
        # 设置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')  # 最大化窗口
        chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
        chrome_options.add_argument('--no-sandbox')  # 禁用沙箱模式
        chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用/dev/shm使用
        chrome_options.add_argument('--disable-extensions')  # 禁用扩展
        chrome_options.add_argument('--disable-notifications')  # 禁用通知
        chrome_options.add_argument('--disable-popup-blocking')  # 禁用弹窗拦截
        chrome_options.add_argument('--disable-infobars')  # 禁用信息栏
        chrome_options.add_argument('--disable-web-security')  # 禁用网页安全策略
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')  # 禁用站点隔离
        chrome_options.add_argument('--disable-site-isolation-trials')  # 禁用站点隔离测试
        chrome_options.add_argument('--ignore-certificate-errors')  # 忽略证书错误
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 禁用自动化控制检测
        
        # 检测系统架构
        system = platform.system()
        machine = platform.machine()
        
        if system == 'Darwin' and machine == 'arm64':
            # Mac ARM64架构
            chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            service = Service()
        else:
            # 其他系统
            service = Service(ChromeDriverManager().install())
        
        # 创建Chrome驱动
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"设置Chrome驱动时出错: {str(e)}")
        raise

def wait_for_ai_response(driver, wait, filename):
    """等待AI回答完成"""
    print("\n等待AI回答...")
    def check_msg_list_eq(msg_list):
        #判断msg_list是否相等
        for i in range(msg_len):
            if msg_list[i] != msg_list[0]:
                return False
        return True
        
    try:
        # 等待AI开始回答（等待消息内容出现）
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ds-markdown.ds-markdown--block")))
        msg_len  = 5
        msg_list = [""] * msg_len
        idx = 0
        
        while True:
            messages = driver.find_elements(By.CSS_SELECTOR, "div.ds-markdown.ds-markdown--block")
            if messages:
                # 获取最后一个消息的HTML内容
                html_content = messages[-1].get_attribute('innerHTML')
                # 转换为markdown格式
                markdown_content = md(html_content, 
                    heading_style="ATX",  # 使用 # 风格的标题
                    bullets="-",          # 使用 - 作为列表符号
                    code_language="python",  # 默认代码块语言
                    strip=['script', 'style'],  # 移除脚本和样式标签
                    wrap_code=True,       # 保持代码块格式
                    wrap_list=True,       # 保持列表格式
                    wrap_tables=True,     # 保持表格格式
                    newline_style="LF"    # 使用Unix风格的换行
                )
                msg_list[idx] = markdown_content
                idx = (idx + 1) % msg_len
                if check_msg_list_eq(msg_list):
                    print(f"AI回答: \n{markdown_content}")
                    # 保存到文件
                    save_markdown_content(markdown_content, filename)
                    break
            time.sleep(2)
            
    except TimeoutException:
        print("\n等待AI回答超时")
        driver.save_screenshot("response_timeout.png")
        raise
    except Exception as e:
        print(f"\n获取AI回答时出错: {str(e)}")
        driver.save_screenshot("response_error.png")
        raise

def send_message(driver, wait, message):
    """发送消息并等待AI回答"""
    try:
        # 等待并定位对话框输入框
        chat_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea#chat-input")))
        print("找到对话框输入框")
        
        # 输入消息
        chat_input.clear()
        chat_input.send_keys(message)
        print(f"已输入消息: {message}")

        filename = get_variable_name(message)
        print(f"生成的变量名: {filename}")
        filename = f"{filename}.md"
        
        # 等待一下确保输入完成
        time.sleep(1)
        
        # 发送消息（按回车键）
        chat_input.send_keys(Keys.RETURN)
        print("已发送消息")
        
        # 等待AI回答
        wait_for_ai_response(driver, wait, filename)
        
    except Exception as e:
        print(f"发送消息时出错: {str(e)}")
        driver.save_screenshot("send_message_error.png")
        raise

def visit_deepseek():
    """访问DeepSeek官网并点击相关按钮"""
    driver = None
    try:
        # 设置并获取驱动
        driver = setup_driver()
        wait = WebDriverWait(driver, 20)  # 设置等待时间为20秒
        
        # 直接访问登录页面
        print("正在访问 DeepSeek 登录页面...")
        driver.get("https://chat.deepseek.com/sign_in")
        
        # 等待页面加载
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "title")))
        
        # 等待页面完全加载
        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        
        # 等待并点击密码登录按钮
        print("等待密码登录按钮出现...")
        try:
            password_login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), '密码登录')]")))
            wait.until(EC.visibility_of(password_login_button))
            driver.execute_script("arguments[0].click();", password_login_button)
            print("已点击密码登录按钮")
        except Exception as e:
            print(f"点击密码登录按钮时出错: {str(e)}")
            driver.save_screenshot("login_button_error.png")
            raise
        
        # 等待登录表单加载
        print("等待登录表单加载...")
        try:
            # 输入邮箱和密码
            email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
            email_input.clear()
            email_input.send_keys(DEEPSEEK_EMAIL)
            print("已输入邮箱")
            
            password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
            password_input.clear()
            password_input.send_keys(DEEPSEEK_PASSWORD)
            print("已输入密码")
            
            # 点击同意条款复选框
            # checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ds-checkbox-wrapper--block div.ds-checkbox")))
            # wait.until(EC.visibility_of(checkbox))
            # driver.execute_script("arguments[0].click();", checkbox)
            # print("已点击同意条款复选框")
            # time.sleep(1)
            
            # 点击登录按钮
            login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ds-button.ds-button--primary.ds-button--filled.ds-button--rect.ds-button--block.ds-button--l.ds-sign-up-form__register-button")))
            wait.until(EC.visibility_of(login_button))
            driver.execute_script("arguments[0].click();", login_button)
            print("已点击登录按钮")
            
            # 等待登录完成并进入聊天界面
            print("等待进入聊天界面...")
            time.sleep(3)
            print("已进入聊天界面")

            # print("点击深度思考...")
            # deepsearch_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ds-button.ds-button--primary.ds-button--filled.ds-button--rect.ds-button--m._3172d9f")))
            # wait.until(EC.visibility_of(deepsearch_button))
            # driver.execute_script("arguments[0].click();", deepsearch_button)           
            # time.sleep(3)

            # print("点击联网搜索...")
            # search_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ds-button.ds-button--primary.ds-button--filled.ds-button--rect.ds-button--m._3172d9f")))
            # wait.until(EC.visibility_of(search_button))
            # driver.execute_script("arguments[1].click();", search_button)           
            # time.sleep(3)

            # 发送测试消息
            while True:
                print("等待用户输入:")
                test_message = input()
                send_message(driver, wait, test_message)

                print("点击新对话...")
                new_dialog_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.c7dddcde")))
                wait.until(EC.visibility_of(new_dialog_button))
                driver.execute_script("arguments[0].click();", new_dialog_button)           
                time.sleep(3)
            
            # 保持浏览器打开状态
            while True:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    print("\n用户中断程序")
                    break
                
        except Exception as e:
            print(f"登录过程中出错: {str(e)}")
            driver.save_screenshot("login_process_error.png")
            raise
        
    except Exception as e:
        print(f"访问网站时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    finally:
        # 关闭浏览器
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"关闭浏览器时出错: {str(e)}")

def main():
    print("开始访问 DeepSeek 官网...")
    try:
        visit_deepseek()
        print("访问完成")
    except Exception as e:
        print(f"程序执行出错: {str(e)}")

if __name__ == "__main__":
    main() 