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
    
    def __init__(self, email, password, recipients, subject, content, cv_path=None):
        super().__init__()
        self.email = email
        self.password = password
        self.recipients = recipients
        self.subject = subject
        self.content = content
        self.cv_path = cv_path
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
                    
                    # Metin içeriğini HTML formatına çevir
                    html_content = self.text_to_html(self.content)
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
                    self.progress_updated.emit(i + 1, f"Gönderildi: {recipient}")
                    
                except Exception as e:
                    failed_sends += 1
                    error_message += f"Hata ({recipient}): {str(e)}\n"
                    continue
            
            server.quit()
            self.finished_signal.emit(successful_sends, failed_sends, error_message)
            
        except smtplib.SMTPAuthenticationError:
            self.error_signal.emit("Kimlik doğrulama hatası! E-posta veya uygulama şifrenizi kontrol edin.")
        except Exception as e:
            self.error_signal.emit(f"Bağlantı hatası: {str(e)}")
    
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

class ModernMailSender(QWidget):
    def __init__(self):
        super().__init__()
        self.cv_path = None
        self.email_thread = None
        self.content_history = []  # Metin geçmişi için
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Modern UI oluşturur"""
        # Ana layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Başlık
        title_label = QLabel("Toplu E-posta Gönderici")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Scroll area oluştur
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Ana içerik widget'ı
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)
        
        # Gmail ayarları bölümü
        gmail_frame = self.create_section_frame("Gmail Ayarları")
        gmail_layout = QGridLayout()
        
        # E-posta adresi
        email_label = QLabel("Gmail Adresiniz:")
        email_label.setStyleSheet("color: #2c3e50; background-color: transparent;")
        gmail_layout.addWidget(email_label, 0, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ornek@gmail.com")
        self.style_input(self.email_input)
        gmail_layout.addWidget(self.email_input, 0, 1)
        
        # Uygulama şifresi
        password_label = QLabel("Uygulama Şifreniz:")
        password_label.setStyleSheet("color: #2c3e50; background-color: transparent;")
        gmail_layout.addWidget(password_label, 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("16 haneli uygulama şifreniz")
        self.style_input(self.password_input)
        gmail_layout.addWidget(self.password_input, 1, 1)
        
        # Yardım butonu
        help_btn = QPushButton("Uygulama Şifresi Nasıl Alınır?")
        help_btn.clicked.connect(self.show_help)
        self.style_button(help_btn, "#3498db")
        gmail_layout.addWidget(help_btn, 2, 0, 1, 2)
        
        gmail_frame.setLayout(gmail_layout)
        content_layout.addWidget(gmail_frame)
        
        # Alıcı listesi bölümü
        recipients_frame = self.create_section_frame("Alıcı Listesi")
        recipients_layout = QVBoxLayout()
        
        recipients_label = QLabel("E-posta adresleri (her satıra bir adres):")
        recipients_label.setStyleSheet("color: #2c3e50; background-color: transparent;")
        recipients_layout.addWidget(recipients_label)
        
        self.recipients_input = QTextEdit()
        self.recipients_input.setPlaceholderText("ornek1@gmail.com\nornek2@gmail.com\nornek3@gmail.com")
        self.recipients_input.setMaximumHeight(120)
        self.style_text_input(self.recipients_input)
        recipients_layout.addWidget(self.recipients_input)
        
        recipients_frame.setLayout(recipients_layout)
        content_layout.addWidget(recipients_frame)
        
        # Mail içeriği bölümü
        content_frame = self.create_section_frame("Mail İçeriği")
        content_mail_layout = QVBoxLayout()
        
        # Konu
        subject_layout = QHBoxLayout()
        subject_label = QLabel("Konu:")
        subject_label.setStyleSheet("color: #2c3e50; background-color: transparent;")
        subject_layout.addWidget(subject_label)
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Mail konunuzu buraya yazın")
        self.style_input(self.subject_input)
        subject_layout.addWidget(self.subject_input)
        content_mail_layout.addLayout(subject_layout)
        
        # İçerik
        content_label = QLabel("İçerik:")
        content_label.setStyleSheet("color: #2c3e50; background-color: transparent;")
        content_mail_layout.addWidget(content_label)
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Mail içeriğinizi buraya yazın...\n\nBoşluklar ve satır sonları korunacaktır.\nKopyala-yapıştır formatı otomatik olarak korunur.")
        self.content_input.setMinimumHeight(200)
        self.content_input.setAcceptRichText(False)  # Sadece düz metin kabul et
        self.content_input.setLineWrapMode(QTextEdit.WidgetWidth)  # Kelime kaydırma
        self.style_text_input(self.content_input)
        content_mail_layout.addWidget(self.content_input)
        
        # Metin düzenleme araçları
        tools_layout = QHBoxLayout()
        
        # Temizleme butonları
        clean_spaces_btn = QPushButton("🧹 Fazla Boşlukları Temizle")
        clean_spaces_btn.clicked.connect(self.clean_extra_spaces)
        self.style_button(clean_spaces_btn, "#e67e22")
        tools_layout.addWidget(clean_spaces_btn)
        
        # Satır düzenleme
        fix_lines_btn = QPushButton("📝 Satırları Düzenle")
        fix_lines_btn.clicked.connect(self.fix_line_breaks)
        self.style_button(fix_lines_btn, "#9b59b6")
        tools_layout.addWidget(fix_lines_btn)
        
        # Büyük/küçük harf düzenleme
        case_btn = QPushButton("🔤 Büyük Harfleri Düzelt")
        case_btn.clicked.connect(self.fix_capitalization)
        self.style_button(case_btn, "#3498db")
        tools_layout.addWidget(case_btn)
        
        content_mail_layout.addLayout(tools_layout)
        
        # İkinci satır araçlar
        tools_layout2 = QHBoxLayout()
        
        # Hepsini düzenle butonu
        fix_all_btn = QPushButton("✨ Hepsini Otomatik Düzenle")
        fix_all_btn.clicked.connect(self.fix_all_formatting)
        self.style_button(fix_all_btn, "#27ae60")
        tools_layout2.addWidget(fix_all_btn)
        
        # Geri al butonu
        undo_btn = QPushButton("↶ Geri Al")
        undo_btn.clicked.connect(self.undo_changes)
        self.style_button(undo_btn, "#95a5a6")
        tools_layout2.addWidget(undo_btn)
        
        # Önizleme butonu
        preview_btn = QPushButton("🔍 İçerik Önizleme")
        preview_btn.clicked.connect(self.preview_content)
        self.style_button(preview_btn, "#f39c12")
        tools_layout2.addWidget(preview_btn)
        
        content_mail_layout.addLayout(tools_layout2)
        
        content_frame.setLayout(content_mail_layout)
        content_layout.addWidget(content_frame)
        
        # CV ekleme bölümü
        cv_frame = self.create_section_frame("CV Ekleme (İsteğe Bağlı)")
        cv_layout = QHBoxLayout()
        
        self.cv_label = QLabel("CV seçilmedi")
        cv_layout.addWidget(self.cv_label)
        
        cv_btn = QPushButton("CV Seç")
        cv_btn.clicked.connect(self.select_cv)
        self.style_button(cv_btn, "#9b59b6")
        cv_layout.addWidget(cv_btn)
        
        cv_clear_btn = QPushButton("CV'yi Kaldır")
        cv_clear_btn.clicked.connect(self.clear_cv)
        self.style_button(cv_clear_btn, "#e74c3c")
        cv_layout.addWidget(cv_clear_btn)
        
        cv_frame.setLayout(cv_layout)
        content_layout.addWidget(cv_frame)
        
        # Gönderme bölümü
        send_frame = self.create_section_frame("Gönderme")
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
        
        # Durum etiketi
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        send_layout.addWidget(self.status_label)
        
        # Gönder butonu
        self.send_btn = QPushButton("📧 E-postaları Gönder")
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
        """Bölüm frame'i oluşturur"""
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
        """Input alanlarını stillendirir"""
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
        self.cv_label.setText("CV seçilmedi")
        self.cv_label.setStyleSheet("color: #7f8c8d;")
    
    def preview_content(self):
        """Mail içeriğinin önizlemesini gösterir"""
        content = self.content_input.toPlainText().strip()
        
        if not content:
            QMessageBox.warning(self, "Önizleme", "Önce mail içeriği yazın!")
            return
        
        # HTML formatına çevir
        thread = EmailSendingThread("", "", [], "", content)
        html_content = thread.text_to_html(content)
        
        # Önizleme penceresi oluştur
        preview_dialog = QMessageBox(self)
        preview_dialog.setWindowTitle("Mail İçerik Önizlemesi")
        preview_dialog.setText("Mail içeriğiniz bu şekilde gözükecek:")
        preview_dialog.setDetailedText(f"HTML Kodu:\n{html_content}")
        preview_dialog.setInformativeText(content[:500] + "..." if len(content) > 500 else content)
        preview_dialog.exec_()
    
    def clean_extra_spaces(self):
        """Fazla boşlukları temizler"""
        content = self.content_input.toPlainText()
        
        if not content.strip():
            QMessageBox.warning(self, "Uyarı", "Temizlenecek metin yok!")
            return
        
        # Mevcut içeriği geçmişe kaydet
        self.save_content_to_history()
        
        import re
        
        # Satır başı ve sonundaki boşlukları temizle
        lines = content.split('\n')
        cleaned_lines = [line.strip() for line in lines]
        
        # Çoklu boşlukları tek boşluğa çevir (satır başları hariç)
        for i, line in enumerate(cleaned_lines):
            cleaned_lines[i] = re.sub(r' +', ' ', line)
        
        # Çoklu satır sonlarını en fazla 2 satır sonuna çevir
        cleaned_content = '\n'.join(cleaned_lines)
        cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
        
        self.content_input.setPlainText(cleaned_content)
        QMessageBox.information(self, "Başarılı", "Fazla boşluklar temizlendi!")
    
    def fix_line_breaks(self):
        """Satır sonlarını düzenler"""
        content = self.content_input.toPlainText()
        
        if not content.strip():
            QMessageBox.warning(self, "Uyarı", "Düzenlenecek metin yok!")
            return
        
        # Mevcut içeriği geçmişe kaydet
        self.save_content_to_history()
        
        # Paragrafları ayır (çift satır sonu ile ayrılmış)
        paragraphs = content.split('\n\n')
        
        fixed_paragraphs = []
        for paragraph in paragraphs:
            # Her paragraf içindeki tek satır sonlarını boşlukla değiştir
            # Ama liste öğeleri ve özel formatları koru
            lines = paragraph.split('\n')
            
            # Liste öğelerini tespit et (-, •, *, sayılar)
            import re
            fixed_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    # Liste öğesi kontrolü
                    if re.match(r'^[-•*]\s+|^\d+\.\s+|^[a-zA-Z]\)\s+', line):
                        # Liste öğesi - yeni satır olarak bırak
                        if fixed_lines and not fixed_lines[-1].endswith('\n'):
                            fixed_lines.append('\n')
                        fixed_lines.append(line)
                    elif line.startswith(('📧', '📱', '🔗', '✅', '🎯', '💼')):
                        # Emoji ile başlayan satırlar - yeni satır
                        if fixed_lines and not fixed_lines[-1].endswith('\n'):
                            fixed_lines.append('\n')
                        fixed_lines.append(line)
                    else:
                        # Normal metin - önceki satırla birleştir
                        if fixed_lines and not fixed_lines[-1].endswith('\n'):
                            fixed_lines[-1] += ' ' + line
                        else:
                            fixed_lines.append(line)
            
            fixed_paragraphs.append('\n'.join(fixed_lines))
        
        # Paragrafları tekrar birleştir
        fixed_content = '\n\n'.join(fixed_paragraphs)
        
        self.content_input.setPlainText(fixed_content)
        QMessageBox.information(self, "Başarılı", "Satır sonları düzenlendi!")
    
    def fix_capitalization(self):
        """Büyük/küçük harf düzenlemesi yapar"""
        content = self.content_input.toPlainText()
        
        if not content.strip():
            QMessageBox.warning(self, "Uyarı", "Düzenlenecek metin yok!")
            return
        
        # Mevcut içeriği geçmişe kaydet
        self.save_content_to_history()
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.strip():
                # Satır başındaki kelimeyi büyük harfle başlat
                words = line.strip().split()
                if words:
                    # İlk kelimeyi büyük harfle başlat
                    if not words[0][0].isupper() and words[0][0].isalpha():
                        words[0] = words[0][0].upper() + words[0][1:]
                    
                    # E-posta adreslerini küçük harfe çevir
                    for i, word in enumerate(words):
                        if '@' in word and '.' in word:
                            words[i] = word.lower()
                    
                    # URL'leri küçük harfe çevir
                    for i, word in enumerate(words):
                        if word.startswith(('http://', 'https://', 'www.')):
                            words[i] = word.lower()
                
                fixed_lines.append(' '.join(words) if words else line)
            else:
                fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        self.content_input.setPlainText(fixed_content)
        QMessageBox.information(self, "Başarılı", "Büyük/küçük harfler düzenlendi!")
    
    def save_content_to_history(self):
        """Mevcut içeriği geçmişe kaydet"""
        current_content = self.content_input.toPlainText()
        if current_content.strip():
            self.content_history.append(current_content)
            # Son 10 değişikliği tut
            if len(self.content_history) > 10:
                self.content_history.pop(0)
    
    def fix_all_formatting(self):
        """Tüm düzenleme işlemlerini tek seferde yapar"""
        content = self.content_input.toPlainText()
        
        if not content.strip():
            QMessageBox.warning(self, "Uyarı", "Düzenlenecek metin yok!")
            return
        
        # Mevcut içeriği geçmişe kaydet
        self.save_content_to_history()
        
        # Tüm düzenleme işlemlerini sırayla yap
        self.clean_extra_spaces()
        self.fix_line_breaks()
        self.fix_capitalization()
        
        QMessageBox.information(self, "Tamamlandı", 
            "Tüm düzenleme işlemleri tamamlandı!\n\n"
            "• Fazla boşluklar temizlendi\n"
            "• Satır sonları düzenlendi\n"
            "• Büyük/küçük harfler düzeltildi\n\n"
            "Geri almak için 'Geri Al' butonunu kullanabilirsiniz.")
    
    def undo_changes(self):
        """Son değişiklikleri geri alır"""
        if not self.content_history:
            QMessageBox.information(self, "Bilgi", "Geri alınacak değişiklik yok!")
            return
        
        # Son kaydedilen içeriği geri yükle
        last_content = self.content_history.pop()
        self.content_input.setPlainText(last_content)
        QMessageBox.information(self, "Başarılı", "Son değişiklikler geri alındı!")

    def send_emails(self):
        """E-posta gönderme işlemini başlatır"""
        # Girdi kontrolü
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        recipients_text = self.recipients_input.toPlainText().strip()
        subject = self.subject_input.text().strip()
        content = self.content_input.toPlainText().strip()
        
        if not all([email, password, recipients_text, subject, content]):
            QMessageBox.warning(self, "Eksik Bilgi", 
                "Lütfen tüm gerekli alanları doldurun!")
            return
        
        # E-posta adreslerini ayıkla
        recipients = [line.strip() for line in recipients_text.split('\n') 
                     if line.strip() and '@' in line]
        
        if not recipients:
            QMessageBox.warning(self, "Alıcı Hatası", 
                "Geçerli e-posta adresi bulunamadı!")
            return
        
        # Onay iste
        reply = QMessageBox.question(self, "Onay", 
            f"{len(recipients)} kişiye e-posta göndermek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.No:
            return
        
        # UI'yi güncelle
        self.send_btn.setEnabled(False)
        self.cancel_btn.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(recipients))
        self.progress_bar.setValue(0)
        self.status_label.setText("E-posta gönderimi başlatılıyor...")
        
        # Thread başlat
        self.email_thread = EmailSendingThread(
            email, password, recipients, subject, content, self.cv_path)
        self.email_thread.progress_updated.connect(self.update_progress)
        self.email_thread.finished_signal.connect(self.sending_finished)
        self.email_thread.error_signal.connect(self.sending_error)
        self.email_thread.start()
    
    def cancel_sending(self):
        """E-posta gönderimini iptal eder"""
        if self.email_thread:
            self.email_thread.cancel()
        self.reset_ui()
    
    def update_progress(self, value, status):
        """Progress bar'ı günceller"""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)
    
    def sending_finished(self, successful, failed, error_msg):
        """Gönderim tamamlandığında çalışır"""
        self.reset_ui()
        
        if failed == 0:
            QMessageBox.information(self, "Başarılı", 
                f"Tüm e-postalar başarıyla gönderildi! ({successful} adet)")
        else:
            QMessageBox.warning(self, "Kısmi Başarı", 
                f"Gönderim sonucu:\n"
                f"✅ Başarılı: {successful} adet\n"
                f"❌ Başarısız: {failed} adet\n\n"
                f"Hata detayları:\n{error_msg[:500]}{'...' if len(error_msg) > 500 else ''}")
    
    def sending_error(self, error_msg):
        """Gönderim hatası durumunda çalışır"""
        self.reset_ui()
        QMessageBox.critical(self, "Hata", f"E-posta gönderilirken hata oluştu:\n\n{error_msg}")
    
    def reset_ui(self):
        """UI'yi başlangıç durumuna getirir"""
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