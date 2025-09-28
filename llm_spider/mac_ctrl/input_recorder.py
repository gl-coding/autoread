import pyautogui
import keyboard
import time
from datetime import datetime
import threading
import queue

class InputRecorder:
    def __init__(self):
        self.running = False
        self.mouse_positions = []
        self.start_time = None
        self.event_queue = queue.Queue()
        
    def record_mouse(self):
        """记录鼠标移动和点击"""
        last_position = None
        while self.running:
            try:
                # 获取当前鼠标位置
                current_position = pyautogui.position()
                
                # 如果位置发生变化，记录新位置
                if current_position != last_position:
                    current_time = time.time() - self.start_time
                    self.mouse_positions.append((current_position.x, current_position.y, current_time))
                    self.event_queue.put(('move', current_position.x, current_position.y))
                    last_position = current_position
                
                # 检查鼠标点击
                if pyautogui.mouseDown():
                    self.event_queue.put(('click', current_position.x, current_position.y, 'down'))
                if pyautogui.mouseUp():
                    self.event_queue.put(('click', current_position.x, current_position.y, 'up'))
                
                time.sleep(0.1)  # 降低CPU使用率
                
            except Exception as e:
                print(f"记录鼠标时出错: {str(e)}")
                break
    
    def record_keyboard(self):
        """记录键盘输入"""
        while self.running:
            try:
                # 使用keyboard库记录按键
                event = keyboard.read_event()
                if event.event_type == keyboard.KEY_DOWN:
                    self.event_queue.put(('key', event.name, 'down'))
                elif event.event_type == keyboard.KEY_UP:
                    self.event_queue.put(('key', event.name, 'up'))
            except Exception as e:
                print(f"记录键盘时出错: {str(e)}")
                break
    
    def process_events(self):
        """处理记录的事件"""
        while self.running:
            try:
                event = self.event_queue.get(timeout=0.1)
                event_type = event[0]
               
                if event_type == 'move':
                    x, y = event[1], event[2]
                    print(f"鼠标移动到: ({x}, {y})")
                elif event_type == 'click':
                    _, x, y, action = event
                    print(f"{action.capitalize()}鼠标在位置 ({x}, {y})")
                elif event_type == 'key':
                    _, key, action = event
                    print(f"{action.capitalize()}键盘{key}")
            except Exception as e:
                print(f"处理事件时出错: {str(e)}")
    
    def start_recording(self):
        """开始记录"""
        print("开始记录用户输入...")
        print("按 'Esc' 键停止记录")
        self.running = True
        self.start_time = time.time()
        
        # 创建并启动记录线程
        mouse_thread = threading.Thread(target=self.record_mouse)
        keyboard_thread = threading.Thread(target=self.record_keyboard)
        process_thread = threading.Thread(target=self.process_events)
        
        mouse_thread.start()
        keyboard_thread.start()
        process_thread.start()
        
        # 等待Esc键
        keyboard.wait('esc')
        
    def stop_recording(self):
        """停止记录"""
        self.running = False
        print("\n记录已停止")
        
    def print_summary(self):
        """打印记录摘要"""
        print("\n=== 记录摘要 ===")
        print(f"记录时长: {time.time() - self.start_time:.2f} 秒")
        print(f"鼠标移动轨迹点数量: {len(self.mouse_positions)}")
        print("================\n")

def main():
    recorder = InputRecorder()
    try:
        recorder.start_recording()
    except KeyboardInterrupt:
        print("\n用户中断记录")
    finally:
        recorder.stop_recording()
        recorder.print_summary()

if __name__ == "__main__":
    main() 