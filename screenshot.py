import os
import subprocess
import platform
import time
import json
import pyautogui
from datetime import datetime
from PIL import ImageGrab

CONFIG_FILE = 'config.json'

def load_config():
    """
    加载配置文件，如果不存在则创建默认配置
    """
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            default_config = {
                "position": {
                    "x": 0,
                    "y": 0,
                    "description": "默认位置"
                }
            }
            save_config(default_config)
            return default_config
    except Exception as e:
        print(f'加载配置文件失败: {str(e)}')
        return {"position": {"x": 0, "y": 0, "description": "默认位置"}}

def save_config(config):
    """
    保存配置到文件
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print('配置已保存')
    except Exception as e:
        print(f'保存配置文件失败: {str(e)}')

def take_screenshot():
    try:
        # 创建screenshots文件夹（如果不存在）
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        # 生成文件名（使用时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshots/screenshot_{timestamp}.png'
        
        # 根据操作系统选择不同的截图方法
        system = platform.system().lower()
        
        if system == 'darwin':  # macOS
            # 使用screencapture命令截图
            result = subprocess.run(['screencapture', '-x', filename], capture_output=True, text=True)
            if result.returncode == 0:
                print(f'截图已保存: {filename}')
            else:
                print(f'截图失败: {result.stderr}')
        
        elif system == 'windows':  # Windows
            # 使用PIL的ImageGrab进行截图
            screenshot = ImageGrab.grab()
            screenshot.save(filename)
            print(f'截图已保存: {filename}')
        
        else:
            print(f'不支持的操作系统: {system}')
            
    except Exception as e:
        print(f'截图失败: {str(e)}')

def click_at_position(x, y, clicks=1, interval=0.25):
    """
    在指定坐标点击鼠标左键
    """
    try:
        # 保存当前鼠标位置
        current_x, current_y = pyautogui.position()
        
        # 移动到指定位置
        pyautogui.moveTo(x, y, duration=0.5)
        
        # 执行点击
        pyautogui.click(clicks=clicks, interval=interval)
        
        # 移回原位置
        pyautogui.moveTo(current_x, current_y, duration=0.5)
        
        print(f'已在坐标 ({x}, {y}) 完成 {clicks} 次点击')
        
    except Exception as e:
        print(f'点击失败: {str(e)}')

def get_mouse_position():
    """
    获取当前鼠标位置并保存到配置文件
    """
    x, y = pyautogui.position()
    print(f'当前鼠标位置: ({x}, {y})')
    
    # 询问是否保存该位置
    save = input('是否保存该位置？(y/n): ').lower()
    if save == 'y':
        description = input('请输入该位置的描述: ')
        
        config = load_config()
        config['position'] = {
            'x': x,
            'y': y,
            'description': description
        }
        save_config(config)
    
    return x, y

def show_saved_position():
    """
    显示保存的位置
    """
    config = load_config()
    position = config['position']
    print('\n保存的位置:')
    print(f"坐标: ({position['x']}, {position['y']})")
    print(f"描述: {position['description']}")

def click_saved_position():
    """
    点击保存的位置
    """
    config = load_config()
    position = config['position']
    
    print('\n当前保存的位置:')
    print(f"坐标: ({position['x']}, {position['y']})")
    print(f"描述: {position['description']}")
    
    confirm = input('是否点击该位置？(y/n): ').lower()
    if confirm == 'y':
        clicks = int(input('请输入点击次数（默认1次）: ') or '1')
        click_at_position(position['x'], position['y'], clicks)

if __name__ == '__main__':
    # 设置pyautogui的安全选项
    pyautogui.FAILSAFE = True
    
    while True:
        print('\n请选择操作：')
        print('1. 截图')
        print('2. 指定坐标点击')
        print('3. 获取并保存当前鼠标位置')
        print('4. 查看保存的位置')
        print('5. 点击保存的位置')
        print('0. 退出程序')
        
        choice = input('请输入选项（0-5）: ')
        
        if choice == '1':
            print('正在截图...')
            take_screenshot()
        elif choice == '2':
            try:
                x = int(input('请输入横坐标 X: '))
                y = int(input('请输入纵坐标 Y: '))
                clicks = int(input('请输入点击次数（默认1次）: ') or '1')
                click_at_position(x, y, clicks)
            except ValueError:
                print('输入无效，请输入数字')
        elif choice == '3':
            print('请在3秒内将鼠标移动到目标位置...')
            time.sleep(3)
            get_mouse_position()
        elif choice == '4':
            show_saved_position()
        elif choice == '5':
            click_saved_position()
        elif choice == '0':
            print('程序已退出')
            break
        else:
            print('无效的选项') 