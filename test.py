import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtGui import QMovie

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create a button
        self.mic_button = QPushButton(self)
        self.mic_button.setFixedSize(200, 200)  # Set the size of the button

        # Create a QLabel to hold the GIF
        self.mic_label = QLabel(self.mic_button)
        self.mic_label.setGeometry(0, 0, 200, 200)  # Position the label inside the button

        # Load the GIF
        self.movie = QMovie("icons/mic_ani.gif")
        self.mic_label.setMovie(self.movie)
        self.mic_label.setScaledContents(True)
        self.movie.start()

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.mic_button)
        
        self.setLayout(layout)
        self.setWindowTitle('PyQt5 Button with GIF')
        self.setGeometry(100, 100, 300, 300)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
