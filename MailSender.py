import smtplib
from email.message import EmailMessage

class MailSender:
    def __init__(self, from_email, password, smtp_server, smtp_port):
        self.from_email = from_email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_mail(self, subject, body, to_email):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg.set_content(body)

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(self.from_email, self.password)
            smtp.send_message(msg)
