import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QTabWidget, QLabel)
from PyQt5.QtCore import Qt
from mail_sender import MailSenderApp
from mail_viewer import EmailViewer

class MailApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("E-posta Uygulaması")
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Sekme widget'ı oluştur
        self.tabs = QTabWidget()
        
        # E-posta görüntüleyici sekmesi
        self.viewer = EmailViewer()
        self.tabs.addTab(self.viewer, "E-postaları Görüntüle")
        
        # E-posta gönderici sekmesi
        self.sender = MailSenderApp()
        self.tabs.addTab(self.sender, "E-posta Gönder")
        
        # Sekmeleri ana layout'a ekle
        layout.addWidget(self.tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MailApp()
    window.show()
    sys.exit(app.exec_()) 