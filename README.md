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