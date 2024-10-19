import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout,QStackedWidget, QLabel, QPushButton, QTextEdit, QGridLayout, QScrollArea, QFrame
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon,QMovie
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from PyQt5 import QtWidgets
from comtypes import CLSCTX_ALL
import ctypes
from backend import *
import backend as b
import database as db
BtnTextFont = '25px'
toggleMic = True
prompt = "none"
btnStyle = f"background-color: #333333; font-size: {BtnTextFont}; color: #87CEEB; padding: 5px; border-radius:5px"
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
movie = None
ret = None
class PopupWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle('NOVA')
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        self.setGeometry(0, 0, 300, 300)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)


        layout = QVBoxLayout()

        self.mic_button = self.main_window.create_mic_button()
        self.mic_button.clicked.connect(self.main_window.micon)
        
        self.show_main_button = QPushButton('Show Main Window', self)
        self.show_main_button.clicked.connect(self.show_main_window)
        self.show_main_button.setStyleSheet(btnStyle)
        
        layout.addWidget(self.mic_button)
        layout.addWidget(self.show_main_button)

        self.setLayout(layout)

    def show_main_window(self):
        self.hide()
        self.main_window.show_main_interface()

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Scrollable area for chat bubbles
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #1e1e1e; border: none;")

        # Widget to hold the layout of chat bubbles
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.chat_container)

        layout.addWidget(self.scroll_area)

        # Input area
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
            QTextEdit {
                background-color: #333333;
                color: white;
                border: 1px solid #ccc;
                border-radius: 20px;
                font-size: 20px;
                padding: 5px;
            }
            QPushButton {
                background-color: #25D366;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 20px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #128C7E;
            }
        """)

    def send_message(self):
        global prompt
        message = self.message_input.toPlainText().strip()
        if message:
            prompt = message
            self.message_input.clear()

    def add_message(self, message, is_sent=False):
        # Create a bubble widget for the message
        bubble_widget = self.create_bubble_widget(message, is_sent)
        self.chat_layout.addWidget(bubble_widget)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    

    def create_bubble_widget(self, message, is_sent):
        # Create a QWidget to act as the message bubble
        bubble_frame = QFrame()
        bubble_layout = QHBoxLayout(bubble_frame)
        if message.startswith("You:"): is_sent= True

        
        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(int(self.scroll_area.width() * 0.7))
        bubble.setStyleSheet(f"""
            background-color: {'#00a884' if is_sent else '#333333'};
            color: white;
            border-radius: 10px;
            padding: 10px;
            font-size:{BtnTextFont}
        """)  

        if is_sent:
            bubble_layout.addStretch()  # Right-align sent messages
            bubble_layout.addWidget(bubble)
        else:
            bubble_layout.addWidget(bubble)  # Left-align received messages
            bubble_layout.addStretch()

        bubble_layout.setContentsMargins(10, 5, 10, 5)
        return bubble_frame


# NovaInterface with chat integration
class NovaInterface(QWidget):
    def __init__(self):
        global movie
        movie = QMovie("icons/mic_ani.gif")
        super().__init__()
        self.initUI()
        volume.SetMute(False, None)
        self.chat_window.message_input.installEventFilter(self)
        self.is_popup_mode = False
        # demo(self)


    def initUI(self):
        self.setWindowTitle('NOVA')
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        self.setGeometry(0, 0, 800, 1000)
        self.popup = PopupWindow(self)


        # Main layout
        self.main_layout = QVBoxLayout()

        # Top section with grid layout
        top_layout = QGridLayout()

        # SK logo (top-left corner)
        sk_label = QLabel('SK')
        sk_label.setStyleSheet("background-color: #ff6600; color: #ffffff; font-weight: bold; padding: 5px; border-radius: 20px;")
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

        self.mic_button = self.create_mic_button()       
        self.mic_button.clicked.connect(self.micon)
        # Bottom buttons layout
        
        self.bottom_layout = QHBoxLayout()
        history_button = QPushButton('Show Chat History')
        history_button.setStyleSheet(btnStyle)
        history_button.setIcon(QIcon('icons/menu.png'))
        history_button.setIconSize(QSize(30, 30))

        self.text_mode_button = QPushButton()
        self.text_mode_button.setStyleSheet(btnStyle)
        self.text_mode_button.setIcon(QIcon('icons/keyboard.png'))
        self.text_mode_button.setIconSize(QSize(50, 50))
        self.text_mode_button.clicked.connect(self.toggle_input_mode)

        self.mute_button = QPushButton()
        self.mute_button.setStyleSheet(btnStyle)
        self.mute_button.setIcon(QIcon('icons/unmute.png'))
        self.mute_button.setIconSize(QSize(50, 50))
        self.mute_button.clicked.connect(self.toggle_mute)

        self.float_window_button = QPushButton()
        self.float_window_button.setStyleSheet(btnStyle)
        self.float_window_button.setIcon(QIcon('icons/popup_open.png'))
        self.float_window_button.setIconSize(QSize(50, 50))
        self.float_window_button.clicked.connect(self.show_popup)

        self.bottom_layout.addWidget(history_button)
        self.bottom_layout.addStretch()
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.mic_button)
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.text_mode_button)
        self.bottom_layout.addWidget(self.mute_button)
        self.bottom_layout.addWidget(self.float_window_button)

        # Add all sections to the main layout
        self.main_layout.addLayout(top_layout)

        # Add the chat window in the middle
        self.chat_window = ChatWindow()
        self.main_layout.addWidget(self.chat_window)

        self.main_layout.addLayout(self.bottom_layout)
        self.setLayout(self.main_layout)

        self.chat_window.message_input.hide()
        self.chat_window.send_button.hide()

        self.stacked_widget = QStackedWidget()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.stacked_widget.addWidget(self.main_widget)

        self.popup_widget = QWidget()
        popup_layout = QVBoxLayout()
        self.popup_mic_button = self.create_mic_button()
        self.popup_mic_button.clicked.connect(self.micon)
        popup_layout.addWidget(self.popup_mic_button)
        self.popup_widget.setLayout(popup_layout)
        self.stacked_widget.addWidget(self.popup_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def show_popup(self):
        self.is_popup_mode = True
        self.stacked_widget.setCurrentWidget(self.popup_widget)
        self.setGeometry(0, 0, 300, 300)  # Adjust size for popup mode
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.show()

    def show_main_interface(self):
        self.is_popup_mode = False
        self.stacked_widget.setCurrentWidget(self.main_widget)
        self.showMaximized()  # Show in full screen
        self.setWindowFlags(Qt.Window)
        self.show()

    def toggle_input_mode(self):
        global toggleMic
        # Toggle visibility of the text field and microphone button
        if self.chat_window.message_input.isVisible():
            self.chat_window.message_input.hide()
            self.chat_window.send_button.hide()
            self.mic_button.show()
            toggleMic = True
        else:
            self.chat_window.message_input.show()
            self.chat_window.send_button.show()
            self.mic_button.hide()
            toggleMic = False
            self.chat_window.add_message("Enter your Prompt:")

    def create_mic_button(self):
        global movie
        mic_size = 250
        mic_button = QPushButton(self)
        mic_button.setFixedSize(mic_size * 2, mic_size)

        mic_label = QLabel(mic_button)
        mic_label.setGeometry(0, 0, mic_size * 2, mic_size)

        
        mic_label.setMovie(movie)
        mic_label.setScaledContents(True)
        # movie.finished.connect(movie.start)
        movie.start()
        # movie.stop()
        return mic_button



    def show_popup(self):
        
        self.hide()
        self.popup.show()
    
    def eventFilter(self, obj, event):
        if obj == self.chat_window.message_input and event.type() == event.KeyPress:
            # if event.key() == Qt.Key_Return:
            #     if not toggleMic:
            #         self.chat_window.send_message()
            #     return True  # Return True to indicate the event was handled
            if event.modifiers() == Qt.ShiftModifier:
                if event.key() == Qt.Key_Return:
                    if not toggleMic:
                        self.chat_window.send_message()
                    return True  # Return True to indicate the event was handled

        return super().eventFilter(obj, event)  # Pass the event to the base class
    
    def micon(self):
        global movie
        if b.mic_off: 
            b.mic_off = False
            movie.start()
            speak("How can I help you, Sir?")
        else: 
            b.mic_off = True
            movie.stop()
            movie.jumpToFrame(0)

        

        print("b.mic_off:"+ str(b.mic_off))

    def toggle_mute(self):
        

        # Get the current mute state
        is_muted = volume.GetMute()
        if is_muted:
            self.mute_button.setIcon(QIcon('icons/unmute.png'))
        else:
            self.mute_button.setIcon(QIcon('icons/mute.png'))
            
        # Toggle the mute state
        volume.SetMute(not is_muted, None)
        print(f"Muted: {not is_muted}")

    # Toggle mute/unmute
    def sleep_(self):
        result=CustomMessageBox.show_message(self,"Are you sure you want to Sleep your pc")
        
        try:
            if result==1:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            else:
                ret= "Sleep canceled"
        except Exception as e:
            ret= f"Something Went wrong {e}"
        self.chat_window.add_message(ret)
        speak(ret)       
        
    def shutdown_(self):
        
        result =  CustomMessageBox.show_message(self,"Are you sure you want to shutdown your pc")
        
        try:
            if result==1:
                os.system("shutdown /s /t 0")
            else:
                ret= "Shutdown Cancelled"
        except Exception as e:
            ret= f"Something Went wrong {e}"
        self.chat_window.add_message(ret)
        speak(ret)
        
    def restart_(self):
        result=CustomMessageBox.show_message(self,"Are you sure you want to Resatart your pc")
        try:
            if result == 1:
                os.system("shutdown /r /t 0")
            else:
                ret= "Restart canceled"
        except Exception as e:
            ret= f"Something Went wrong {e}"
        self.chat_window.add_message(ret)
        speak(ret)


    
#     result = CustomMessageBox.show_message(self,"Welcome to NOVA\n\nNOVA is an AI assistant which can control your desktop based on your command.")



class ChatThread(QThread):
    message_received = pyqtSignal(str)
    micon = pyqtSignal()
    restart = pyqtSignal()
    shutdown = pyqtSignal()
    sleep = pyqtSignal()
    send = pyqtSignal(str)
    def send_message(self,message):
                speak("Please provide the phone number to which I should send messages.")
                number = CustomInputBox.show_input_dialog("Please provide the phone number to which I should send messages")
                while (len(number)<=9):
                    number = CustomInputBox.show_input_dialog(f"The provided phone number have only {len(number)} digits Please Enter again")
        
                
                speak("This process may take a few seconds and during this process i can't do any other work")
                now = datetime.datetime.now()
                future_time = now + datetime.timedelta(minutes=2)
                time_hour = future_time.hour
                time_minute = future_time.minute

                country_code="+91"
                number=f"{country_code}{number}"
                kit.sendwhatmsg(number, message, time_hour, time_minute)

    def __init__(self,obj):
        super().__init__()
    def run(self):
        flag = True
        global prompt
        global ret
        conversations = db.get_conversations()
        if conversations :
            for conv in conversations:
            # Get the encrypted data as a string
                encrypted_user_input = conv.to_dict().get('user_input')
                encrypted_assistant_response = conv.to_dict().get('assistant_response')
                try:
                # Decrypt the data
                    user_input = db.decrypt_data(encrypted_user_input.encode('utf-8')) if isinstance(encrypted_user_input, str) else db.decrypt_data(encrypted_user_input)
                    assistant_response = db.decrypt_data(encrypted_assistant_response.encode('utf-8')) if isinstance(encrypted_assistant_response, str) else db.decrypt_data(encrypted_assistant_response)
                    self.message_received.emit("You:"+user_input)
                    self.message_received.emit(assistant_response)
                except Exception as decryption_error:
                    print(f"Decryption error for conversation ID {conv.id}: {decryption_error}")


        # Simulate receiving a message
        wish()
        speak("How can I help you, Sir?")
        
        while True:    
            if flag:
                flag= False
                self.message_received.emit("Listening...")
            if toggleMic and not b.mic_off:
                query = takecmd().lower()
            else:
                query = prompt
            if query=="none":
                continue 
            elif toggleMic and not b.mic_off:
                self.micon.emit()
                flag =  True
                self.message_received.emit("Recognizing...")
            

            self.message_received.emit("You:"+query)
            result = input_from_gui(query,self)
            if result =="restart_": 
                self.restart.emit()
                result = "restarting your computer"

            if result =="shutdown_": 
                self.shutdown.emit()
                result = "shutdowning your computer"


            if result =="sleep_": 
                self.sleep.emit()
                result = "sleeping your computer"

            if result.__contains__("sending  message"): 
                self.send_message(result.replace("sending  message","",1))

                         
                # result = "message send" 

            self.message_received.emit(result)
            db.save_conversation(query,result)
            speak(result)
            prompt ="none"
            if result.__contains__("Goodbye! "): 
                QApplication.quit()
            time.sleep(1)         
 
            speak("Sir, Do you have any other work")
            if toggleMic:
                self.micon.emit()
            time.sleep(2)
        

    
            


if __name__ == '__main__':
    app = QApplication(sys.argv)    
    ex = NovaInterface()
    ex.show()
    chat_thread = ChatThread(ex)
    chat_thread.message_received.connect(ex.chat_window.add_message)    
    chat_thread.micon.connect(ex.micon)
    chat_thread.restart.connect(ex.restart_)
    chat_thread.shutdown.connect(ex.shutdown_)
    chat_thread.sleep.connect(ex.sleep_)
    chat_thread.start()
    sys.exit(app.exec_())
