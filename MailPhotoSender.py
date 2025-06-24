
import os
from email.message import EmailMessage
import smtplib
class MailPhotoSender:
    def __init__(self, from_email, password, smtp_server, smtp_port):
        self.from_email = from_email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_mail_with_image(self, subject, body, to_email, image_path=r"C:\Users\esma-\dev\CameraDetection\face.jpg"):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg.set_content(body)

        with open(image_path, 'rb') as img:
            img_data = img.read()
            img_name = os.path.basename(image_path)
            msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename=img_name)

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
            smtp.starttls()
            smtp.login(self.from_email, self.password)
            smtp.send_message(msg)
