# -*- coding: utf-8 -*-
import sys
import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
from email.utils import formataddr
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
                            QPushButton, QFileDialog, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt
from dotenv import load_dotenv

class MailSenderApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Ana layout
        layout = QVBoxLayout(self)
        
        # E-posta ayarları
        email_layout = QHBoxLayout()
        email_label = QLabel("Gmail Adresiniz:")
        self.email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)
        
        # Şifre ayarları
        password_layout = QHBoxLayout()
        password_label = QLabel("Uygulama Şifreniz:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Alıcı listesi
        recipients_label = QLabel("Alıcı Listesi (Her satıra bir e-posta):")
        self.recipients_input = QTextEdit()
        layout.addWidget(recipients_label)
        layout.addWidget(self.recipients_input)
        
        # Konu
        subject_layout = QHBoxLayout()
        subject_label = QLabel("Mail Konusu:")
        self.subject_input = QLineEdit()
        subject_layout.addWidget(subject_label)
        subject_layout.addWidget(self.subject_input)
        layout.addLayout(subject_layout)
        
        # Mail içeriği
        content_label = QLabel("Mail İçeriği:")
        self.content_input = QTextEdit()
        layout.addWidget(content_label)
        layout.addWidget(self.content_input)
        
        # CV ekleme
        cv_layout = QHBoxLayout()
        self.cv_path = ""
        cv_button = QPushButton("CV Seç")
        cv_button.clicked.connect(self.select_cv)
        cv_layout.addWidget(cv_button)
        layout.addLayout(cv_layout)
        
        # Gönder butonu
        send_button = QPushButton("Mailleri Gönder")
        send_button.clicked.connect(self.send_emails)
        layout.addWidget(send_button)
        
        # İlerleme çubuğu
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Durum mesajı
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    def select_cv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "CV Seç", "", "PDF Dosyaları (*.pdf);;Tüm Dosyalar (*)")
        if file_name:
            self.cv_path = file_name
            self.status_label.setText(f"Seçilen CV: {os.path.basename(file_name)}")

    def send_emails(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        recipients = [r.strip() for r in self.recipients_input.toPlainText().split('\n') if r.strip()]
        subject = self.subject_input.text().strip()
        content = self.content_input.toPlainText().strip()
        
        if not all([email, password, recipients, subject, content]):
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
            return
        
        if len(recipients) > 50:
            reply = QMessageBox.question(self, "Uyarı", 
                "Çok sayıda alıcı var. Gmail günlük gönderim limiti nedeniyle bazı e-postalar engellenebilir.\n"
                "Devam etmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        self.progress_bar.setMaximum(len(recipients))
        self.progress_bar.setValue(0)
        
        try:
            # Gmail SMTP sunucusuna bağlan
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            # Kimlik doğrulama
            try:
                server.login(email, password)
            except smtplib.SMTPAuthenticationError as e:
                QMessageBox.critical(self, "Kimlik Doğrulama Hatası", 
                    "E-posta veya uygulama şifresi hatalı!\n\n"
                    "Gmail için uygulama şifresi oluşturmak için:\n"
                    "1. https://myaccount.google.com/security adresine gidin\n"
                    "2. '2 Adımlı Doğrulama'yı etkinleştirin\n"
                    "3. 'Uygulama Şifreleri'ne gidin\n"
                    "4. 'Uygulama Seç' > 'Diğer' > 'Mail Uygulaması'\n"
                    "5. Oluşturulan 16 haneli şifreyi kopyalayın")
                return
            
            successful_sends = 0
            failed_sends = 0
            
            for i, recipient in enumerate(recipients):
                try:
                    # Her 10 e-postada bir 1 dakika bekle
                    if i > 0 and i % 10 == 0:
                        time.sleep(60)
                    
                    # Yeni mesaj oluştur
                    msg = MIMEMultipart()
                    
                    # Gönderen ve alıcı bilgilerini ayarla
                    msg['From'] = formataddr(('Gönderen', email))
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    
                    # Mail içeriğini ekle
                    text_part = MIMEText(content.encode('utf-8'), 'plain', 'utf-8')
                    msg.attach(text_part)
                    
                    # CV'yi ekle
                    if self.cv_path:
                        with open(self.cv_path, 'rb') as f:
                            cv_attachment = MIMEApplication(f.read(), _subtype='pdf')
                            cv_attachment.add_header('Content-Disposition', 'attachment', 
                                                   filename=os.path.basename(self.cv_path))
                            msg.attach(cv_attachment)
                    
                    # Maili gönder
                    server.sendmail(email, recipient, msg.as_string())
                    
                    successful_sends += 1
                    
                    # İlerleme çubuğunu güncelle
                    self.progress_bar.setValue(i + 1)
                    self.status_label.setText(f"Gönderilen: {recipient}")
                    QApplication.processEvents()
                    
                except Exception as e:
                    print(f"Mail gönderilirken hata: {str(e)}")
                    failed_sends += 1
                    continue
            
            server.quit()
            
            # Sonuç mesajı
            if failed_sends == 0:
                QMessageBox.information(self, "Başarılı", f"Tüm mailler başarıyla gönderildi! ({successful_sends} adet)")
            else:
                QMessageBox.warning(self, "Kısmi Başarı", 
                    f"Toplam {len(recipients)} e-postadan:\n"
                    f"- {successful_sends} adet başarıyla gönderildi\n"
                    f"- {failed_sends} adet gönderilemedi\n\n"
                    "Gönderilemeyen e-postalar için Gmail'in günlük gönderim limitini aşmış olabilirsiniz.")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", 
                f"Mail gönderilirken bir hata oluştu: {str(e)}\n\n"
                "Lütfen şunları kontrol edin:\n"
                "1. İnternet bağlantınızın olduğundan emin olun\n"
                "2. Gmail adresinizin doğru olduğundan emin olun\n"
                "3. Uygulama şifrenizin doğru olduğundan emin olun\n"
                "4. Gmail hesabınızda 2 Adımlı Doğrulama'nın açık olduğundan emin olun")
        
        finally:
            self.progress_bar.setValue(0)
            self.status_label.setText("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MailSenderApp()
    window.show()
    sys.exit(app.exec_()) 