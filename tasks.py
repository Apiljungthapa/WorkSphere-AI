from celery import Celery
from celery.exceptions import Retry
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)  # Retry 3 times, wait 60 seconds between retries
def send_email_task(self, to_email: str, full_name: str, otp_code: int):
    """Task to send OTP via email."""
    message = Mail(
        from_email='apilthapa87@gmail.com',
        to_emails=to_email,
        subject='Your OTP Code',
        html_content=f'<strong>Hello {full_name}, your OTP code is {otp_code}. Please enter this while logging in. </strong>'
    )
    try:
        sg = SendGridAPIClient('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')
        sg.send(message)
        print(f"Email sent to {to_email}")
    except Exception as e:
        if "429" in str(e):  # Check for "Too Many Requests" error
            print("Rate limit exceeded. Retrying...")
            raise self.retry(exc=e)
        else:
            print(f"Error sending email: {e}")
