import sys, time
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QTextEdit, QGridLayout
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from backend import *
import backend as b
BtnTextFont = '30px'
toggleMic = True
prompt = "none"
output_buffer = io.StringIO()
class process():
    def __init__(self):
        pass
        
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
        global prompt        
        # This method is kept for potential future use
        message = self.message_input.toPlainText().strip()
        if message:
            prompt=message
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
    def __init__(self):
        super().__init__()
        self.initUI()
        
        

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
        self.mic_button.setStyleSheet("""background-color: #0088ff; border-radius: 50px;""")
        self.mic_button.clicked.connect(self.micon)

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
        self.chat_window = ChatWindow()
        self.main_layout.addWidget(self.chat_window)

        self.main_layout.addLayout(self.bottom_layout)

        self.setLayout(self.main_layout)
        self.chat_window.message_input.hide()
        self.chat_window.send_button.hide()

    def toggle_input_mode(self):
        global toggleMic
        # Toggle visibility of the text field and microphone button
        if self.chat_window.message_input.isVisible():
            self.chat_window.message_input.hide()
            self.chat_window.send_button.hide()
            self.mic_button.show()
            toggleMic=True
        else:
            self.chat_window.message_input.show()
            self.chat_window.send_button.show()
            self.mic_button.hide()
            toggleMic=False
     
    def micon(self):
        if b.mic_off: 
            b.mic_off = False
            speak("How can I help you, Sir?")
            self.mic_button.setIcon(QIcon('icons/mic.png'))
            self.mic_button.setIconSize(QSize(100, 100))  

        else: 
            b.mic_off = True
            self.mic_button.setIcon(QIcon('icons/mic_off.png'))
            self.mic_button.setIconSize(QSize(30, 30))
        print("b.mic_off:"+ str(b.mic_off))

            

   
    def on_new_message(self, message):
        self.chat_window.add_message(message, is_sent=True)

class ChatThread(QThread):
    message_received = pyqtSignal(str)
    def __init__(self):
        super().__init__()

    def run(self):
        global prompt
        # Simulate receiving a message
        time.sleep(1)
        wish()
        speak("How can I help you, Sir?")
        if toggleMic:
         self.message_received.emit("Listening...")
        else:
         self.message_received.emit("Enter your query: ")
        while True:    
            if toggleMic and not b.mic_off:
                query = takecmd().lower()
            else:
                query = prompt
            if query=="none":
                continue 
            elif toggleMic and not b.mic_off:
                self.message_received.emit("Recognizing...") 
            self.message_received.emit("You:"+query)
            result = microphone(query)        
            self.message_received.emit(result)
            speak(result)
            prompt ="none"
            time.sleep(1)
            speak("Sir, Do you have any other work")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NovaInterface()
    ex.show()
    chat_thread = ChatThread()
    chat_thread.message_received.connect(ex.chat_window.add_message)
    chat_thread.start()
    sys.exit(app.exec_())

