"""
Payment Service - Also BLOCKING!

Another monolith anti-pattern:
- Synchronous payment processing
- External API call blocks the entire request
- No timeout handling
- No circuit breaker
- If payment gateway is slow, everything is slow

In microservices:
- Separate payment service
- Async processing
- Circuit breaker pattern (Hystrix, Resilience4j)
- Timeout and retry strategies
- Fallback mechanisms
"""
import time
import uuid
from typing import Tuple

from app.config import get_settings

settings = get_settings()


class PaymentService:
    """
    Payment processing service with INTENTIONAL DELAYS
    """

    @staticmethod
    def process_payment(
        order_id: int,
        amount: float,
        payment_method: str
    ) -> Tuple[bool, str, str]:
        """
        Process a payment - BLOCKS for 1 second!

        In reality, this would call an external payment gateway:
        - Stripe, PayPal, Square, etc.
        - Network latency
        - API processing time
        - 3D Secure verification

        Returns: (success, status, transaction_id)
        """
        print(f"💳 [PaymentService] Processing payment for order #{order_id}")
        print(f"💰 [PaymentService] Amount: ${amount:.2f}, Method: {payment_method}")
        print(f"⏳ [PaymentService] Calling payment gateway... ({settings.PAYMENT_DELAY_SECONDS}s delay)")

        # INTENTIONAL BLOCKING DELAY!
        # This simulates calling external payment API (Stripe, PayPal, etc.)
        time.sleep(settings.PAYMENT_DELAY_SECONDS)

        # Simulate payment processing
        # In real world: validate card, check fraud, process charge
        transaction_id = f"txn_{uuid.uuid4().hex[:12]}"

        # Simulate 95% success rate
        import random
        success = random.random() > 0.05  # 5% failure rate

        if success:
            status = "completed"
            print(f"✅ [PaymentService] Payment successful! Transaction ID: {transaction_id}")
        else:
            status = "failed"
            print(f"❌ [PaymentService] Payment failed! (Simulated failure)")

        return success, status, transaction_id

    @staticmethod
    def refund_payment(transaction_id: str, amount: float) -> bool:
        """
        Refund a payment - also BLOCKS!
        """
        print(f"💸 [PaymentService] Processing refund for {transaction_id}")
        print(f"⏳ [PaymentService] This will take {settings.PAYMENT_DELAY_SECONDS} second...")

        # ANOTHER BLOCKING DELAY!
        time.sleep(settings.PAYMENT_DELAY_SECONDS)

        print(f"✅ [PaymentService] Refund of ${amount:.2f} completed")
        return True

    @staticmethod
    def verify_payment(transaction_id: str) -> bool:
        """
        Verify a payment status - yep, also blocks!
        """
        print(f"🔍 [PaymentService] Verifying payment {transaction_id}")
        time.sleep(0.5)  # Shorter delay for verification
        print(f"✅ [PaymentService] Payment verified")
        return True
