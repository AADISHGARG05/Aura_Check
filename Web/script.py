import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



def send_email(email):
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    SENDER_EMAIL = "tryagain800930@gmail.com"
    SENDER_PASSWORD = "tchd pwbi knhd ipgu"
    # email = "nevarycolab@gmail.com"

    # Create Email Message
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = email
    message["Subject"] = "Test Email from Python"

    # Email Body
    body = "Hello, this is a test email sent from Python!"
    message.attach(MIMEText(body, "plain"))

    # Send Email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, email, message.as_string())

    print("Email sent successfully!")