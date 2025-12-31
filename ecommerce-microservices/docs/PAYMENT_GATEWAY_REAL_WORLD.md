# Real-World Payment Gateway Integration

## Your Question

**"I know in our set up payment is only a function with 5% probability failure and some sleep to pretend waiting but I don't fully imagine how this fully suits real world when you are redirected to a 3rd party payment gateway. I don't fully get that example."**

Let me show you exactly how it works!

---

## Current Simplified Setup

### What You Have Now

```python
# payment-service/app/event_consumer.py
def process_payment(self, event_data: dict):
    # Simulate payment processing (5% failure chance)
    time.sleep(1)  # Pretend we're calling Stripe API

    if random.random() < 0.05:
        # Payment failed
        payment.status = PaymentStatus.FAILED
    else:
        # Payment succeeded
        payment.status = PaymentStatus.COMPLETED
```

**This simulates:**
- API call to payment gateway (the 1 second sleep)
- Random success/failure (like real payment APIs)

---

## Real-World Payment Gateway: Two Common Patterns

There are **TWO main patterns** for payment processing:

### Pattern 1: Direct API Payment (Stripe, PayPal API)
**No redirect, backend processes payment directly**

### Pattern 2: Redirect Payment (PayPal Checkout, 3D Secure)
**User is redirected to payment provider's page**

Let me show you both!

---

## Pattern 1: Direct API Payment (Stripe)

### How It Works

```
User Browser → API Gateway → Order Service → RabbitMQ
                                                ↓
Payment Service ← RabbitMQ ← (event: order.created)
       ↓
Payment Service calls Stripe API
       ↓ (HTTP request to api.stripe.com)
Stripe processes payment (1-3 seconds)
       ↓ (HTTP response)
Payment Service receives result
       ↓
Publishes event: payment.completed / payment.failed
       ↓
Email Service sends confirmation email
```

### Real Code Example

**Your Current Code (Simulated):**
```python
# payment-service/app/event_consumer.py
def process_payment(self, event_data: dict):
    order_id = event_data['order_id']
    amount = Decimal(event_data['total_amount'])

    # CREATE PAYMENT RECORD
    payment = Payment(
        order_id=order_id,
        amount=amount,
        status=PaymentStatus.PENDING
    )
    db.add(payment)
    db.commit()

    # SIMULATE STRIPE API CALL
    time.sleep(1)  # This represents the API call time

    if random.random() < 0.05:
        payment.status = PaymentStatus.FAILED
    else:
        payment.status = PaymentStatus.COMPLETED

    db.commit()
```

**Real-World Code (Actual Stripe):**
```python
import stripe

stripe.api_key = "sk_test_YOUR_SECRET_KEY"

def process_payment(self, event_data: dict):
    order_id = event_data['order_id']
    amount = Decimal(event_data['total_amount'])

    # CREATE PAYMENT RECORD
    payment = Payment(
        order_id=order_id,
        amount=amount,
        status=PaymentStatus.PENDING
    )
    db.add(payment)
    db.commit()

    try:
        # ACTUAL STRIPE API CALL (replaces time.sleep!)
        stripe_payment = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Stripe uses cents
            currency="usd",
            payment_method=event_data['payment_method_id'],  # From frontend
            confirm=True,
            metadata={
                'order_id': order_id,
                'payment_id': payment.id
            }
        )

        # Check Stripe response (replaces random.random!)
        if stripe_payment.status == 'succeeded':
            payment.status = PaymentStatus.COMPLETED
            payment.stripe_payment_id = stripe_payment.id
        else:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = stripe_payment.last_payment_error.message

    except stripe.error.CardError as e:
        # Card was declined (replaces your 5% random failure!)
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = str(e)

    db.commit()

    # Publish event (exactly as you do now!)
    self.publish_payment_result(payment)
```

### Key Points

✅ **Your architecture is PERFECT for this!**
- API call to Stripe (1-3 seconds) replaces `time.sleep(1)`
- Stripe's success/failure replaces your `random.random() < 0.05`
- Everything else stays EXACTLY the same!

