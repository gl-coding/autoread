import pyautogui
import time
import sys
import os

from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID
)

# 设置安全保护，防止程序失控
pyautogui.FAILSAFE = True

def move_mouse(x, y, duration=0.5):
    """移动鼠标到指定坐标"""
    pyautogui.moveTo(x, y, duration=duration)

def click_mouse(button='left'):
    """点击鼠标"""
    pyautogui.click(button=button)

def double_click():
    """双击鼠标"""
    pyautogui.doubleClick()

def right_click():
    """右键点击"""
    pyautogui.rightClick()

def drag_mouse(x, y, duration=0.5):
    """拖拽鼠标"""
    pyautogui.dragTo(x, y, duration=duration)

def type_text(text):
    """输入文本"""
    pyautogui.write(text)

def type_text_with_delay(text, delay=0.01):
    """输入文本，每个字符之间有一定延迟"""
    for char in text:
        print(char)
        pyautogui.write(char, interval=delay)
        time.sleep(delay)

def press_key(key):
    """按下指定按键"""
    pyautogui.press(key)

def hotkey(*args):
    """组合键"""
    pyautogui.hotkey(*args)

def get_mouse_position():
    """获取当前鼠标位置"""
    return pyautogui.position()

def get_active_window():
    """获取当前活动窗口名称"""
    try:
        # 获取所有窗口信息
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID
        )
        
        # 遍历所有窗口找到活动窗口
        for window in window_list:
            if window.get('kCGWindowLayer', 0) == 0:  # 只获取主窗口
                window_name = window.get('kCGWindowName', '')
                if window_name:
                    return window_name
                # 如果没有窗口名称，尝试获取应用程序名称
                app_name = window.get('kCGWindowOwnerName', '')
                if app_name:
                    return app_name
        return "无法获取窗口名称"
    except Exception as e:
        return f"获取窗口名称时出错: {str(e)}"

def main():
    print("Mac 鼠标键盘控制程序")
    print("按 Ctrl+C 退出程序")
    
    try:
        while True:
            print("\n可用命令：")
            print("1. 移动鼠标")
            print("2. 点击鼠标")
            print("3. 双击鼠标")
            print("4. 右键点击")
            print("5. 拖拽鼠标")
            print("6. 输入文本")
            print("7. 输入文本（每个字符之间有一定延迟）")
            print("8. 按下按键")
            print("9. 组合键")
            print("10. 获取鼠标位置")
            print("11. 获取当前窗口名称")
            print("0. 退出")
            
            choice = input("\n请选择操作 (0-10): ")
            
            if choice == '1':
                x = int(input("请输入目标X坐标: "))
                y = int(input("请输入目标Y坐标: "))
                move_mouse(x, y)
            
            elif choice == '2':
                button = input("选择鼠标按键 (left/right): ")
                click_mouse(button)
            
            elif choice == '3':
                double_click()
            
            elif choice == '4':
                right_click()
            
            elif choice == '5':
                x = int(input("请输入目标X坐标: "))
                y = int(input("请输入目标Y坐标: "))
                drag_mouse(x, y)
            
            elif choice == '6':
                text = input("请输入要输入的文本: ")
                type_text(text)
            
            elif choice == '7':
                text = input("请输入要输入的文本: ")
                type_text_with_delay(text)
            
            elif choice == '8':
                key = input("请输入要按下的按键: ")
                press_key(key)
            
            elif choice == '9':
                keys = input("请输入组合键 (用空格分隔): ").split()
                hotkey(*keys)
            
            elif choice == '10':
                pos = get_mouse_position()
                print(f"当前鼠标位置: x={pos.x}, y={pos.y}")
            
            elif choice == '11':
                move_mouse(100, 100)
                time.sleep(1)
                click_mouse("left")
                window_name = get_active_window()
                print(f"当前活动窗口名称: {window_name}")
            
            elif choice == '0':
                print("程序退出")
                break
            
            else:
                print("无效的选择，请重试")
            
            time.sleep(1)  # 添加短暂延迟，防止操作过快
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit()

if __name__ == "__main__":
    main() 