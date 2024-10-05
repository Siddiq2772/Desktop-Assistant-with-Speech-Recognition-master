import sys, time
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QTextEdit, QGridLayout
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
import pyttsx3
import speech_recognition as sr
import datetime
import os
import requests
import wikipedia
import webbrowser
import pywhatkit as kit
import pygetwindow as gw
import AppOpener
import gemini_ai
import time
import psutil
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

BtnTextFont = '30px'
host = '127.0.0.1'  # The server's hostname or IP address
port = 65432        # The port used by the server

mic_on =True

class VoiceAssistant:
    def __init__(self):
        self.engine = pyttsx3.init("sapi5")
        self.commands = ["open", "shutdown", "ip address of my device", "minimise window", "close window", 
                         "maximise window", "go to", "search on google", "search on wikipedia", "current temperature", 
                         "send message", "ai mode", "sleep", "current date", "restart", "play video on youtube", 
                         "help", "close", "battery", "current time", "Incomplete", "mute", "unmute", "exit"]
        self.system_control = SystemControls(self)
        self.audio_control = AudioControls(self)
        self.web_handler = WebHandler(self)
        global  mic_on
        self.chat_window = ChatWindow()


        
    
    def print(self,msg):
        self.chat_window.add_message(msg)
    def set_speech_rate(self, rate):
        self.engine.setProperty('rate', rate)

    def speak(self, text, speed=200):
        self.set_speech_rate(speed)
        self.engine.say(text)
        self.engine.runAndWait()

    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.print("Listening...")
            r.pause_threshold = 0.8
            try:
                if not mic_on:  return 
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                if not mic_on:  return 
                self.print("Recognizing...")
                query = r.recognize_google(audio)
                self.print(query)
                return query.lower()
            except sr.WaitTimeoutError:
                self.speak("Listening timed out. Please try again.")
            except sr.UnknownValueError:
                self.speak("Sorry, I did not understand that.")
            except sr.RequestError:
                self.speak("Sorry, there was an issue with the request.")
            return "none"

    def wish(self):
        now = int(datetime.datetime.now().hour)
        if 5 <= now < 12:
            self.speak("Good Morning")
        elif 12 <= now < 17:
            self.speak("Good Afternoon")
        else:
            self.speak("Good Evening")

    def process_command(self, command):
        """Handles the received command and triggers appropriate actions."""
        command_type, param = self.extract_command(command)
        if command_type:
            action = getattr(self, command_type, None)
            if action:
                if param:
                    action(param)
                else:
                    action()

    def extract_command(self, query):
        for command in self.commands:
            if query.startswith(command):
                param = query[len(command):].strip()
                return command, param
        return None, None

    def microphone_mode(self,interface):
        self.wish()
        self.speak("How can I help you, Sir?")
        while True:
            query = self.take_command().lower()
            if query == "none":
                continue
            elif not mic_on: 
                break
            interface.chat_window.add_message(query, is_sent=False)
            interface.chat_window.message_input.clear()
            self.process_command(query)
            time.sleep(3)
            self.speak("Sir, do you have any other work?")

    def keyboard_mode(self):
        self.wish()
        self.speak("How can I help you, Sir?")
         # wait for 1 second before checking again

    def input(self,interface):
        while True:
            if query == None : continue
            query = interface.chat_window.message_input.toPlainText().strip()
            if query:
                interface.chat_window.add_message(query, is_sent=False)
                interface.chat_window.message_input.clear()
                self.process_command(query)
                time.sleep(3)
                self.speak("Sir, do you have any other work?")
            time.sleep(1) 

    def start_keyboard_mode(self, interface):
        self.keyboard_thread = threading.Thread(target=self.keyboard_mode, args=(interface,))
        self.keyboard_thread.start()
    
    def start_microphone_mode(self,interface):
        self.microphone_thread = threading.Thread(target=self.microphone_mode, args=(interface,))
        self.microphone_thread.start()

    # Command execution functions
    def open(self, app_name):
        self.system_control.open_apps(app_name)

    def current_time(self):
        time_str = datetime.datetime.now().strftime("%I:%M %p")
        self.print(time_str)
        self.speak(f"The current time is {time_str}")

    def current_date(self):
        date_str = datetime.datetime.now().strftime("%B %d, %Y")
        self.print(f"Today's date is {date_str}")
        self.speak(f"Today's date is {date_str}")

    def help(self):
        help_text = (
            "Here are some commands you can use: \n\n"
            "1. Open <app>\n2. Search on Wikipedia <query>\n3. Current temperature in <city>\n"
            "4. Play video on YouTube <video_name>\n5. Shutdown, Restart, Sleep\n"
            "6. Send message\n7. Battery status\n"
        )
        self.print(help_text)
        self.speak(help_text)

    def exit(self):
        now = int(datetime.datetime.now().hour)
        if 5 <= now < 12:
            self.speak("Goodbye! Have a great day ahead!")
        elif 12 <= now < 17:
            self.speak("Goodbye! Have a wonderful afternoon!")
        elif 17 <= now < 21:
            self.speak("Goodbye! Have a pleasant evening!")
        else:
            self.speak("Goodbye! Have a restful night!")
        exit()

    # Forwarding to specific helper classes
    def ip_address(self):
        self.system_control.ip_address()

    def send_message(self, message):
        self.system_control.send_message(message)

    def mute(self):
        self.audio_control.mute()

    def unmute(self):
        self.audio_control.unmute()

    def current_temperature(self, city):
        self.web_handler.temperature(city)

    def play_video_on_youtube(self, video_name):
        self.web_handler.play_video_on_youtube(video_name)

    def search_on_google(self, query):
        self.web_handler.google_search(query)

    def search_on_wikipedia(self, query):
        self.web_handler.search_wikipedia(query)


