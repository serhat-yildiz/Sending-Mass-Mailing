# -*- coding: utf-8 -*-
import sys
import os
import smtplib
import time
import html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.header import Header
from email.utils import formataddr
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QPushButton, QFileDialog, QMessageBox, 
    QProgressBar, QFrame, QGridLayout, QScrollArea,
    QApplication, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon
from dotenv import load_dotenv

class EmailSendingThread(QThread):
    """E-posta gönderme işlemini arka planda yapar"""
    progress_updated = pyqtSignal(int, str)
    finished_signal = pyqtSignal(int, int, str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, email, password, recipients, subject, content, cv_path=None, is_html=False):
        super().__init__()
        self.email = email
        self.password = password
        self.recipients = recipients
        self.subject = subject
        self.content = content
        self.cv_path = cv_path
        self.is_html = is_html
        self.is_cancelled = False
    
    def cancel(self):
        self.is_cancelled = True
    
    def run(self):
        successful_sends = 0
        failed_sends = 0
        error_message = ""
        
        try:
            # Gmail SMTP sunucusuna bağlan
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            # Kimlik doğrulama
            server.login(self.email, self.password)
            
            for i, recipient in enumerate(self.recipients):
                if self.is_cancelled:
                    break
                
                try:
                    # Her 10 e-postada bir 1 dakika bekle (rate limiting)
                    if i > 0 and i % 10 == 0:
                        for j in range(60):
                            if self.is_cancelled:
                                break
                            time.sleep(1)
                    
                    # HTML formatında mesaj oluştur
                    msg = MIMEMultipart()
                    msg['From'] = formataddr(('Gönderen', self.email))
                    msg['To'] = recipient
                    msg['Subject'] = self.subject
                    
                    # HTML içeriği aynen kullan
                    html_content = self.content
                    
                    text_part = MIMEText(html_content, 'html', 'utf-8')
                    msg.attach(text_part)
                    
                    # CV dosyası varsa ekle
                    if self.cv_path and os.path.exists(self.cv_path):
                        with open(self.cv_path, 'rb') as f:
                            cv_part = MIMEApplication(f.read(), _subtype='pdf')
                            cv_part.add_header('Content-Disposition', 'attachment', 
                                                   filename=os.path.basename(self.cv_path))
                            msg.attach(cv_part)
                    
                    # Maili gönder
                    server.sendmail(self.email, recipient, msg.as_string())
                    successful_sends += 1
                    
                    # Progress güncelle
                    self.progress_updated.emit(i + 1, f"Sent: {recipient}")
                    
                except Exception as e:
                    failed_sends += 1
                    error_message += f"Error ({recipient}): {str(e)}\n"
                    continue
            
            server.quit()
            self.finished_signal.emit(successful_sends, failed_sends, error_message)
            
        except smtplib.SMTPAuthenticationError:
            self.error_signal.emit("Authentication error! Please check your email or app password.")
        except Exception as e:
            self.error_signal.emit(f"Connection error: {str(e)}")
    
    def text_to_html(self, text):
        """Metni HTML formatına çevirir, satır sonlarını ve boşlukları korur"""
        # HTML karakterlerini escape et
        escaped_text = html.escape(text)
        
        # Satır sonlarını <br> ile değiştir
        html_text = escaped_text.replace('\n', '<br>\n')
        
        # Çoklu boşlukları korumak için &nbsp; kullan
        import re
        # 2 veya daha fazla boşluğu &nbsp; ile değiştir
        html_text = re.sub(r' {2,}', lambda m: '&nbsp;' * len(m.group()), html_text)
        
        # Tab karakterlerini 4 boşlukla değiştir
        html_text = html_text.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        
        # HTML yapısı ile sarmayla
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            font-size: 14px;
            line-height: 1.8;
            color: #333;
            margin: 20px;
            background-color: #ffffff;
        }}
        .content {{
            white-space: pre-wrap;
            word-wrap: break-word;
            max-width: 100%;
        }}
        p {{
            margin: 0 0 10px 0;
        }}
        .signature {{
            margin-top: 20px;
            border-top: 1px solid #eee;
            padding-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="content">{html_text}</div>
</body>
</html>"""
        
        return html_content
    
    def process_html_content(self, content):
        """HTML içeriğini işler"""
        # Eğer tam HTML yapısı yoksa, temel yapıyı ekle
        if '<html>' not in content.lower() and '<body>' not in content.lower():
            processed_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            margin: 20px;
            background-color: #ffffff;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>"""
        else:
            processed_html = content
        
        return processed_html

class ModernMailSender(QWidget):
    def __init__(self):
        super().__init__()
        self.cv_path = None
        self.email_thread = None
        self.content_mode = 'html'  # Sadece HTML modu
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Creates modern UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Compact Header
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 10)
        header_layout.setSpacing(5)
        
        service_title = QLabel("Professional HTML Email Service")
        service_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 12px 0;
                margin: 0;
                text-align: center;
            }
        """)
        service_title.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(service_title)
        
        main_layout.addWidget(header_widget)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)
        
        # Gmail settings section
        gmail_frame = self.create_section_frame("Gmail Settings")
        gmail_layout = QGridLayout()
        
        # Email address
        email_label = QLabel("Your Gmail Address:")
        email_label.setStyleSheet("color: #2c3e50; background-color: transparent;")
        gmail_layout.addWidget(email_label, 0, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@gmail.com")
        self.style_input(self.email_input)
        gmail_layout.addWidget(self.email_input, 0, 1)
        
        # App password
        password_label = QLabel("Your App Password:")
        password_label.setStyleSheet("color: #2c3e50; background-color: transparent;")
        gmail_layout.addWidget(password_label, 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Your 16-digit app password")
        self.style_input(self.password_input)
        gmail_layout.addWidget(self.password_input, 1, 1)
        
        # Help button
        help_btn = QPushButton("How to Get App Password?")
        help_btn.clicked.connect(self.show_help)
        self.style_button(help_btn, "#3498db")
        gmail_layout.addWidget(help_btn, 2, 0, 1, 2)
        
        gmail_frame.setLayout(gmail_layout)
        content_layout.addWidget(gmail_frame)
        
        # Recipients list section
        recipients_frame = self.create_section_frame("Recipients List")
        recipients_layout = QVBoxLayout()
        
        recipients_label = QLabel("Email addresses (one per line):")
        recipients_label.setStyleSheet("color: #2c3e50; background-color: transparent;")
        recipients_layout.addWidget(recipients_label)
        
        self.recipients_input = QTextEdit()
        self.recipients_input.setPlaceholderText("example1@gmail.com\nexample2@gmail.com\nexample3@gmail.com")
        self.recipients_input.setMaximumHeight(120)
        self.style_text_input(self.recipients_input)
        recipients_layout.addWidget(self.recipients_input)
        
        recipients_frame.setLayout(recipients_layout)
        content_layout.addWidget(recipients_frame)
        
        # Email content section
        content_frame = self.create_section_frame("Email Content")
        content_mail_layout = QVBoxLayout()
        
        # Subject
        subject_layout = QHBoxLayout()
        subject_label = QLabel("Subject:")
        subject_label.setStyleSheet("color: #2c3e50; background-color: transparent;")
        subject_layout.addWidget(subject_label)
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter your email subject here")
        self.style_input(self.subject_input)
        subject_layout.addWidget(self.subject_input)
        content_mail_layout.addLayout(subject_layout)
        
        # Service Info Panel
        info_panel = QWidget()
        info_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 5px 0;
            }
        """)
        info_layout = QHBoxLayout(info_panel)
        info_layout.setContentsMargins(15, 12, 15, 12)
        
        # Service Icon
        service_icon = QLabel("🚀")
        service_icon.setStyleSheet("font-size: 20px; margin-right: 10px;")
        
        # Service Message
        service_msg = QLabel("Ready to send professional HTML emails to multiple recipients")
        service_msg.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #495057;
                font-weight: 500;
                background: transparent;
            }
        """)
        
        info_layout.addWidget(service_icon)
        info_layout.addWidget(service_msg)
        info_layout.addStretch()
        
        content_mail_layout.addWidget(info_panel)
        
        # HTML Template area
        content_input_label = QLabel("Your HTML Email Template:")
        content_input_label.setStyleSheet("color: #2c3e50; background-color: transparent; font-weight: bold;")
        content_mail_layout.addWidget(content_input_label)
        
        self.content_input = QTextEdit()
        self.content_input.setMinimumHeight(300)
        self.content_input.setAcceptRichText(False)  # Accept only plain text
        self.content_input.setLineWrapMode(QTextEdit.WidgetWidth)  # Word wrapping
        self.content_input.setPlaceholderText(self.get_html_placeholder())
        self.style_html_input(self.content_input)
        content_mail_layout.addWidget(self.content_input)
        
        # Usage instructions
        instructions_frame = self.create_instructions_frame()
        content_mail_layout.addWidget(instructions_frame)
        

        
        content_frame.setLayout(content_mail_layout)
        content_layout.addWidget(content_frame)
        
        # CV attachment section
        cv_frame = self.create_section_frame("CV Attachment (Optional)")
        cv_layout = QHBoxLayout()
        
        self.cv_label = QLabel("No CV selected")
        cv_layout.addWidget(self.cv_label)
        
        cv_btn = QPushButton("Select CV")
        cv_btn.clicked.connect(self.select_cv)
        self.style_button(cv_btn, "#9b59b6")
        cv_layout.addWidget(cv_btn)
        
        cv_clear_btn = QPushButton("Remove CV")
        cv_clear_btn.clicked.connect(self.clear_cv)
        self.style_button(cv_clear_btn, "#e74c3c")
        cv_layout.addWidget(cv_clear_btn)
        
        cv_frame.setLayout(cv_layout)
        content_layout.addWidget(cv_frame)
        
        # Sending section
        send_frame = self.create_section_frame("Sending")
        send_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 6px;
            }
        """)
        send_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        send_layout.addWidget(self.status_label)
        
        # Send button
        self.send_btn = QPushButton("🚀 Deploy Email Campaign")
        self.send_btn.clicked.connect(self.send_emails)
        self.send_btn.setMinimumHeight(50)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        send_layout.addWidget(self.send_btn)
        
        # İptal butonu
        self.cancel_btn = QPushButton("İptal Et")
        self.cancel_btn.clicked.connect(self.cancel_sending)
        self.cancel_btn.setVisible(False)
        self.style_button(self.cancel_btn, "#e74c3c")
        send_layout.addWidget(self.cancel_btn)
        
        send_frame.setLayout(send_layout)
        content_layout.addWidget(send_frame)
        
        # Spacer ekle
        content_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Scroll area'ya ekle
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
    
    def create_section_frame(self, title):
        """Creates section frame"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setFrameShadow(QFrame.Raised)
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                padding: 15px;
            }
            QFrame QLabel {
                color: #2c3e50;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        
        # Başlık ekle
        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 10px;
                border: none;
                background-color: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        return frame
    
    def style_input(self, widget):
        """Styles input fields"""
        widget.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: white;
                color: #2c3e50;
            }
        """)
    
    def style_text_input(self, widget):
        """Text input alanlarını stillendirir"""
        widget.setStyleSheet("""
            QTextEdit {
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8f9fa;
                color: #2c3e50;
                font-family: 'Courier New', 'Monaco', monospace;
                line-height: 1.5;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QTextEdit:focus {
                border-color: #3498db;
                background-color: white;
                color: #2c3e50;
            }
        """)
    
    def style_button(self, button, color):
        """Butonları stillendirir"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.2)};
            }}
        """)
    
    def darken_color(self, color, factor=0.1):
        """Rengi koyulaştırır"""
        color_map = {
            "#3498db": "#2980b9",
            "#9b59b6": "#8e44ad", 
            "#e74c3c": "#c0392b",
            "#27ae60": "#229954",
            "#f39c12": "#e67e22",
            "#e67e22": "#d35400",
            "#95a5a6": "#7f8c8d"
        }
        return color_map.get(color, color)
    
    def show_help(self):
        """Yardım mesajını gösterir"""
        QMessageBox.information(self, "Uygulama Şifresi Yardımı", 
            "Gmail için uygulama şifresi oluşturmak için:\n\n"
            "1. https://myaccount.google.com/security adresine gidin\n"
            "2. '2 Adımlı Doğrulama'yı etkinleştirin\n"
            "3. 'Uygulama Şifreleri'ne gidin\n"
            "4. 'Uygulama Seç' > 'Diğer' > 'Mail Uygulaması'\n"
            "5. Oluşturulan 16 haneli şifreyi kopyalayın\n\n"
            "Not: Normal Gmail şifrenizi DEĞİL, özel uygulama şifresini kullanmalısınız!")

    def select_cv(self):
        """CV dosyası seçer"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "CV Dosyası Seç", "", "PDF Dosyalar (*.pdf)")
        
        if file_path:
            self.cv_path = file_path
            self.cv_label.setText(f"CV: {os.path.basename(file_path)}")
            self.cv_label.setStyleSheet("color: #27ae60; font-weight: bold;")
    
    def clear_cv(self):
        """CV dosyasını kaldırır"""
        self.cv_path = None
        self.cv_label.setText("No CV selected")
        self.cv_label.setStyleSheet("color: #7f8c8d;")
    
    def get_html_placeholder(self):
        """Returns HTML placeholder text"""
        return """📧 MailCraft Pro - HTML Email Editor

