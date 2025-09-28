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
import sys
import pyperclip
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                            QFrame, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QPalette, QColor, QPainter, QPainterPath

from abstract import get_variable_name, generate_title

def process_markdown_content(content):
    """处理markdown内容，删除复制行并处理代码块语言"""
    try:
        # 按行分割内容
        lines = content.split('\n')
        processed_lines = []
        skip_next = False
        next_code_language = None
        in_code_block = False
        
        for i, line in enumerate(lines):
            try:
                if i == 0:
                    if line.strip() == "":
                        continue
                    elif line.strip().startswith("#") and not line.strip().startswith("##"):
                        print("标题正常...")
                        processed_lines.append(line)
                        continue
                    else:
                        print("标题缺失，生成标题...")
                        title = generate_title(line)
                        print("生成标题:", title)
                        title_md = f"# {title}\n"
                        if title_md:
                            processed_lines.append(title_md)
                            processed_lines.append(line)
                            continue

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
            except Exception as e:
                print(f"处理第 {i+1} 行时出错: {str(e)}")
                continue
        
        return '\n'.join(processed_lines)
    except Exception as e:
        print(f"处理markdown内容时出错: {str(e)}")
        return content  # 如果处理失败，返回原始内容

def save_markdown_content(content, filename=None):
    """保存markdown内容到文件"""
    try:
        if not content or not isinstance(content, str):
            print("无效的内容")
            return None
            
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
    max_retries = 10
    retry_count = 0
    
    def check_msg_list_eq(msg_list):
        try:
            #判断msg_list是否相等
            for i in range(msg_len):
                if msg_list[i] != msg_list[0]:
                    return False
            return True
        except Exception as e:
            print(f"检查消息列表时出错: {str(e)}")
            return False
        
    while retry_count < max_retries:
        try:
            # 等待AI开始回答（等待消息内容出现）
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ds-markdown.ds-markdown--block")))
            msg_len  = 5
            msg_list = [""] * msg_len
            idx = 0
            
            while True:
                try:
                    messages = driver.find_elements(By.CSS_SELECTOR, "div.ds-markdown.ds-markdown--block")
                    if messages:
                        # 获取最后一个消息的HTML内容
                        html_content = messages[-1].get_attribute('innerHTML')
                        if not html_content:
                            print("获取到的HTML内容为空")
                            time.sleep(2)
                            continue
                            
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
                        
                        if not markdown_content:
                            print("转换后的markdown内容为空")
                            time.sleep(2)
                            continue
                            
                        msg_list[idx] = markdown_content
                        idx = (idx + 1) % msg_len
                        if check_msg_list_eq(msg_list):
                            print(f"AI回答: \n{markdown_content}")
                            # 保存到文件
                            save_markdown_content(markdown_content, filename)
                            return
                except Exception as e:
                    print(f"获取消息时出错: {str(e)}")
                    time.sleep(2)
                    continue
                    
                time.sleep(2)
                
        except TimeoutException:
            retry_count += 1
            print(f"\n等待AI回答超时 (尝试 {retry_count}/{max_retries})")
            if retry_count < max_retries:
                print("正在重试... sleep 5s")
                time.sleep(5)  # 等待5秒后重试
                continue
            else:
                print("\n等待AI回答超时，已达到最大重试次数")
                driver.save_screenshot("response_timeout.png")
                raise
        except Exception as e:
            print(f"\n获取AI回答时出错: {str(e)}")
            driver.save_screenshot("response_error.png")
            raise
            
    raise TimeoutException("等待AI回答超时，已达到最大重试次数")

def send_message(driver, wait, message):
    """发送消息并等待AI回答"""
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
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
            return
            
        except Exception as e:
            retry_count += 1
            print(f"发送消息时出错 (尝试 {retry_count}/{max_retries}): {str(e)}")
            if retry_count < max_retries:
                print("正在重试... sleep 5s")
                time.sleep(5)  # 等待5秒后重试
                continue
            else:
                print("发送消息失败，已达到最大重试次数")
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
            time.sleep(1)
            email_input.clear()
            email_input.send_keys(DEEPSEEK_EMAIL)
            print("已输入邮箱")
            
            password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
            time.sleep(2)
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

class ChatThread(QThread):
    """处理聊天相关操作的线程"""
    message_sent = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, driver, wait, message=None, action=None):
        super().__init__()
        self.driver = driver
        self.wait = wait
        self.message = message
        self.action = action
    
    def run(self):
        try:
            if self.action == "send":
                send_message(self.driver, self.wait, self.message)
                self.status_changed.emit("就绪")
            elif self.action == "new_chat":
                new_dialog_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.c7dddcde")))
                self.wait.until(EC.visibility_of(new_dialog_button))
                self.driver.execute_script("arguments[0].click();", new_dialog_button)
                time.sleep(3)
                self.status_changed.emit("就绪")
        except Exception as e:
            self.error_occurred.emit(str(e))

