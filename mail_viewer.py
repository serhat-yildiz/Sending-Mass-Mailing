import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import (QWidget, QVBoxLayout,
                           QHBoxLayout, QListWidget, QTextEdit, QPushButton,
                           QLabel, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt

class EmailViewer(QWidget):
    def __init__(self):
        super().__init__()
        
        # Ana layout
        layout = QHBoxLayout(self)
        
        # Sol panel (e-posta listesi)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # E-posta listesi
        self.email_list = QListWidget()
        self.email_list.itemClicked.connect(self.show_email_content)
        left_layout.addWidget(QLabel("E-postalar:"))
        left_layout.addWidget(self.email_list)
        
        # Sağ panel (e-posta içeriği)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # E-posta içeriği
        self.email_content = QTextEdit()
        self.email_content.setReadOnly(True)
        right_layout.addWidget(QLabel("E-posta İçeriği:"))
        right_layout.addWidget(self.email_content)
        
        # Layout'a panelleri ekle
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        
        # E-posta bağlantı bilgileri
        self.email = ""
        self.password = ""
        self.imap_server = ""
        
        # Bağlantı ayarları
        self.setup_connection()
        
    def setup_connection(self):
        load_dotenv()
        
        # Gmail için varsayılan ayarlar
        self.imap_server = "imap.gmail.com"
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        
        if not all([self.email, self.password]):
            self.show_settings_dialog()
        else:
            self.fetch_emails()
    
    def show_settings_dialog(self):
        dialog = QWidget()
        dialog.setWindowTitle("E-posta Ayarları")
        layout = QVBoxLayout(dialog)
        
        # E-posta adresi
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("E-posta:"))
        email_input = QLineEdit()
        email_input.setText(self.email)
        email_layout.addWidget(email_input)
        layout.addLayout(email_layout)
        
        # Şifre
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Şifre:"))
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setText(self.password)
        password_layout.addWidget(password_input)
        layout.addLayout(password_layout)
        
        # Sunucu
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel("IMAP Sunucu:"))
        server_input = QLineEdit()
        server_input.setText(self.imap_server)
        server_layout.addWidget(server_input)
        layout.addLayout(server_layout)
        
        # Kaydet butonu
        save_button = QPushButton("Kaydet")
        save_button.clicked.connect(lambda: self.save_settings(
            email_input.text(),
            password_input.text(),
            server_input.text(),
            dialog
        ))
        layout.addWidget(save_button)
        
        dialog.setLayout(layout)
        dialog.show()
    
    def save_settings(self, email, password, server, dialog):
        self.email = email
        self.password = password
        self.imap_server = server
        dialog.close()
        self.fetch_emails()
    
    def fetch_emails(self):
        try:
            # IMAP sunucusuna bağlan
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email, self.password)
            
            # Gelen kutusunu seç
            mail.select("inbox")
            
            # Tüm e-postaları al
            _, messages = mail.search(None, "ALL")
            
            # E-posta listesini temizle
            self.email_list.clear()
            
            # Her e-postayı işle
            for num in messages[0].split():
                _, msg = mail.fetch(num, "(RFC822)")
                email_body = msg[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Konu ve gönderen bilgilerini al
                subject = decode_header(email_message["subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                sender = decode_header(email_message["from"])[0][0]
                if isinstance(sender, bytes):
                    sender = sender.decode()
                
                # Listeye ekle
                self.email_list.addItem(f"{sender} - {subject}")
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"E-postalar alınırken bir hata oluştu: {str(e)}")
    
    def show_email_content(self, item):
        try:
            # IMAP sunucusuna bağlan
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email, self.password)
            
            # Gelen kutusunu seç
            mail.select("inbox")
            
            # Tüm e-postaları al
            _, messages = mail.search(None, "ALL")
            
            # Seçilen e-postayı bul
            selected_index = self.email_list.row(item)
            message_num = messages[0].split()[selected_index]
            
            # E-postayı al
            _, msg = mail.fetch(message_num, "(RFC822)")
            email_body = msg[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # E-posta içeriğini oluştur
            content = f"Gönderen: {email_message['from']}\n"
            content += f"Alıcı: {email_message['to']}\n"
            content += f"Konu: {email_message['subject']}\n"
            content += f"Tarih: {email_message['date']}\n\n"
            
            # E-posta gövdesini al
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        content += body
            else:
                body = email_message.get_payload(decode=True).decode()
                content += body
            
            # İçeriği göster
            self.email_content.setText(content)
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"E-posta içeriği alınırken bir hata oluştu: {str(e)}") 