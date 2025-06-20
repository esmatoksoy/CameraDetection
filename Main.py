from MailSender import MailSender
from dotenv import load_dotenv
import os

# Load variables from the .env file
load_dotenv(dotenv_path=r"C:\Users\esma-\OneDrive\Masaüstü\CameraDetection\info.env")

# Read values from environment variables
from_email = os.getenv("FROM_EMAIL")
to_email = os.getenv("TO_EMAIL")
password = os.getenv("PASSWORD")

if __name__ == "__main__":
    sender = MailSender(
        from_email=from_email,
        password=password,
        smtp_server="smtp.gmail.com",
        smtp_port=587
    )

    success = sender.send_mail(
        subject="Testing Email",
        body="No photo only mail.",
        to_email=to_email
    )

    if success:
        print("Email sent successfully.")
    else:
        print("Failed to send email.")