class BrowserThread(QThread):
    """处理浏览器操作的线程"""
    status_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    browser_ready = pyqtSignal(object, object)  # 发送driver和wait对象
    
    def run(self):
        try:
            self.status_changed.emit("正在启动浏览器...")
            driver = setup_driver()
            wait = WebDriverWait(driver, 20)
            
            print("正在访问 DeepSeek 登录页面...")
            driver.get("https://chat.deepseek.com/sign_in")
            
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "title")))
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
            
            print("等待密码登录按钮出现...")
            password_login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), '密码登录')]")))
            wait.until(EC.visibility_of(password_login_button))
            driver.execute_script("arguments[0].click();", password_login_button)
            print("已点击密码登录按钮")
            
            print("等待登录表单加载...")
            email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
            email_input.clear()
            email_input.send_keys(DEEPSEEK_EMAIL)
            print("已输入邮箱")
            
            password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
            password_input.clear()
            password_input.send_keys(DEEPSEEK_PASSWORD)
            print("已输入密码")
            
            login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ds-button.ds-button--primary.ds-button--filled.ds-button--rect.ds-button--block.ds-button--l.ds-sign-up-form__register-button")))
            wait.until(EC.visibility_of(login_button))
            driver.execute_script("arguments[0].click();", login_button)
            print("已点击登录按钮")
            
            print("等待进入聊天界面...")
            time.sleep(3)
            print("已进入聊天界面")
            
            self.status_changed.emit("就绪")
            self.browser_ready.emit(driver, wait)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

class ClipboardMonitor(QThread):
    """监控剪贴板的线程"""
    clipboard_changed = pyqtSignal(str)  # 添加信号
    
    def __init__(self):
        super().__init__()
        self.last_text = ""
        self.running = True
    
    def run(self):
        while self.running:
            try:
                current_text = pyperclip.paste()
                if current_text != self.last_text:
                    self.last_text = current_text
                    self.clipboard_changed.emit(current_text)  # 发送信号
                time.sleep(1)  # 每秒检查一次
            except Exception as e:
                print(f"监控剪贴板时出错: {str(e)}")
                time.sleep(1)
    
    def stop(self):
        """停止监控"""
        self.running = False

