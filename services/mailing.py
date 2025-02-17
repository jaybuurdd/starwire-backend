import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv() 

def send_email(to: str, subject: str, body: str) -> bool:
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "job.t.developer@gmail.com"
    sender_pass = os.getenv("EMAIL_APP_PASSWORD")

    # create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to
    message["Subject"] = subject  # ✅ Corrected

    message.attach(MIMEText(body, "plain"))

    try:
        # connect to gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # secure connection
        server.login(sender_email, sender_pass)
        # send email
        server.sendmail(sender_email, to, message.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False