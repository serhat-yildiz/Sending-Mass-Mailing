# 📧 Professional Mass Email HTML Template Sender

This application is a modern desktop application that can send mass emails using professional HTML email templates through Gmail accounts.

## ✨ Features

- 🎨 **HTML Email Template Support**: Send emails using professional HTML templates
- 📧 **Gmail Integration**: Secure sending through your Gmail account
- 📊 **Bulk Sending**: Send emails to multiple recipients simultaneously
- 📎 **CV/File Attachment**: PDF file attachment support
- 🎯 **Progress Tracking**: Real-time sending status tracking
- 🔒 **Secure**: Secure communication via encrypted SMTP protocol
- 🖥️ **Modern Interface**: User-friendly, modern design

## 🚀 Installation

### 1. Requirements
- Python 3.7 or higher
- PyQt5 (installed via Homebrew)
- Gmail account and app password

### 2. Installation Steps

```bash
# Clone or download the project
cd Sending-Mass-Mailing

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install required packages
pip install -r requirements_alt.txt

# Install PyQt5 via Homebrew (macOS)
brew install pyqt@5
```

### 3. Run the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Start the application
PYTHONPATH="/opt/homebrew/lib/python3.13/site-packages:$PYTHONPATH" python3 mail_app.py
```

## 🔑 Creating Gmail App Password

### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Find and enable "2-Step Verification"
3. Verify your phone number

### Step 2: Create App Password
1. With 2-Step Verification enabled, go to "App Passwords" section
2. Select "Other (custom name)" from "Select App" menu
3. Give it a name like "Mail Application" or "Mass Mailer"
4. Click "Generate" button
5. Copy the generated 16-digit password

⚠️ **IMPORTANT**: You must use this special app password, NOT your regular Gmail password!

## 📝 Using the Application

### 1. Gmail Settings
- **Gmail Address**: Enter your sender email address
- **App Password**: Enter the 16-digit password you created above

### 2. Recipients List
- Write one email address per line
- Example:
  ```
  candidate1@example.com
  candidate2@gmail.com
  hr@company.com
  ```

### 3. Email Content
- **Subject**: Write your email subject
- **HTML Template**: Paste your professional HTML template

### 4. CV Attachment (Optional)
- Click "Select CV" button
- Choose your CV file in PDF format

### 5. Start Sending
- Click "🚀 Deploy Email Campaign" button
- Confirm and wait for sending to complete

## 🎨 HTML Email Template Guide

### Basic HTML Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Email</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 2px solid #3498db;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .content {
            line-height: 1.6;
            color: #333;
        }
        .highlight {
            background-color: #e8f4fd;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }
        .button {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="color: #2c3e50; margin: 0;">Company Name</h1>
            <p style="margin: 5px 0; color: #7f8c8d;">Professional Communication</p>
        </div>
        
        <div class="content">
            <h2 style="color: #2c3e50;">Hello,</h2>
            
            <p>We would like to get in touch with you...</p>
            
            <div class="highlight">
                <strong>Important Information:</strong> You can highlight your important message in this section.
            </div>
            
            <p>For detailed information, you can click the button below:</p>
            
            <a href="https://example.com" class="button">View Details</a>
            
            <p>Best regards,<br>
            <strong>Your Name</strong><br>
            Your Position</p>
        </div>
        
        <div class="footer">
            <p>This email was sent automatically.</p>
            <p>Company Name | Address | Phone | Website</p>
        </div>
    </div>
</body>
</html>
```

### Job Application Template Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Application</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; }
        .profile { text-align: center; margin-bottom: 30px; }
        .skills { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="profile">
            <h1 style="color: #2c3e50;">Your Name</h1>
            <p style="color: #7f8c8d; font-size: 16px;">Software Developer</p>
        </div>
        
        <h2 style="color: #3498db;">Dear HR Specialist,</h2>
        
        <p>I would like to apply for the <strong>[Position Name]</strong> position available at your company.</p>
        
        <div class="skills">
            <h3 style="margin-top: 0; color: #2c3e50;">Technical Skills:</h3>
            <ul>
                <li>Python, JavaScript, React</li>
                <li>PostgreSQL, MongoDB</li>
                <li>Docker, AWS</li>
            </ul>
        </div>
        
        <p>You can find detailed information in my attached CV.</p>
        
        <p>Best regards,<br>
        <strong>Your Name</strong><br>
        📧 email@example.com | 📱 +1 555 123 45 67</p>
    </div>
</body>
</html>
```

## 📊 Sending Limits and Recommendations

### Gmail Limits
- **Daily Limit**: 500 emails
- **New Accounts**: 100 emails/day
- **Hourly Limit**: 100 emails
- **Rate Limiting**: 1 minute wait every 10 emails

### Best Practices
1. **Small Groups**: Send in groups of 50-100 emails
2. **Personalization**: Customize each template for the recipient
3. **Test Sending**: Send a test email to yourself first
4. **Spam Prevention**: Avoid excessively large file attachments
5. **Content Quality**: Prepare professional and meaningful content

## 🔧 Troubleshooting

### Common Errors

**1. Authentication Error**
- Check your app password
- Make sure 2-factor authentication is enabled

**2. PyQt5 Import Error**
```bash
brew install pyqt@5
export PYTHONPATH="/opt/homebrew/lib/python3.13/site-packages:$PYTHONPATH"
```

**3. SSL Certificate Error**
- Check your internet connection
- Check firewall settings

## 📄 License

MIT License - This software can be freely used and distributed.