Paste your professional HTML email template here...

<!-- ENTERPRISE EMAIL TEMPLATE STRUCTURE -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Email</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="color: #2c3e50;">Your Professional Message</h1>
        <p style="line-height: 1.6;">Your content goes here...</p>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0; color: #6c757d;">Important information or call-to-action</p>
        </div>
        
        <p style="color: #6c757d; font-size: 12px;">
            Best regards,<br>Your Company
        </p>
    </div>
</body>
</html>

🔒 SECURE DELIVERY: Templates are transmitted via encrypted SMTP
⚡ INSTANT SENDING: Bulk email delivery to multiple recipients
📊 ENTERPRISE READY: Professional email marketing solution"""
    
    def style_html_input(self, widget):
        """HTML input alanını stillendirir"""
        widget.setStyleSheet("""
            QTextEdit {
                padding: 15px;
                border: 2px solid #3498db;
                border-radius: 8px;
                font-size: 12px;
                background-color: #f8f9fa;
                color: #2c3e50;
                font-family: 'Courier New', 'Monaco', monospace;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #e67e22;
                background-color: white;
            }
        """)
    
    def create_instructions_frame(self):
        """Creates usage instructions frame"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setFrameShadow(QFrame.Raised)
        frame.setStyleSheet("""
            QFrame {
                background-color: #e8f4fd;
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Title
        title = QLabel("📋 MailCraft Pro Service Guide")
        title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("""
🔧 How to use MailCraft Pro:

1. 📝 Paste your HTML template in the editor above
2. 📧 Configure recipients and email subject  
3. 🚀 Send to multiple recipients instantly

⚠️ ENTERPRISE GRADE: Your HTML is transmitted exactly as provided
🔒 SECURE: All communications use encrypted SMTP protocols
        """)
        instructions.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 12px;
                line-height: 1.6;
                background-color: transparent;
            }
        """)
        layout.addWidget(instructions)
        
        return frame
    

    

    

    

    


    def send_emails(self):
        """Starts email sending process"""
        # Input validation
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        recipients_text = self.recipients_input.toPlainText().strip()
        subject = self.subject_input.text().strip()
        content = self.content_input.toPlainText().strip()
        
        if not all([email, password, recipients_text, subject, content]):
            QMessageBox.warning(self, "Missing Information", 
                "Please fill in all required fields!")
            return
        
        # Extract email addresses
        recipients = [line.strip() for line in recipients_text.split('\n') 
                     if line.strip() and '@' in line]
        
        if not recipients:
            QMessageBox.warning(self, "Recipients Error", 
                "No valid email addresses found!")
            return
        
        # Ask for confirmation
        reply = QMessageBox.question(self, "Confirmation", 
            f"Are you sure you want to send emails to {len(recipients)} people?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.No:
            return
        
        # Update UI
        self.send_btn.setEnabled(False)
        self.cancel_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(recipients))
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing email campaign...")
        
        # Start thread (always HTML mode)
        self.email_thread = EmailSendingThread(
            email, password, recipients, subject, content, self.cv_path, True)
        self.email_thread.progress_updated.connect(self.update_progress)
        self.email_thread.finished_signal.connect(self.sending_finished)
        self.email_thread.error_signal.connect(self.sending_error)
        self.email_thread.start()
    
    def cancel_sending(self):
        """Cancels email sending"""
        if self.email_thread:
            self.email_thread.cancel()
        self.reset_ui()
    
    def update_progress(self, value, status):
        """Updates progress bar"""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
    
    def sending_finished(self, successful, failed, error_msg):
        """Called when sending is completed"""
        self.reset_ui()
        
        if failed == 0:
            QMessageBox.information(self, "Success", 
                f"All emails sent successfully! ({successful} emails)")
        else:
            QMessageBox.warning(self, "Partial Success", 
                f"Sending result:\n"
                f"✅ Successful: {successful} emails\n"
                f"❌ Failed: {failed} emails\n\n"
                f"Error details:\n{error_msg[:500]}{'...' if len(error_msg) > 500 else ''}")
    
    def sending_error(self, error_msg):
        """Called when sending error occurs"""
        self.reset_ui()
        QMessageBox.critical(self, "Error", f"An error occurred while sending emails:\n\n{error_msg}")
    
    def reset_ui(self):
        """Resets UI to initial state"""
        self.send_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("")
    
    def load_settings(self):
        """Ayarları yükler"""
        load_dotenv()
        saved_email = os.getenv('EMAIL', '')
        saved_password = os.getenv('PASSWORD', '')
        
        if saved_email:
            self.email_input.setText(saved_email)
        if saved_password:
            self.password_input.setText(saved_password)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Modern font ayarla (macOS uyumlu)
    font = QFont("Arial", 9)
    app.setFont(font)
    
    window = ModernMailSender()
    window.show()
    sys.exit(app.exec_()) 