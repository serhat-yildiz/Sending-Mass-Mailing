# Email Sending and Viewing Application

This application is a desktop application that can send mass emails and view emails through Gmail and Outlook accounts.

## Features

- Connect to Gmail and Outlook accounts
- Send mass emails
- View emails
- CV attachment support
- User-friendly interface
- Progress tracking

## Installation

1. Install required Python packages:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file and add your email information:
```
EMAIL=your_email@gmail.com
PASSWORD=your_app_password
```

3. Run the application:
```bash
python mail_app.py
```

## Creating App Password for Gmail

1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"
3. Go to "App Passwords"
4. Select "App" > "Other" > "Mail Application"
5. Copy the generated 16-digit password

## Creating App Password for Outlook

1. Go to https://account.microsoft.com/security
2. Go to "Security" > "Advanced security options"
3. Create a new app password from the "App passwords" section
4. Copy the generated password

## Usage

1. Enter your email settings
2. Add recipient list
3. Write email subject and content
4. Optionally add CV
5. Click "Send Emails" button

## Daily Sending Limits

- Gmail: 500 emails per day
- New Gmail accounts: 100 emails per day
- Mass sending: 100 emails per hour

## License

MIT License

---

# E-posta Gönderme ve Görüntüleme Uygulaması

Bu uygulama, Gmail ve Outlook hesapları üzerinden toplu e-posta gönderme ve e-posta görüntüleme işlemlerini yapabilen bir masaüstü uygulamasıdır.

## Özellikler

- Gmail ve Outlook hesaplarına bağlanma
- Toplu e-posta gönderme
- E-posta görüntüleme
- CV ekleme desteği
- Kullanıcı dostu arayüz
- İlerleme takibi

## Kurulum

1. Gerekli Python paketlerini yükleyin:
```bash
pip install -r requirements.txt
```

2. `.env` dosyası oluşturun ve e-posta bilgilerinizi ekleyin:
```
EMAIL=your_email@gmail.com
PASSWORD=your_app_password
```

3. Uygulamayı çalıştırın:
```bash
python mail_app.py
```

## Gmail için Uygulama Şifresi Oluşturma

1. https://myaccount.google.com/security adresine gidin
2. "2 Adımlı Doğrulama"yı etkinleştirin
3. "Uygulama Şifreleri"ne gidin
4. "Uygulama Seç" > "Diğer" > "Mail Uygulaması"
5. Oluşturulan 16 haneli şifreyi kopyalayın

## Outlook için Uygulama Şifresi Oluşturma

1. https://account.microsoft.com/security adresine gidin
2. "Güvenlik" > "Gelişmiş güvenlik seçenekleri"ne gidin
3. "Uygulama şifreleri" bölümünden yeni şifre oluşturun
4. Oluşturulan şifreyi kopyalayın

## Kullanım

1. E-posta ayarlarınızı girin
2. Alıcı listesini ekleyin
3. E-posta konusu ve içeriğini yazın
4. İsterseniz CV ekleyin
5. "Mailleri Gönder" butonuna tıklayın

## Günlük Gönderim Limitleri

- Gmail: Günlük 500 e-posta
- Yeni Gmail hesapları: Günlük 100 e-posta
- Toplu gönderimlerde: Saatte 100 e-posta

## Lisans

MIT License 