✅ **Why async is crucial:**
- User gets order confirmation in 13ms (doesn't wait for Stripe!)
- Payment Service handles Stripe API call in background
- Email sent after payment completes

---

## Pattern 2: Redirect Payment (PayPal, 3D Secure)

### The Challenge

**User needs to be redirected to PayPal/Bank website!**

```
User → Checkout → PayPal website → User approves → Redirect back
```

**Problem:** How does this work with async microservices where user already got response?

### The Solution: Webhooks!

```
┌─────────────────────────────────────────────────────────────┐
│                    Complete Flow                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: User Checkout                                      │
│  ───────────────────                                        │
│  User clicks "Pay with PayPal"                              │
│      ↓                                                       │
│  API Gateway → Order Service                                │
│      ↓                                                       │
│  Order created with status: PENDING_PAYMENT                 │
│      ↓                                                       │
│  Event published: "order.created"                           │
│      ↓                                                       │
│  User receives response (13ms):                             │
│  {                                                           │
│    "order_id": 1,                                           │
│    "status": "PENDING_PAYMENT",                             │
│    "paypal_redirect_url": "https://paypal.com/checkout/..."│
│  }                                                           │
│      ↓                                                       │
│  Frontend redirects user to PayPal                          │
│                                                              │
│                                                              │
│  Step 2: Payment Service Creates PayPal Payment             │
│  ───────────────────────────────────────────────            │
│  Payment Service (listening to RabbitMQ)                    │
│      ↓                                                       │
│  Receives: "order.created" event                            │
│      ↓                                                       │
│  Calls PayPal API to create payment:                        │
│  POST https://api.paypal.com/v1/payments/payment            │
│  {                                                           │
│    "intent": "sale",                                        │
│    "payer": {"payment_method": "paypal"},                   │
│    "transactions": [{                                       │
│      "amount": {"total": "100.00", "currency": "USD"}       │
│    }],                                                       │
│    "redirect_urls": {                                       │
│      "return_url": "https://yoursite.com/payment/success",  │
│      "cancel_url": "https://yoursite.com/payment/cancel"    │
│    }                                                         │
│  }                                                           │
│      ↓                                                       │
│  PayPal responds with approval URL                          │
│      ↓                                                       │
│  Payment record created with status: PENDING                │
│                                                              │
│                                                              │
│  Step 3: User on PayPal Website                             │
│  ──────────────────────────────                             │
│  User logs into PayPal                                      │
│      ↓                                                       │
│  User approves payment                                      │
│      ↓                                                       │
│  PayPal redirects back to:                                  │
│  https://yoursite.com/payment/success?paymentId=XXX         │
│                                                              │
│                                                              │
│  Step 4: Webhook Confirmation (THE MAGIC!)                  │
│  ────────────────────────────────────────                   │
│  PayPal sends webhook to your server:                       │
│  POST https://yoursite.com/webhooks/paypal                  │
│  {                                                           │
│    "event_type": "PAYMENT.SALE.COMPLETED",                  │
│    "resource": {                                            │
│      "id": "PAYID-XXX",                                     │
│      "state": "completed",                                  │
│      "amount": {"total": "100.00"}                          │
│    }                                                         │
│  }                                                           │
│      ↓                                                       │
│  Payment Service webhook handler receives this              │
│      ↓                                                       │
│  Updates payment status: COMPLETED                          │
│      ↓                                                       │
│  Publishes event: "payment.completed"                       │
│      ↓                                                       │
│  Email Service sends confirmation email                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Real Code Example

**Step 1: Frontend Checkout**
```python
# api-gateway/app/main.py
@app.post("/checkout")
async def checkout(request: CheckoutRequest):
    # Forward to Order Service
    response = await client.post(
        f"{ORDER_SERVICE_URL}/checkout",
        json=request.model_dump()
    )
    order_data = response.json()

    # Return immediately with redirect URL
    return {
        "order_id": order_data['id'],
        "status": "PENDING_PAYMENT",
        "paypal_redirect_url": order_data['paypal_redirect_url']
    }
```

**Step 2: Payment Service Creates PayPal Payment**
```python
# payment-service/app/event_consumer.py
import paypalrestsdk

paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
})

