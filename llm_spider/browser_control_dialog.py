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
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                            QFrame, QSplitter, QListWidget, QListWidgetItem,
                            QInputDialog, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QPalette, QColor, QPainter, QPainterPath

from abstract import get_variable_name, generate_title

def process_markdown_content(content):
    """处理markdown内容，删除复制行并处理代码块语言"""
    try:
        if not content or not isinstance(content, str):
            return content
            
        # 按行分割内容
        lines = content.split('\n')
        processed_lines = []
        skip_next = False
        next_code_language = None
        in_code_block = False
        
        for i, line in enumerate(lines):
            try:
                if not line:
                    continue
                    
                if i == 0:
                    if line.strip() == "":
                        continue
                    elif line.strip().startswith("#") and not line.strip().startswith("##"):
                        processed_lines.append(line)
                        continue
                    else:
                        title = generate_title(line)
                        if title:
                            processed_lines.append(f"# {title}\n")
                            processed_lines.append(line)
                            continue

                if skip_next:
                    skip_next = False
                    continue
                    
                # 跳过"复制"行
                if line.strip() in ["复制", "下载", "---"]:
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
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
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
        return content

def save_markdown_content(content, filename=None):
    """保存markdown内容到文件"""
    try:
        if not content or not isinstance(content, str):
            print("无效的内容")
            return None
            
        # 处理markdown内容
        processed_content = process_markdown_content(content)
        if not processed_content:
            print("处理后的内容为空")
            return None
        
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
            if not msg_list or not isinstance(msg_list, list):
                return False
            if not msg_list[0]:
                return False
            return all(msg == msg_list[0] for msg in msg_list)
        except Exception as e:
            print(f"检查消息列表时出错: {str(e)}")
            return False
        
    while retry_count < max_retries:
        try:
            # 等待AI开始回答（等待消息内容出现）
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ds-markdown.ds-markdown--block")))
            msg_len = 5
            msg_list = [""] * msg_len
            idx = 0
            
            while True:
                try:
                    messages = driver.find_elements(By.CSS_SELECTOR, "div.ds-markdown.ds-markdown--block")
                    if not messages:
                        time.sleep(2)
                        continue
                        
                    # 获取最后一个消息的HTML内容
                    html_content = messages[-1].get_attribute('innerHTML')
                    if not html_content:
                        time.sleep(2)
                        continue
                        
                    # 转换为markdown格式
                    markdown_content = md(html_content, 
                        heading_style="ATX",
                        bullets="-",
                        code_language="python",
                        strip=['script', 'style'],
                        wrap_code=True,
                        wrap_list=True,
                        wrap_tables=True,
                        newline_style="LF"
                    )
                    
                    if not markdown_content:
                        time.sleep(2)
                        continue
                        
                    msg_list[idx] = markdown_content
                    idx = (idx + 1) % msg_len
                    
                    if check_msg_list_eq(msg_list):
                        print(f"AI回答: \n{markdown_content}")
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
                time.sleep(5)
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
            chat_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea._27c9245.ds-scroll-area.d96f2d2a")))
            print("机器人:找到对话框输入框")
            
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
            print("已进入聊天界面???")

            print("点击深度思考...")
            deepsearch_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ds-button.ds-button--primary.ds-button--filled.ds-button--rect.ds-button--m._3172d9f")))
            wait.until(EC.visibility_of(deepsearch_button))
            driver.execute_script("arguments[0].click();", deepsearch_button)           
            time.sleep(3)

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
            print("已进入聊天界面.....")
            
            self.status_changed.emit("就绪")
            self.browser_ready.emit(driver, wait)
            
        except Exception as e:
            self.error_occurred.emit(str(e))

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
        self.questions = []
        self.current_question_index = 0
        self.auto_mode = False
        self.auto_timer = None
        self.is_floating = False
        self.check_button_timer = QTimer()  # 添加定时器用于检查按钮
        self.check_button_timer.timeout.connect(self.check_and_click_button)
        self.init_ui()
        self.start_browser()
        
        # 设置窗口透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 重定向标准输出到GUI
        sys.stdout = self
        
        # 设置事件循环策略
        if platform.system() == 'Darwin':  # macOS
            os.environ['QT_MAC_WANTS_WINDOW'] = '1'
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('DeepSeek 笔记助手')
        self.setGeometry(0, 0, 700, 450)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        
        # 创建左侧问题列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(10)
        
        # 问题列表标题
        questions_label = QLabel("问题列表")
        questions_label.setFont(QFont('Arial', 14, QFont.Bold))
        questions_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(questions_label)
        
        # 问题列表
        self.questions_list = QListWidget()
        self.questions_list.setFont(QFont('Consolas', 11))
        self.questions_list.setMinimumHeight(200)
        self.questions_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(255, 255, 255, 100);
                border: 1px solid rgba(52, 152, 219, 100);
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: rgba(52, 152, 219, 150);
                color: white;
            }
        """)
        left_layout.addWidget(self.questions_list)
        
        # 问题列表按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(5)
        
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
            QPushButton:checked {
                background-color: rgba(41, 128, 185, 255);
            }
        """
        
        self.add_question_btn = QPushButton('+')
        self.remove_question_btn = QPushButton('-')
        self.edit_question_btn = QPushButton('✎')
        self.auto_mode_btn = QPushButton('▶')
        
        for btn in [self.add_question_btn, self.remove_question_btn, 
                   self.edit_question_btn, self.auto_mode_btn]:
            btn.setStyleSheet(button_style)
            btn.setMinimumWidth(40)
            btn.setFont(QFont('Arial', 14))
            btn.setToolTip({
                self.add_question_btn: '添加问题',
                self.remove_question_btn: '删除问题',
                self.edit_question_btn: '编辑问题',
                self.auto_mode_btn: '自动模式'
            }[btn])
        
        self.auto_mode_btn.setCheckable(True)
        
        buttons_layout.addWidget(self.add_question_btn)
        buttons_layout.addWidget(self.remove_question_btn)
        buttons_layout.addWidget(self.edit_question_btn)
        buttons_layout.addWidget(self.auto_mode_btn)
        
        left_layout.addLayout(buttons_layout)
        
        # 设置左侧部件宽度
        left_widget.setMinimumWidth(175)  # 减小最小宽度
        left_widget.setMaximumWidth(200)  # 减小最大宽度
        
        # 创建右侧聊天区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        
        # 聊天历史区域
        chat_frame = GlassFrame()
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(10, 10, 10, 10)
        
        self.chat_text = QTextEdit()
        self.chat_text.setReadOnly(True)
        self.chat_text.setFont(QFont('Consolas', 11))
        self.chat_text.setMinimumHeight(250)  # 减小最小高度
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
        
        # 输入区域
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
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.send_button = QPushButton('发送')
        self.network_button = QPushButton('联网')
        self.deep_think_button = QPushButton('深度思考')  # 新增深度思考按钮
        self.new_chat_button = QPushButton('新对话')
        self.floating_btn = QPushButton('📌')
        self.insert_button = QPushButton('插入')
        
        for btn in [self.send_button, self.network_button, self.deep_think_button, self.new_chat_button, self.floating_btn, self.insert_button]:
            btn.setStyleSheet(button_style)
            btn.setMinimumWidth(80)
            btn.setFont(QFont('Arial', 11))
            btn.setToolTip({
                self.send_button: '发送消息',
                self.network_button: '联网',
                self.deep_think_button: '深度思考',
                self.new_chat_button: '开始新对话',
                self.floating_btn: '窗口悬浮',
                self.insert_button: '插入选中文本到问题列表'
            }[btn])
        
        self.floating_btn.setCheckable(True)
        self.insert_button.setEnabled(False)
        
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.network_button)
        button_layout.addWidget(self.deep_think_button)  # 添加深度思考按钮到布局
        button_layout.addWidget(self.insert_button)
        button_layout.addWidget(self.new_chat_button)
        button_layout.addWidget(self.floating_btn)
        
        # 添加所有组件到右侧布局
        right_layout.addWidget(chat_frame)
        right_layout.addWidget(input_frame)
        right_layout.addLayout(button_layout)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        # 添加分割器到主布局
        main_layout.addWidget(splitter)
        
        # 创建状态栏
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: rgba(255, 255, 255, 100);
                color: #2c3e50;
            }
        """)
        self.status_bar.showMessage('就绪')
        
        # 连接信号
        self.send_button.clicked.connect(self.send_message)
        self.new_chat_button.clicked.connect(self.new_chat)
        self.input_text.textChanged.connect(self.check_input)
        self.add_question_btn.clicked.connect(self.add_question)
        self.remove_question_btn.clicked.connect(self.remove_question)
        self.edit_question_btn.clicked.connect(self.edit_question)
        self.auto_mode_btn.clicked.connect(self.toggle_auto_mode)
        self.floating_btn.clicked.connect(self.toggle_floating)
        self.questions_list.itemClicked.connect(self.question_selected)
        self.chat_text.selectionChanged.connect(self.on_selection_changed)
        self.insert_button.clicked.connect(self.insert_selected_text)
        self.network_button.clicked.connect(self.on_network_clicked)
        self.deep_think_button.clicked.connect(self.on_deep_think_clicked)  # 连接深度思考按钮信号
        
        # 设置快捷键
        self.input_text.installEventFilter(self)
        
        # 初始化自动发送定时器
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.send_next_question)
    
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
        # 启动按钮检查定时器
        self.check_button_timer.start(1000)  # 每秒检查一次
    
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
    
    def add_question(self):
        """添加新问题"""
        question, ok = QInputDialog.getText(self, '添加问题', '请输入问题:')
        if ok and question.strip():
            self.questions.append(question.strip())
            self.questions_list.addItem(question.strip())
    
    def remove_question(self):
        """删除选中的问题"""
        current_item = self.questions_list.currentItem()
        if current_item:
            index = self.questions_list.row(current_item)
            self.questions.pop(index)
            self.questions_list.takeItem(index)
    
    def edit_question(self):
        """编辑选中的问题"""
        current_item = self.questions_list.currentItem()
        if current_item:
            index = self.questions_list.row(current_item)
            question, ok = QInputDialog.getText(self, '编辑问题', '请输入问题:', text=current_item.text())
            if ok and question.strip():
                self.questions[index] = question.strip()
                current_item.setText(question.strip())
    
    def question_selected(self, item):
        """问题被选中时"""
        self.input_text.setText(item.text())
    
    def toggle_auto_mode(self):
        """切换自动模式"""
        self.auto_mode = self.auto_mode_btn.isChecked()
        if self.auto_mode:
            if not self.questions:
                QMessageBox.warning(self, '警告', '问题列表为空，请先添加问题！')
                self.auto_mode_btn.setChecked(False)
                self.auto_mode = False
                return
            self.current_question_index = 0
            self.auto_timer.start(5000)  # 每5秒发送一个问题
            self.auto_mode_btn.setText('停止自动')
        else:
            self.auto_timer.stop()
            self.auto_mode_btn.setText('自动模式')
    
    def send_next_question(self):
        """发送下一个问题"""
        try:
            if not self.auto_mode or not self.questions:
                return
                
            # 检查是否有正在进行的对话线程
            if any(thread.isRunning() for thread in self.chat_threads):
                print("机器人:上一个对话还在进行中，等待完成...")
                return
                
            # 检查当前状态是否为"就绪"
            if self.status_bar.currentMessage() != "就绪":
                print("等待就绪状态...")
                return
                
            if self.current_question_index < len(self.questions):
                question = self.questions[self.current_question_index]
                self.input_text.setText(question)
                self.send_message()
                
                # 删除已发送的问题
                self.questions.pop(self.current_question_index)
                self.questions_list.takeItem(self.current_question_index)
                
                # 如果问题列表为空，停止自动模式
                if not self.questions:
                    self.auto_mode_btn.setChecked(False)
                    self.auto_mode = False
                    self.auto_timer.stop()
                    self.auto_mode_btn.setText('自动模式')
                    QMessageBox.information(self, '完成', '所有问题已发送完成！')
            else:
                self.auto_mode_btn.setChecked(False)
                self.auto_mode = False
                self.auto_timer.stop()
                self.auto_mode_btn.setText('自动模式')
                QMessageBox.information(self, '完成', '所有问题已发送完成！')
        except Exception as e:
            print(f"发送下一个问题时出错: {str(e)}")
            self.auto_mode_btn.setChecked(False)
            self.auto_mode = False
            self.auto_timer.stop()
            self.auto_mode_btn.setText('自动模式')
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        # 停止按钮检查定时器
        if self.check_button_timer:
            self.check_button_timer.stop()
            
        # 停止自动发送定时器
        if self.auto_timer:
            self.auto_timer.stop()
        
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

    def on_selection_changed(self):
        """处理文本选择变化事件"""
        # 检查是否有文本被选中
        cursor = self.chat_text.textCursor()
        has_selection = cursor.hasSelection()
        
        # 根据选择状态启用或禁用插入按钮
        self.insert_button.setEnabled(has_selection)
        
        # 更新按钮样式
        if has_selection:
            self.insert_button.setStyleSheet("""
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
            """)
        else:
            self.insert_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(52, 152, 219, 100);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 12px;
                }
            """)
    
    def insert_selected_text(self):
        """将选中的文本插入到问题列表中"""
        # 获取选中的文本
        cursor = self.chat_text.textCursor()
        selected_text = cursor.selectedText().strip()
        
        if selected_text:
            # 创建自定义对话框
            dialog = QDialog(self)
            dialog.setWindowTitle('修改问题')
            dialog.setMinimumWidth(300)
            dialog.setMinimumHeight(200)
            
            # 创建布局
            layout = QVBoxLayout(dialog)
            layout.setSpacing(10)
            
            # 添加标签
            label = QLabel('请修改问题内容:')
            label.setFont(QFont('Arial', 11))
            layout.addWidget(label)
            
            # 创建文本编辑区域
            text_edit = QTextEdit()
            text_edit.setFont(QFont('Consolas', 11))
            text_edit.setMinimumHeight(300)
            text_edit.setText(selected_text)
            layout.addWidget(text_edit)
            
            # 创建按钮区域
            button_layout = QHBoxLayout()
            button_layout.setSpacing(10)
            
            ok_button = QPushButton('确定')
            cancel_button = QPushButton('取消')
            
            # 设置按钮样式
            for btn in [ok_button, cancel_button]:
                btn.setMinimumWidth(100)
                btn.setFont(QFont('Arial', 11))
            
            button_layout.addWidget(ok_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            # 连接按钮信号
            ok_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)
            
            # 显示对话框
            if dialog.exec_() == QDialog.Accepted:
                modified_text = text_edit.toPlainText().strip()
                if modified_text:
                    # 添加到问题列表
                    self.questions.append(modified_text)
                    self.questions_list.addItem(modified_text)
                    
                    # 隐藏插入按钮
                    self.insert_button.hide()
                    
                    # 清除选择
                    cursor.clearSelection()
                    self.chat_text.setTextCursor(cursor)

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

    def toggle_floating(self):
        """切换窗口悬浮状态"""
        self.is_floating = self.floating_btn.isChecked()
        if self.is_floating:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.floating_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(41, 128, 185, 255);
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
                QPushButton:checked {
                    background-color: rgba(41, 128, 185, 255);
                }
            """)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.floating_btn.setStyleSheet("""
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
                QPushButton:checked {
                    background-color: rgba(41, 128, 185, 255);
                }
            """)
        self.show()  # 重新显示窗口以应用新的窗口标志

    def on_network_clicked(self):
        """联网按钮点击事件"""
        try:
            if self.driver and self.wait:
                self.status_bar.showMessage("正在启用联网搜索...")
                
                # 等待并获取所有匹配的按钮
                # 尝试多种可能的按钮选择器
                button_selectors = [
                    "button.feec6a7a.f79352dc._70150b8.a567dba3"
                ]
                
                buttons = None
                for selector in button_selectors:
                    try:
                        print(f"尝试按钮选择器: {selector}")
                        buttons = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                        if buttons:
                            print(f"成功找到按钮，使用选择器: {selector}")
                            break
                    except:
                        continue
                
                if not buttons:
                    raise Exception("未找到联网搜索按钮")
                
                if len(buttons) >= 2:  # 确保有至少两个按钮
                    # 点击第二个按钮(联网搜索)
                    self.wait.until(EC.visibility_of(buttons[1]))
                    self.driver.execute_script("arguments[0].click();", buttons[1])
                    time.sleep(3)
                    self.status_bar.showMessage("联网搜索已启用")
                else:
                    raise Exception("未找到联网搜索按钮")
            else:
                QMessageBox.warning(self, '警告', '浏览器未就绪!')
        except Exception as e:
            self.status_bar.showMessage(f"启用联网搜索失败: {str(e)}")
            QMessageBox.warning(self, '错误', f'启用联网搜索时出错: {str(e)}')

    def on_deep_think_clicked(self):
        """深度思考按钮点击事件"""
        try:
            if self.driver and self.wait:
                self.status_bar.showMessage("正在启用深度思考...")
                
                # 等待并获取所有匹配的按钮
                # 尝试多种可能的深度思考按钮选择器
                deep_think_selectors = [
                    "button.feec6a7a.f79352dc._70150b8.a567dba3"
                ]
                
                buttons = None
                for selector in deep_think_selectors:
                    try:
                        print(f"尝试深度思考按钮选择器: {selector}")
                        buttons = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
                        if buttons:
                            print(f"成功找到深度思考按钮，使用选择器: {selector}")
                            break
                    except:
                        continue
                
                if not buttons:
                    raise Exception("未找到深度思考按钮")
                
                if len(buttons) >= 1:  # 确保至少有一个按钮
                    # 点击第一个按钮(深度思考)
                    self.wait.until(EC.visibility_of(buttons[0]))
                    self.driver.execute_script("arguments[0].click();", buttons[0])
                    time.sleep(3)
                    self.status_bar.showMessage("深度思考已启用")
                else:
                    raise Exception("未找到深度思考按钮")
            else:
                QMessageBox.warning(self, '警告', '浏览器未就绪!')
        except Exception as e:
            self.status_bar.showMessage(f"启用深度思考失败: {str(e)}")
            QMessageBox.warning(self, '错误', f'启用深度思考时出错: {str(e)}')

    def check_and_click_button(self):
        """检查并点击特定class的按钮"""
        try:
            if not self.driver or not self.wait:
                return
                
            # 使用JavaScript检查按钮是否存在并可见
            js_code = """
                var btn = document.querySelector('div.ds-button.ds-button--secondary.ds-button--bordered.ds-button--rect.ds-button--m');
                if (btn && btn.offsetParent !== null) {
                    return true;
                }
                return false;
            """
            button_visible = self.driver.execute_script(js_code)
            
            if button_visible:
                # 找到并点击按钮
                button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 
                    "div.ds-button.ds-button--secondary.ds-button--bordered.ds-button--rect.ds-button--m")))
                self.driver.execute_script("arguments[0].click();", button)
                print("自动点击了确认按钮")
                
        except Exception as e:
            # 这里我们不需要显示错误,因为按钮不存在是正常的情况
            pass

def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 