class GlassFrame(QFrame):
    """毛玻璃效果的框架"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建圆角矩形路径
        path = QPainterPath()
        rect = self.rect()
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 10, 10)
        
        # 设置半透明背景
        painter.fillPath(path, QColor(255, 255, 255, 180))
        
        # 绘制边框
        painter.setPen(QColor(255, 255, 255, 100))
        painter.drawPath(path)

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.wait = None
        self.browser_thread = None
        self.chat_threads = []
        self.clipboard_monitor = None
        self.init_ui()
        self.start_browser()
        self.start_clipboard_monitor()
        
        # 设置窗口透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 重定向标准输出到GUI
        sys.stdout = self
        
        # 设置事件循环策略
        if platform.system() == 'Darwin':  # macOS
            os.environ['QT_MAC_WANTS_WINDOW'] = '1'
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('DeepSeek Chat')
        self.setGeometry(0, 0, 600, 450)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建聊天历史区域
        chat_frame = GlassFrame()
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(10, 10, 10, 10)
        
        self.chat_text = QTextEdit()
        self.chat_text.setReadOnly(True)
        self.chat_text.setFont(QFont('Consolas', 10))
        self.chat_text.setMinimumHeight(200)  # 减小最小高度
        self.chat_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 100);
                border: 1px solid rgba(52, 152, 219, 100);
                border-radius: 8px;
                padding: 8px;
                color: #2c3e50;
            }
            QTextEdit:focus {
                border: 1px solid rgba(52, 152, 219, 200);
                background-color: rgba(255, 255, 255, 180);
            }
        """)
        chat_layout.addWidget(self.chat_text)
        
        # 创建输入区域
        input_frame = GlassFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        self.input_text = QTextEdit()
        self.input_text.setMinimumHeight(80)  # 减小最小高度
        self.input_text.setMaximumHeight(120)  # 减小最大高度
        self.input_text.setFont(QFont('Consolas', 11))
        self.input_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 150);
                border: 1px solid rgba(52, 152, 219, 100);
                border-radius: 8px;
                padding: 8px;
                color: #2c3e50;
            }
            QTextEdit:focus {
                border: 1px solid rgba(52, 152, 219, 200);
                background-color: rgba(255, 255, 255, 180);
            }
        """)
        input_layout.addWidget(self.input_text)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: rgba(52, 152, 219, 200);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(52, 152, 219, 255);
            }
            QPushButton:pressed {
                background-color: rgba(41, 128, 185, 255);
            }
            QPushButton:disabled {
                background-color: rgba(52, 152, 219, 100);
            }
        """
        
        self.send_button = QPushButton('发送')
        self.new_chat_button = QPushButton('新对话')
        
        for btn in [self.send_button, self.new_chat_button]:
            btn.setStyleSheet(button_style)
            btn.setMinimumWidth(80)  # 减小按钮最小宽度
            button_layout.addWidget(btn)
        
        # 创建状态栏
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: rgba(255, 255, 255, 100);
                color: #2c3e50;
            }
        """)
        self.status_bar.showMessage('就绪')
        
        # 添加所有组件到主布局
        layout.addWidget(chat_frame, stretch=1)  # 添加 stretch 参数
        layout.addWidget(input_frame)
        layout.addLayout(button_layout)
        
        # 连接信号
        self.send_button.clicked.connect(self.send_message)
        self.new_chat_button.clicked.connect(self.new_chat)
        self.input_text.textChanged.connect(self.check_input)
        
        # 设置快捷键
        self.input_text.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """处理事件过滤器"""
        if obj == self.input_text and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return:
                if not event.modifiers() & Qt.ShiftModifier:
                    self.send_message()
                    return True
        return super().eventFilter(obj, event)
    
    def check_input(self):
        """检查输入内容"""
        text = self.input_text.toPlainText().strip()
        self.send_button.setEnabled(bool(text))
    
    def start_browser(self):
        """启动浏览器"""
        self.browser_thread = BrowserThread()
        self.browser_thread.status_changed.connect(self.status_bar.showMessage)
        self.browser_thread.error_occurred.connect(self.handle_error)
        self.browser_thread.browser_ready.connect(self.browser_ready)
        self.browser_thread.start()
    
    def browser_ready(self, driver, wait):
        """浏览器准备就绪"""
        self.driver = driver
        self.wait = wait
        self.new_chat_button.setEnabled(True)
    
    def send_message(self):
        """发送消息"""
        message = self.input_text.toPlainText().strip()
        if message and self.driver and self.wait:
            self.input_text.clear()
            self.status_bar.showMessage("正在发送消息...")
            
            chat_thread = ChatThread(self.driver, self.wait, message, "send")
            chat_thread.status_changed.connect(self.status_bar.showMessage)
            chat_thread.error_occurred.connect(self.handle_error)
            chat_thread.finished.connect(lambda: self.cleanup_thread(chat_thread))
            self.chat_threads.append(chat_thread)
            chat_thread.start()
    
    def new_chat(self):
        """开始新对话"""
        if self.driver and self.wait:
            self.status_bar.showMessage("正在开始新对话...")
            
            chat_thread = ChatThread(self.driver, self.wait, action="new_chat")
            chat_thread.status_changed.connect(self.status_bar.showMessage)
            chat_thread.error_occurred.connect(self.handle_error)
            chat_thread.finished.connect(lambda: self.cleanup_thread(chat_thread))
            self.chat_threads.append(chat_thread)
            chat_thread.start()
    
    def cleanup_thread(self, thread):
        """清理已完成的线程"""
        if thread in self.chat_threads:
            self.chat_threads.remove(thread)
            thread.deleteLater()
    
    def handle_error(self, error_message):
        """处理错误"""
        self.status_bar.showMessage(f"错误: {error_message}")
        self.chat_text.append(f"\n错误: {error_message}\n")
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 停止剪贴板监控
        if self.clipboard_monitor:
            self.clipboard_monitor.stop()
            self.clipboard_monitor.wait()
        
        # 恢复标准输出
        sys.stdout = sys.__stdout__
        
        # 等待所有聊天线程完成
        for thread in self.chat_threads:
            thread.wait()
        
        # 等待浏览器线程完成
        if self.browser_thread:
            self.browser_thread.wait()
        
        # 关闭浏览器
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"关闭浏览器时出错: {str(e)}")
        
        event.accept()

    def start_clipboard_monitor(self):
        """启动剪贴板监控"""
        self.clipboard_monitor = ClipboardMonitor()
        self.clipboard_monitor.clipboard_changed.connect(self.update_input_text)  # 连接信号
        self.clipboard_monitor.start()
    
    def update_input_text(self, text):
        """更新输入框内容"""
        if text.strip():  # 只处理非空文本
            self.input_text.setText(text)
    
    def write(self, text):
        """重定向输出到GUI"""
        if text.strip():  # 只处理非空文本
            self.chat_text.append(text)
            # 滚动到底部
            self.chat_text.verticalScrollBar().setValue(
                self.chat_text.verticalScrollBar().maximum()
            )
            # 确保GUI更新
            QApplication.processEvents()
    
    def flush(self):
        """实现flush方法"""
        pass

def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 