class SystemControls:
    def __init__(self, assistant):
        self.assistant = assistant

    def restart(self):
        self.assistant.speak("Are you sure you want to restart your PC?")
        user = self.assistant.take_command().lower()
        if "yes" in user:
            self.assistant.speak("Your PC is restarting.")
            os.system("shutdown /r /t 0")
        else:
            self.assistant.speak("Restart canceled.")

    def battery_status(self):
        battery = psutil.sensors_battery()
        if battery:
            percentage = battery.percent
            plugged = battery.power_plugged
            plug_status = "Plugged In" if plugged else "Not Plugged In"
            self.assistant.speak(f"Your battery is at {percentage}% and {plug_status}")
        else:
            self.assistant.speak("Battery not found.")

    def open_apps(self, app_name):
        try:
            self.assistant.speak(f"Opening {app_name}")
            AppOpener.open(app_name, match_closest=True)
        except Exception as e:
            self.assistant.speak("Something went wrong opening the app.")

    def ip_address(self):
        try:
            ip = requests.get("https://api.ipify.org").text
            self.assistant.speak(f"Your IP address is {ip}")
        except Exception as e:
            self.assistant.speak("Unable to get IP address.")

    def send_message(self, message):
        self.assistant.speak("Please provide the phone number.")
        number = input("Enter phone no: ")
        self.assistant.speak("Sending message...")
        future_time = datetime.datetime.now() + datetime.timedelta(minutes=2)
        kit.sendwhatmsg(f"+91{number}", message, future_time.hour, future_time.minute)


