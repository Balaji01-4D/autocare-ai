import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(receiver: str, subject: str, body: str):
    """
    Send a plain text email body via Gmail SMTP.

    Args:
        receiver (str): Receiver's email address.
        body (str): The email body content.
    """
    sender_email = "autocare.org.in@gmail.com"
    sender_password = "dnnupxrjogyjmpeb" 

    msg = MIMEText(body, 'plain')
    msg['From'] = sender_email
    msg['To'] = receiver
    msg['Subject'] = subject 
    

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


send_mail("annetraj2005@gmail.com", "hello", "this is a test mail")