import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from mail_sender import ModernMailSender

class ModernMailApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toplu E-posta Gönderici")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)
        
        # Modern tema uygula
        self.apply_modern_theme()
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Mail gönderici widget'ı ekle
        self.sender = ModernMailSender()
        layout.addWidget(self.sender)
    
    def apply_modern_theme(self):
        """Modern tema uygular"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Modern font ayarla (macOS uyumlu)
    font = QFont("Arial", 9)
    app.setFont(font)
    
    window = ModernMailApp()
    window.show()
    sys.exit(app.exec_()) 