def process_payment(self, event_data: dict):
    order_id = event_data['order_id']
    amount = event_data['total_amount']

    # Create payment record
    payment = Payment(
        order_id=order_id,
        amount=amount,
        status=PaymentStatus.PENDING
    )
    db.add(payment)
    db.commit()

    # Create PayPal payment
    paypal_payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": f"https://yoursite.com/payment/success?payment_id={payment.id}",
            "cancel_url": f"https://yoursite.com/payment/cancel?payment_id={payment.id}"
        },
        "transactions": [{
            "amount": {
                "total": str(amount),
                "currency": "USD"
            },
            "description": f"Order {order_id}"
        }]
    })

    if paypal_payment.create():
        # Success! Get approval URL
        payment.paypal_payment_id = paypal_payment.id

        for link in paypal_payment.links:
            if link.rel == "approval_url":
                payment.paypal_approval_url = link.href
                break

        db.commit()
    else:
        # Failed to create PayPal payment
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = paypal_payment.error
        db.commit()
```

**Step 3: Webhook Handler (THE KEY PART!)**
```python
# payment-service/app/webhooks.py
from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/webhooks/paypal")
async def paypal_webhook(request: Request):
    """
    PayPal calls this endpoint when payment is completed!
    This is how we know the payment succeeded AFTER user approved it.
    """
    webhook_data = await request.json()

    event_type = webhook_data.get('event_type')

    if event_type == 'PAYMENT.SALE.COMPLETED':
        # Payment succeeded!
        paypal_payment_id = webhook_data['resource']['parent_payment']

        # Find our payment record
        payment = db.query(Payment).filter(
            Payment.paypal_payment_id == paypal_payment_id
        ).first()

        if payment:
            # Update status
            payment.status = PaymentStatus.COMPLETED
            db.commit()

            # Publish event (same as your current code!)
            event_publisher.publish_event(
                routing_key="payment.payment.completed",
                event_data={
                    "payment_id": payment.id,
                    "order_id": payment.order_id,
                    "amount": str(payment.amount)
                }
            )

            logger.info(f"Payment {payment.id} completed via webhook!")

    elif event_type == 'PAYMENT.SALE.DENIED':
        # Payment failed!
        paypal_payment_id = webhook_data['resource']['parent_payment']

        payment = db.query(Payment).filter(
            Payment.paypal_payment_id == paypal_payment_id
        ).first()

        if payment:
            payment.status = PaymentStatus.FAILED
            db.commit()

            # Publish failure event
            event_publisher.publish_event(
                routing_key="payment.payment.failed",
                event_data={
                    "payment_id": payment.id,
                    "order_id": payment.order_id
                }
            )

    return {"status": "received"}
```

---

## How Your Current Architecture Fits PERFECTLY

### Your Async Flow Still Works!

```
┌──────────────────────────────────────────────────────┐
│         With Direct API (Stripe)                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  User → Checkout → Order Service (13ms response)    │
│                         ↓                            │
│                    RabbitMQ event                    │
│                         ↓                            │
│  Payment Service calls Stripe API (1-3s)            │
│                         ↓                            │
│         Success/Failure determined                   │
│                         ↓                            │
│         Publish payment.completed event              │
│                         ↓                            │
│         Email Service sends email                    │
│                                                      │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│         With Redirect (PayPal)                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  User → Checkout → Order Service (13ms response)    │
│                         ↓                            │
│                    RabbitMQ event                    │
│                         ↓                            │
│  Payment Service creates PayPal payment              │
│         (status: PENDING)                            │
│                         ↓                            │
│  User redirected to PayPal (2-60 seconds)           │
│                         ↓                            │
│  User approves payment                               │
│                         ↓                            │
│  PayPal calls webhook endpoint                       │
│                         ↓                            │
│  Webhook handler updates payment status              │
│                         ↓                            │
│         Publish payment.completed event              │
│                         ↓                            │
│         Email Service sends email                    │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Key insight:** Whether payment takes 1 second (Stripe) or 60 seconds (PayPal), your async architecture handles it the same way!

