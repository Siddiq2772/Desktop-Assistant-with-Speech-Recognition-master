# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
# from PyQt5.QtGui import QMovie

# class MyWindow(QWidget):
#     def __init__(self):
#         super().__init__()

#         # Create a button
#         self.mic_button = QPushButton(self)
#         self.mic_button.setFixedSize(200, 200)  # Set the size of the button

#         # Create a QLabel to hold the GIF
#         self.mic_label = QLabel(self.mic_button)
#         self.mic_label.setGeometry(0, 0, 200, 200)  # Position the label inside the button

#         # Load the GIF
#         self.movie = QMovie("icons/mic_ani.gif")
#         self.mic_label.setMovie(self.movie)
#         self.mic_label.setScaledContents(True)
#         self.movie.start()

#         # Set up the layout
#         layout = QVBoxLayout()
#         layout.addWidget(self.mic_button)
        
#         self.setLayout(layout)
#         self.setWindowTitle('PyQt5 Button with GIF')
#         self.setGeometry(100, 100, 300, 300)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = MyWindow()
#     window.show()
#     sys.exit(app.exec_())



import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

class PopupWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Pop-up Window')
        self.setGeometry(0, 0, 300, 300)  # Set position to top-left corner
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)  # Remove minimize and maximize buttons

        layout = QVBoxLayout()
        btn = QPushButton('Show Main Window', self)
        btn.clicked.connect(self.show_main_window)
        layout.addWidget(btn)

        self.setLayout(layout)

    def show_main_window(self):
        self.hide()
        self.main_window.showMaximized()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 400, 300)

        btn = QPushButton('Show Pop-up', self)
        btn.move(150, 130)
        btn.clicked.connect(self.show_popup)

        self.popup = PopupWindow(self)

    def show_popup(self):
        self.hide()
        self.popup.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())