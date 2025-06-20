        # Example usage of send_mail_with_image
        image_path = r"C:\Users\esma-\dev\CameraDetection\test_image.jpg"
        success_with_image = sender.send_mail_with_image(
            subject="Testing Email with Image",
            body="This email contains an image attachment.",
            to_email=to_email,
            image_path=image_path
        )

        if success_with_image:
            print("Email with image sent successfully.")
        else:
            print("Failed to send email with image.")