class AudioControls:
    def __init__(self, assistant):
        self.assistant = assistant

    def mute(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(1, None)
            self.assistant.speak("System muted.")
        except Exception as e:
            self.assistant.speak("Failed to mute the system.")

    def unmute(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(0, None)
            self.assistant.speak("System unmuted.")
        except Exception as e:
            self.assistant.speak("Failed to unmute the system.")


class WebHandler:
    def __init__(self, assistant):
        self.assistant = assistant

    def search_wikipedia(self, query):
        self.assistant.speak("Searching Wikipedia")
        try:
            result = wikipedia.summary(query, sentences=2)
            self.assistant.speak(result)
        except Exception as e:
            self.assistant.speak("Failed to retrieve Wikipedia results.")

    def google_search(self, query):
        self.assistant.speak(f"Searching Google for {query}")
        kit.search(query)

    def play_video_on_youtube(self, video_name):
        self.assistant.speak(f"Playing {video_name} on YouTube.")
        kit.playonyt(video_name)

    def temperature(self, city):
        self.assistant.speak(f"Fetching current temperature in {city}")
        api_key = "your_api_key"
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = base_url + "q=" + city + "&appid=" + api_key + "&units=metric"
        try:
            response = requests.get(complete_url)
            data = response.json()
            if data["cod"] != "404":
                main = data["main"]
                temperature = main["temp"]
                self.assistant.speak(f"The current temperature in {city} is {temperature} degrees Celsius.")
            else:
                self.assistant.speak("City not found.")
        except Exception as e:
            self.assistant.speak("Unable to fetch the temperature at this time.")




class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Chat display area
        self.chat_list = QListWidget()
        self.chat_list.setSpacing(10)
        self.chat_list.setWordWrap(True)
        layout.addWidget(self.chat_list)

        # Input area (you can remove this if you don't need user input)
        self.input_layout = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setFixedHeight(50)
        self.input_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.input_layout.addWidget(self.send_button)

        layout.addLayout(self.input_layout)
        self.setLayout(layout)

        # Styling
        self.setStyleSheet("""
           QListWidget {
                background-color: #1e1e1e;
                color: white;
                font-size:20px;           
                border: none;
            }
            QTextEdit {
                background-color: #333333;
                color: white;
                border: 1px solid #ccc;
                border-radius: 10px;
                font-size:20px;           
                padding: 5px;
            }
            QPushButton {
                background-color: #25D366;
                color: white;
                border: none;
                border-radius: 10px;
                font-size:20px;           
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #128C7E;
            }
        """)

       
    def send_message(self):
        # This method is kept for potential future use
        message = self.message_input.toPlainText().strip()
        if message:
            self.add_message(message, is_sent=True)
            self.message_input.clear()

    def add_message(self, message, is_sent=False):
        item = QListWidgetItem()
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
        bubble_widget = self.create_bubble_widget(message, is_sent)
        item.setSizeHint(bubble_widget.sizeHint())
        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, bubble_widget)
        self.chat_list.scrollToBottom()

    def create_bubble_widget(self, message, is_sent):
        if message.startswith("You:"):
            is_sent = True
        widget = QWidget()
        layout = QHBoxLayout(widget)

        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(int(self.chat_list.width() * 0.7))
        bubble.setStyleSheet(f"""
            background-color: {'#00a884' if is_sent else '#333333'};
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-size:{BtnTextFont}
        """)

        if is_sent:
            layout.addStretch()
        layout.addWidget(bubble)
        if not is_sent:
            layout.addStretch()

        layout.setContentsMargins(10, 5, 10, 5)
        return widget

# NovaInterface with chat integration
class NovaInterface(QWidget):
    def __init__(self,assistant):
        super().__init__()
        self.initUI()
        self.assistant = assistant

        

    def initUI(self):
        self.setWindowTitle('NOVA')
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        self.setGeometry(0, 0, 800, 1000)

        # Main layout
        self.main_layout = QVBoxLayout()

        # Top section with grid layout
        top_layout = QGridLayout()

        # SK logo (top-left corner)
        sk_label = QLabel('SK')
        sk_label.setStyleSheet("background-color: #ff6600; color: #ffffff; font-weight: bold; padding: 5px; border-radius:20px;")
        sk_label.setFixedSize(40, 40)
        sk_label.setAlignment(Qt.AlignCenter)

        # NOVA label (centered)
        self.nova_label = QLabel('NOVA')
        self.nova_label.setStyleSheet("color: #87CEEB; font-size: 50px; font-weight: bold;")
        # Add widgets to the grid layout
        top_layout.addWidget(sk_label, 0, 0, Qt.AlignTop | Qt.AlignLeft)  # Top-left corner
        top_layout.addWidget(self.nova_label, 0, 1, Qt.AlignTop | Qt.AlignCenter)

        # Stretch settings for center and left side
        top_layout.setColumnStretch(0, 1)
        top_layout.setColumnStretch(1, 5)

        # Microphone button
        self.mic_button = QPushButton()
        self.mic_button.setIcon(QIcon('icons/mic.png'))
        self.mic_button.setIconSize(QSize(100, 100))  # Smaller icon size
        self.mic_button.setFixedSize(100, 100)  # Smaller button size
        self.mic_button.setStyleSheet("background-color: #0088ff; border-radius: 50px;")

        # Bottom buttons layout
        self.bottom_layout = QHBoxLayout()
        history_button = QPushButton('Show Chat History')
        history_button.setStyleSheet(f"background-color: #333333; font-size:{BtnTextFont}; color: #87CEEB; padding: 5px;")
        history_button.setIcon(QIcon('icons/menu.png'))
        history_button.setIconSize(QSize(30, 30))

        self.text_mode_button = QPushButton()
        self.text_mode_button.setStyleSheet(f"background-color: #333333; font-size:{BtnTextFont}; color: #87CEEB; padding: 5px;")
        self.text_mode_button.setIcon(QIcon('icons/keyboard.png'))
        self.text_mode_button.setIconSize(QSize(50, 50))
        self.text_mode_button.clicked.connect(self.toggle_input_mode)  # Connect the button to the toggle method

        self.float_window_button = QPushButton()
        self.float_window_button.setStyleSheet(f"background-color: #333333;font-size:{BtnTextFont}; color: #87CEEB; padding: 5px;")
        self.float_window_button.setIcon(QIcon('icons/popup_open.png'))
        self.float_window_button.setIconSize(QSize(50, 50))

        self.bottom_layout.addWidget(history_button)
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.mic_button)
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.text_mode_button)
        self.bottom_layout.addWidget(self.float_window_button)

        # Add all sections to the main layout
        self.main_layout.addLayout(top_layout)

        # Add the chat window in the middle
        self.chat_window = self.assistant.chat_window
        self.main_layout.addWidget(self.chat_window)
        self.main_layout.addLayout(self.bottom_layout)

        self.setLayout(self.main_layout)
        self.chat_window.message_input.hide()
        self.chat_window.send_button.hide()

    def toggle_input_mode(self):
        global mic_on
        if self.chat_window.message_input.isVisible():
            self.chat_window.message_input.hide()
            self.chat_window.send_button.hide()
            self.mic_button.show()
            mic_on = True
            assistant.start_microphone_mode(self)
        else:
            self.chat_window.message_input.show()
            self.chat_window.send_button.show()
            self.mic_button.hide()
            mic_on = False
            assistant.start_keyboard_mode(self)

   
    def on_new_message(self, message):
        # Add received messages to the chat window
        self.chat_window.add_message(message, is_sent=True)



if __name__ == '__main__':
    app = QApplication(sys.argv)    
    ex = NovaInterface(assistant=VoiceAssistant())

    ex.show()
    sys.exit(app.exec_())
