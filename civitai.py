import pyautogui
import cv2
import numpy as np
import time
import subprocess
import threading
import keyboard  # 需要安装：pip install keyboard

# 配置
TEMPLATE_PATH = "yellow_like.png"  # 黄色点赞按钮截图
URL = "https://civitai.com/images"  # 目标网页q
CONFIDENCE = 0.9  # 匹配置信度
SCROLL_AMOUNT = -1000  # 向下滚动的量
CLICK_DELAY = 0.5  # 每次点击后的等待时间
SCROLL_DELAY = 2  # 滚动后等待页面加载的时间
PAGE_LOAD_WAIT = 5  # 等待网页加载的时间

# 全局退出标志
running = True

def check_quit():
    """监听 Q 键退出"""
    global running
    while running:
        if keyboard.is_pressed('q'):
            running = False
            print("\n检测到 Q 键，正在退出...")
            break
        time.sleep(0.1)

def open_browser():
    """自动打开浏览器并访问网页"""
    print(f"正在打开网页： {URL}")
    # Windows 用 start，Mac 用 open，Linux 用 xdg-open
    try:
        # Windows
        subprocess.Popen(['start', URL], shell=True)
    except:
        try:
            # Mac
            subprocess.Popen(['open', URL])
        except:
            # Linux
            subprocess.Popen(['xdg-open', URL])
    
    print(f"等待 {PAGE_LOAD_WAIT} 秒让页面加载...")
    time.sleep(PAGE_LOAD_WAIT)

def find_all_buttons():
    """截屏并找到所有黄色点赞按钮"""
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    template = cv2.imread(TEMPLATE_PATH)
    if template is None:
        print("无法读取模板图片！")
        return []
    
    h, w = template.shape[:2]
    
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= CONFIDENCE)
    points = list(zip(*locations[::-1]))
    
    if not points:
        return []
    
    # 去重
    filtered_points = []
    for pt in points:
        too_close = False
        for fp in filtered_points:
            if abs(pt[0] - fp[0]) < w and abs(pt[1] - fp[1]) < h:
                too_close = True
                break
        if not too_close:
            filtered_points.append(pt)
    
    # 排序：从上到下，从左到右
    filtered_points.sort(key=lambda p: (p[1] // 100, p[0]))
    
    # 转换为点击中心坐标
    click_points = [(pt[0] + w // 2, pt[1] + h // 2) for pt in filtered_points]
    
    return click_points

def main():
    global running
    
    print("=" * 50)
    print("Civitai 自动点赞脚本")
    print("按 Q 键随时退出")
    print("=" * 50)
    
    # 启动退出监听线程
    quit_thread = threading.Thread(target=check_quit, daemon=True)
    quit_thread.start()
    
    # 打开浏览器
    open_browser()
    
    round_num = 0
    while running:
        round_num += 1
        print(f"\n=== 第 {round_num} 轮 ===")
        
        # 找到所有按钮
        buttons = find_all_buttons()
        print(f"找到 {len(buttons)} 个黄色点赞按钮")
        
        if not buttons:
            print("没有找到按钮，滚动后继续...")
            pyautogui.scroll(SCROLL_AMOUNT)
            time.sleep(SCROLL_DELAY)
            continue
        
        # 依次点击
        for i, (x, y) in enumerate(buttons):
            if not running:
                break
            print(f"点击第 {i + 1}/{len(buttons)} 个: ({x}, {y})")
            pyautogui.click(x, y)
            time.sleep(CLICK_DELAY)
        
        if not running:
            break
        
        # 滚动页面
        print("滚动页面...")
        pyautogui.scroll(SCROLL_AMOUNT)
        time.sleep(SCROLL_DELAY)
    
    print("\n脚本已退出！")

if __name__ == "__main__":
    main()
