import sys
import json
import pyautogui
import time
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtWidgets import QMessageBox

class MouseTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.performing_action = False
        self.setup_screenshots_dir()
        self.initUI()
        
    def setup_screenshots_dir(self):
        # 创建screenshots目录
        self.screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots')
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
        
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('鼠标坐标跟踪器')
        self.setFixedSize(400, 300)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建坐标显示标签
        self.coord_label = QLabel('鼠标坐标: (0, 0)')
        self.coord_label.setFont(QFont('Arial', 20))
        self.coord_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.coord_label)
        
        # 创建保存的坐标显示
        saved_coord_layout = QHBoxLayout()
        self.saved_coord_label = QLabel('保存的坐标:')
        self.saved_x_label = QLabel('X:')
        self.saved_y_label = QLabel('Y:')
        self.saved_x_edit = QLineEdit()
        self.saved_y_edit = QLineEdit()
        
        # 设置只接受数字输入
        self.saved_x_edit.setValidator(QIntValidator())
        self.saved_y_edit.setValidator(QIntValidator())
        
        saved_coord_layout.addWidget(self.saved_coord_label)
        saved_coord_layout.addWidget(self.saved_x_label)
        saved_coord_layout.addWidget(self.saved_x_edit)
        saved_coord_layout.addWidget(self.saved_y_label)
        saved_coord_layout.addWidget(self.saved_y_edit)
        layout.addLayout(saved_coord_layout)
        
        # 创建描述输入框
        desc_layout = QHBoxLayout()
        self.desc_label = QLabel('描述:')
        self.desc_edit = QLineEdit()
        desc_layout.addWidget(self.desc_label)
        desc_layout.addWidget(self.desc_edit)
        layout.addLayout(desc_layout)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        
        self.save_manual_button = QPushButton('保存编辑的坐标')
        self.save_manual_button.clicked.connect(self.save_manual_position)
        button_layout.addWidget(self.save_manual_button)
        
        self.click_button = QPushButton('点击保存的坐标')
        self.click_button.clicked.connect(self.click_saved_position)
        button_layout.addWidget(self.click_button)
        
        self.loop_button = QPushButton('开始循环点击')
        self.loop_button.clicked.connect(self.toggle_loop_click)
        button_layout.addWidget(self.loop_button)
        
        layout.addLayout(button_layout)
        
        # 创建状态标签
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 设置定时器更新鼠标位置
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_mouse_position)
        self.timer.start(100)  # 每100毫秒更新一次
        
        # 加载保存的坐标
        self.load_saved_position()
        
        # 显示窗口
        self.show()
    
    def update_mouse_position(self):
        x, y = pyautogui.position()
        self.coord_label.setText(f'鼠标坐标: ({x}, {y})')
    
    def save_current_position(self):
        x, y = pyautogui.position()
        self.saved_x_edit.setText(str(x))
        self.saved_y_edit.setText(str(y))
        self.save_position(x, y)
    
    def save_manual_position(self):
        try:
            x = int(self.saved_x_edit.text() or 0)
            y = int(self.saved_y_edit.text() or 0)
            self.save_position(x, y)
        except ValueError:
            QMessageBox.warning(self, '错误', '请输入有效的坐标数值')
    
    def save_position(self, x, y):
        config = {
            "position": {
                "x": x,
                "y": y,
                "description": self.desc_edit.text()
            }
        }
        
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            self.status_label.setText('坐标已保存')
        except Exception as e:
            self.status_label.setText(f'保存失败: {str(e)}')
    
    def load_saved_position(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                position = config.get('position', {})
                self.saved_x_edit.setText(str(position.get('x', 0)))
                self.saved_y_edit.setText(str(position.get('y', 0)))
                self.desc_edit.setText(position.get('description', ''))
        except FileNotFoundError:
            pass
        except Exception as e:
            self.status_label.setText(f'加载失败: {str(e)}')
    
    def click_saved_position(self):
        try:
            x = int(self.saved_x_edit.text() or 0)
            y = int(self.saved_y_edit.text() or 0)
            
            # 保存当前鼠标位置
            current_x, current_y = pyautogui.position()
            
            # 移动到保存的位置并点击
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.click()
            
            # 移回原位置
            pyautogui.moveTo(current_x, current_y, duration=0.5)
            
            self.status_label.setText('点击完成')
        except ValueError:
            self.status_label.setText('无效的坐标')
        except Exception as e:
            self.status_label.setText(f'点击失败: {str(e)}')

    def toggle_loop_click(self):
        if self.loop_button.text() == '开始循环点击':
            self.start_loop_click()
        else:
            self.stop_loop_click()

    def start_loop_click(self):
        try:
            self.x = int(self.saved_x_edit.text() or 0)
            self.y = int(self.saved_y_edit.text() or 0)
            
            # 更改按钮状态
            self.loop_button.setEnabled(False)
            self.save_manual_button.setEnabled(False)
            self.click_button.setEnabled(False)
            
            # 创建循环定时器
            self.loop_timer = QTimer()
            self.loop_timer.timeout.connect(self.perform_loop_action)
            self.loop_timer.start(2000)  # 每2秒执行一次
            
            # 创建鼠标位置检测定时器
            self.mouse_check_timer = QTimer()
            self.mouse_check_timer.timeout.connect(self.check_mouse_position)
            self.mouse_check_timer.start(100)  # 每0.1秒检查一次
            
            # 记录上一次的鼠标位置
            self.last_mouse_x, self.last_mouse_y = pyautogui.position()
            
            self.status_label.setText('循环点击已开始 (移动鼠标可停止)')
        except ValueError:
            self.status_label.setText('无效的坐标')
            self.enable_all_buttons()
    
    def stop_loop_click(self):
        if hasattr(self, 'loop_timer'):
            self.loop_timer.stop()
        if hasattr(self, 'mouse_check_timer'):
            self.mouse_check_timer.stop()
        self.enable_all_buttons()
        self.status_label.setText('循环点击已停止')
    
    def enable_all_buttons(self):
        self.loop_button.setEnabled(True)
        self.save_manual_button.setEnabled(True)
        self.click_button.setEnabled(True)
    
    def check_mouse_position(self):
        if not self.performing_action:  # 只在不执行动作时检查
            current_x, current_y = pyautogui.position()
            if (current_x, current_y) != (self.last_mouse_x, self.last_mouse_y):
                self.stop_loop_click()
                self.status_label.setText('检测到鼠标被移动，已停止循环')
            self.last_mouse_x, self.last_mouse_y = current_x, current_y
    
    def perform_loop_action(self):
        try:
            self.performing_action = True  # 标记正在执行动作
            
            # 保存当前鼠标位置
            current_x, current_y = pyautogui.position()
            
            # 移动到保存的位置并点击
            pyautogui.moveTo(self.x, self.y, duration=0.1)
            pyautogui.click()
            
            # 等待1秒
            time.sleep(0.5)
            
            # 截图
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot = pyautogui.screenshot()
            screenshot_path = os.path.join(self.screenshots_dir, f'screenshot_{timestamp}.png')
            screenshot.save(screenshot_path)
            
            # 移回原位置
            pyautogui.moveTo(current_x, current_y, duration=0.1)
            
            self.status_label.setText(f'循环点击和截图完成: {timestamp}')
            self.performing_action = False  # 标记动作完成
        except Exception as e:
            self.status_label.setText(f'循环操作失败: {str(e)}')
            self.stop_loop_click()
            self.performing_action = False  # 确保标记被重置

def main():
    app = QApplication(sys.argv)
    tracker = MouseTracker()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 