import sys,time
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QTextEdit, QGridLayout
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon

# subprocess.run(["python","backend.py"])
BtnTextFont ='30px'
host = '127.0.0.1'  # The server's hostname or IP address
port = 65432        # The port used by the server

class SocketThread(QThread):
    new_message = pyqtSignal(str)  # Signal to emit when a new message is received
    
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            while True:
                try:
                    data = s.recv(1024).decode('utf-8')
                    if data:
                        self.new_message.emit(data)
                except Exception as e:
                    print(f"Error: {e}")
                    break

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
        input_layout = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setFixedHeight(50)
        input_layout.addWidget(self.message_input)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

        # Styling
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: white;
                font-size: 20px;
                border: none;
            }
            QTextEdit, QPushButton {
                font-size: 20px;
            }
        """)

        # Start the socket thread
        self.socket_thread = SocketThread()
        self.socket_thread.new_message.connect(self.add_message)
        self.socket_thread.start()

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
        if  message.startswith("You:"):is_sent = True
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

        if is_sent :
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

        self.start_socket_thread()
        

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


    def start_socket_thread(self):
        # Start the socket communication in a separate thread
        self.socket_thread = SocketThread()
        self.socket_thread.new_message.connect(self.on_new_message)  # Connect signal to a slot
        self.socket_thread.start()

    def on_new_message(self, message):
        # Add received messages to the chat window
        self.chat_window.add_message(message,is_sent=True )


if __name__ == '__main__':    
    app = QApplication(sys.argv)
    ex = NovaInterface()
    ex.show()
    sys.exit(app.exec_())
    
   
# ms="djjkf"
# ms.startswith("You:")