"""
Email Service - Intentionally SLOW and BLOCKING!

This demonstrates a major monolith anti-pattern:
- Synchronous email sending blocks the entire request
- If email server is down, orders can't be created
- No retry mechanism
- No queue for background processing

In microservices, this would be:
- Separate notification service
- Async message queue (RabbitMQ, Kafka)
- Fire-and-forget pattern
- Independent scaling
"""
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.config import get_settings

settings = get_settings()


class EmailService:
    """
    Email service with INTENTIONAL DELAYS to demonstrate blocking behavior
    """

    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email - BLOCKS for 2 seconds!

        In production, this would:
        1. Use an async email service (SendGrid, AWS SES)
        2. Put messages in a queue
        3. Process in background workers
        4. Return immediately

        But in our monolith, we BLOCK the entire request! 🐌
        """
        print(f"📧 [EmailService] Sending email to {to_email}: {subject}")
        print(f"⏳ [EmailService] This will take {settings.EMAIL_DELAY_SECONDS} seconds...")

        # INTENTIONAL BLOCKING DELAY!
        # This simulates a slow SMTP server or email API
        time.sleep(settings.EMAIL_DELAY_SECONDS)

        # In real implementation, we'd actually send email via SMTP or API
        # For now, we just log it (and would send to MailHog in real scenario)
        try:
            # Try to send via MailHog if it's running
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = to_email

            # Add plain text and HTML parts
            part1 = MIMEText(body, 'plain')
            msg.attach(part1)

            if html_body:
                part2 = MIMEText(html_body, 'html')
                msg.attach(part2)

            # Connect to MailHog (or fail silently for demo)
            try:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=1) as server:
                    server.send_message(msg)
                    print(f"✅ [EmailService] Email sent successfully! (Check MailHog at http://localhost:8025)")
            except Exception as e:
                print(f"⚠️  [EmailService] Could not send to MailHog (that's okay for demo): {e}")
                print(f"✅ [EmailService] Email logged (would be sent in production)")

            return True

        except Exception as e:
            print(f"❌ [EmailService] Email failed: {e}")
            # In monolith, if email fails, what happens to the order?
            # We might rollback the entire transaction!
            # This is a MAJOR PROBLEM!
            return False

    @staticmethod
    def send_order_confirmation(order_id: int, user_email: str, total: float) -> bool:
        """
        Send order confirmation email - BLOCKS the order creation!
        """
        subject = f"Order Confirmation #{order_id}"
        body = f"""
Thank you for your order!

Order #: {order_id}
Total: ${total:.2f}

We'll send you a shipping confirmation soon.
        """

        html_body = f"""
<html>
<body>
    <h2>Thank you for your order!</h2>
    <p><strong>Order #:</strong> {order_id}</p>
    <p><strong>Total:</strong> ${total:.2f}</p>
    <p>We'll send you a shipping confirmation soon.</p>
</body>
</html>
        """

        return EmailService.send_email(user_email, subject, body, html_body)

    @staticmethod
    def send_shipping_notification(order_id: int, user_email: str) -> bool:
        """Send shipping notification - also BLOCKS!"""
        subject = f"Your Order #{order_id} Has Shipped!"
        body = f"Your order #{order_id} is on its way!"
        return EmailService.send_email(user_email, subject, body)
