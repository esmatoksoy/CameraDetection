from MailPhotoSender import MailPhotoSender
if __name__ == "__main__":
            # Replace these with your actual credentials and recipient
            FROM_EMAIL = "esmatoksoy3@gmail.com"
            PASSWORD = "jfzb kgyx uicn bdor"
            SMTP_SERVER = "smtp.gmail.com"
            SMTP_PORT = 587
            TO_EMAIL = "esma-toksoy@hotmail.com"
            

            sender = MailPhotoSender(FROM_EMAIL, PASSWORD, SMTP_SERVER, SMTP_PORT)
            subject = "Test Email with Image"
            body = "This is a test email with an attached image."
            image_path = r"C:\Users\esma-\dev\CameraDetection\face.jpg"

            sender.send_mail_with_image(subject, body, TO_EMAIL, image_path)
            print("Email with image sent successfully.")    
            