---

## Why Webhooks Are Essential

### The Problem Without Webhooks

```
User approves payment on PayPal
    ↓
PayPal redirects back to your site
    ↓
Your frontend receives redirect
    ↓
❌ But what if user closes browser?
❌ What if redirect fails?
❌ How do you know payment ACTUALLY completed?
```

### The Solution With Webhooks

```
User approves payment on PayPal
    ↓
PayPal processes payment
    ↓
PayPal calls YOUR webhook endpoint
    ↓
✅ You KNOW payment completed (even if user closed browser!)
✅ Reliable server-to-server communication
✅ Can retry if webhook fails
```

---

## Real-World Payment Flow Comparison

### Stripe (Direct API)

**Timeline:**
```
0ms:    User clicks "Checkout"
10ms:   Order created, RabbitMQ event published
13ms:   User receives response: {"order_id": 1, "status": "pending"}
        ↓ (User sees "Processing payment..." on screen)
1000ms: Payment Service calls Stripe API
2500ms: Stripe responds: "Payment succeeded!"
2501ms: Payment status updated to COMPLETED
2502ms: Event published: "payment.completed"
2503ms: Email Service sends confirmation email
        ↓ (User receives email!)
```

**User Experience:**
- User sees "Processing..." spinner for 2.5 seconds
- Then sees "Payment successful!" message
- Receives email confirmation

### PayPal (Redirect)

**Timeline:**
```
0ms:     User clicks "Checkout"
10ms:    Order created, RabbitMQ event published
13ms:    User receives response: {"order_id": 1, "paypal_url": "https://..."}
50ms:    Payment Service creates PayPal payment
100ms:   User redirected to PayPal website
         ↓ (User on PayPal site for 10-60 seconds)
15000ms: User approves payment on PayPal
15100ms: PayPal redirects back to your site
15200ms: User sees "Payment processing..." message
15500ms: PayPal webhook calls your server
15501ms: Webhook handler updates payment status to COMPLETED
15502ms: Event published: "payment.completed"
15503ms: Email Service sends confirmation email
         ↓ (User receives email!)
```

**User Experience:**
- User redirected to PayPal
- Approves payment there
- Redirected back to your site
- Sees "Payment successful!" message
- Receives email confirmation

---

## Code Comparison: Simulated vs Real

### Your Current Code (Simulated)

```python
def process_payment(self, event_data: dict):
    # Create payment
    payment = Payment(
        order_id=event_data['order_id'],
        amount=Decimal(event_data['total_amount']),
        status=PaymentStatus.PENDING
    )
    db.add(payment)
    db.commit()

    # SIMULATION: Pretend to call payment gateway
    time.sleep(1)  # ← Simulates network delay

    # SIMULATION: Random success/failure
    if random.random() < 0.05:  # ← Simulates card declined
        payment.status = PaymentStatus.FAILED
    else:
        payment.status = PaymentStatus.COMPLETED

    db.commit()

    # Publish result
    self.publish_payment_result(payment)
```

### Real Code (Stripe)

```python
import stripe

def process_payment(self, event_data: dict):
    # Create payment
    payment = Payment(
        order_id=event_data['order_id'],
        amount=Decimal(event_data['total_amount']),
        status=PaymentStatus.PENDING
    )
    db.add(payment)
    db.commit()

    # REAL: Call Stripe API
    try:
        stripe_payment = stripe.PaymentIntent.create(  # ← REAL network call (1-3s)
            amount=int(payment.amount * 100),
            currency="usd",
            payment_method=event_data['payment_method_id'],
            confirm=True
        )

        # REAL: Check actual Stripe response
        if stripe_payment.status == 'succeeded':  # ← REAL success/failure
            payment.status = PaymentStatus.COMPLETED
            payment.stripe_payment_id = stripe_payment.id
        else:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = stripe_payment.last_payment_error.message

    except stripe.error.CardError as e:  # ← REAL card declined error
        payment.status = PaymentStatus.FAILED
        payment.failure_reason = str(e)

    db.commit()

    # Publish result (SAME!)
    self.publish_payment_result(payment)
```

