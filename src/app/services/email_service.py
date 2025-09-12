import smtplib
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

class EmailService:
    def __init__(self, to_address: str, smtp_username: str, smtp_password: str, smtp_host: str, smtp_port: int):
        self.to_address = to_address
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        
        # Validate required configuration
        if not all([to_address, smtp_username, smtp_password, smtp_host, smtp_port]):
            raise ValueError("All SMTP configuration parameters are required")

    def send_email(self, content: str, subject: str = "New contact form submission"):
        """Synchronous email sending - runs in thread pool"""
        try:
            # Create email message
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = self.to_address
            msg['Date'] = formatdate(localtime=True)
            msg['Message-ID'] = make_msgid()
            msg.set_content(content)

            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as smtp:
                smtp.starttls()  # Enable TLS encryption
                smtp.login(self.smtp_username, self.smtp_password)
                smtp.send_message(msg)
                
        except smtplib.SMTPException as e:
            raise RuntimeError(f"SMTP error: {e}")
        except Exception as e:
            raise RuntimeError(f"Email sending failed: {e}")