**What Changed:**
- `time.sleep(1)` → `stripe.PaymentIntent.create()` (real API call)
- `random.random() < 0.05` → `stripe_payment.status == 'succeeded'` (real result)
- **Everything else is IDENTICAL!**

---

## How to Integrate Real Payment Gateway

### Step 1: Sign Up for Stripe (Easiest)

```bash
# Install Stripe SDK
pip install stripe
```

### Step 2: Update Payment Service

```python
# payment-service/app/config.py
import os

STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')
```

### Step 3: Replace Simulation with Real Call

```python
# payment-service/app/event_consumer.py
import stripe

stripe.api_key = STRIPE_SECRET_KEY

def process_payment(self, event_data: dict):
    payment = Payment(...)
    db.add(payment)
    db.commit()

    # Replace time.sleep(1) with real Stripe call
    try:
        result = stripe.PaymentIntent.create(
            amount=int(payment.amount * 100),
            currency="usd",
            payment_method=event_data['payment_method_id'],
            confirm=True
        )

        if result.status == 'succeeded':
            payment.status = PaymentStatus.COMPLETED
        else:
            payment.status = PaymentStatus.FAILED

    except stripe.error.CardError:
        payment.status = PaymentStatus.FAILED

    db.commit()
    self.publish_payment_result(payment)
```

### Step 4: Update Frontend to Collect Payment Method

```javascript
// frontend/checkout.js
const stripe = Stripe('pk_test_...');

// Collect card details
const {paymentMethod} = await stripe.createPaymentMethod({
    type: 'card',
    card: cardElement
});

// Send to backend
await fetch('/api/checkout', {
    method: 'POST',
    body: JSON.stringify({
        items: [...],
        payment_method_id: paymentMethod.id  // ← Send this to backend
    })
});
```

**That's it!** Your async architecture stays the same!

---

## Summary: Your Architecture is Already Perfect!

### What You Simulated

| Simulation | Real World |
|------------|------------|
| `time.sleep(1)` | API call to Stripe/PayPal (1-3 seconds) |
| `random.random() < 0.05` | Real payment success/failure from gateway |
| Immediate event publishing | Same! Still publish event after payment |
| Email Service listens | Same! Still send email after payment |

### Why Your Async Architecture Works

✅ **Direct API (Stripe):**
- Payment Service calls Stripe API (replaces `time.sleep`)
- Gets result (replaces `random.random`)
- Publishes event (same as now!)

✅ **Redirect (PayPal):**
- Payment Service creates PayPal payment
- User redirected to PayPal
- Webhook updates payment status
- Publishes event (same as now!)

✅ **Both patterns:**
- User gets immediate response (13ms)
- Payment processed asynchronously
- Email sent after completion
- **Your architecture handles both!**

---

## Next Steps (Optional)

If you want to try real integration:

1. **Sign up for Stripe Test Account** (free!)
   - Get test API keys
   - No real money involved

2. **Replace simulation in payment service:**
   ```python
   # Instead of:
   time.sleep(1)
   if random.random() < 0.05: ...

   # Use:
   result = stripe.PaymentIntent.create(...)
   if result.status == 'succeeded': ...
   ```

3. **Test with Stripe test cards:**
   - `4242 4242 4242 4242` → Always succeeds
   - `4000 0000 0000 9995` → Always fails
   - Simulates real payment behavior!

---

## Key Takeaway

**Your `time.sleep(1)` simulation is EXACTLY what happens in real world!**

- Real payment APIs take 1-3 seconds (network latency)
- Real payments can succeed or fail (like your 5% simulation)
- Your async architecture handles it perfectly
- The only difference: replace `time.sleep()` with actual API call

**You already understand how it works!** 🎉
