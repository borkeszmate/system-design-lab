# Testing the Monolith Pain Points 🔥

This guide shows you how to experience the intentional monolith anti-patterns we built.

## Quick Test Script

Save this as `test_monolith.sh` and run it to see the pain!

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "🎯 Testing E-Commerce Monolith Pain Points"
echo "==========================================="
echo ""

# 1. Register a user
echo "📝 Step 1: Registering user..."
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }' 2>&1 | grep -q "already registered" && \
  curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" || \
  curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "✅ Got auth token"
echo ""

# 2. Create a category (need admin user - skip for now)
echo "📦 Step 2: Would create products here (needs admin)..."
echo "   For this demo, you'll need to create products via Swagger UI"
echo "   Visit: http://localhost:8000/docs"
echo ""

# 3. Add items to cart
echo "🛒 Step 3: Adding items to cart..."
curl -s -X POST "$BASE_URL/api/cart/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
echo "✅ Items added to cart"
echo ""

# 4. THE BIG ONE: Checkout (3-5 second delay!)
echo "💳 Step 4: CHECKOUT - Watch it BLOCK! ⏰"
echo "⚠️  This will take 3-5 seconds..."
echo "⚠️  Payment: 1 second delay"
echo "⚠️  Email: 2 seconds delay"
echo "⚠️  Database operations: ~1 second"
echo ""
echo "Starting timer..."
START_TIME=$(date +%s)

curl -s -X POST "$BASE_URL/api/orders/checkout" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": "123 Main St, City, State 12345",
    "payment_method": "credit_card"
  }' | python3 -m json.tool

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo ""
echo "=========================================="
echo "⏱️  TOTAL TIME: $ELAPSED seconds"
echo "😢 User had to WAIT $ELAPSED seconds!"
echo "=========================================="
echo ""

echo "🎓 What You Just Experienced:"
echo "  ✗ Blocking payment processing (1s)"
echo "  ✗ Blocking email sending (2s)"
echo "  ✗ Long database transaction"
echo "  ✗ No async processing"
echo "  ✗ User waits for EVERYTHING"
echo ""
echo "🚀 In Microservices:"
echo "  ✓ Instant response with order ID"
echo "  ✓ Payment processed in background"
echo "  ✓ Email sent asynchronously"
echo "  ✓ User continues shopping immediately"
```

## Manual Testing via Swagger UI

1. **Open API Docs:**
   ```
   http://localhost:8000/docs
   ```

2. **Register a User:**
   - POST `/api/auth/register`
   - Body:
     ```json
     {
       "email": "admin@example.com",
       "password": "admin123",
       "full_name": "Admin User"
     }
     ```

3. **Login:**
   - POST `/api/auth/login`
   - Copy the `access_token` from response

4. **Authorize:**
   - Click "Authorize" button (top right)
   - Enter: `Bearer YOUR_TOKEN_HERE`

5. **Create Category (as admin - manual DB update needed):**
   - First, make your user an admin:
     ```bash
     docker exec -it ecommerce-postgres psql -U ecommerce -d ecommerce_db \
       -c "UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';"
     ```
   - POST `/api/products/categories`
   - Body:
     ```json
     {
       "name": "Electronics",
       "description": "Electronic items"
     }
     ```

6. **Create Product:**
   - POST `/api/products`
   - Body:
     ```json
     {
       "name": "Laptop",
       "description": "Gaming laptop",
       "price": 999.99,
       "category_id": 1,
       "initial_inventory": 10
     }
     ```

7. **Add to Cart:**
   - POST `/api/cart/items`
   - Body:
     ```json
     {
       "product_id": 1,
       "quantity": 2
     }
     ```

8. **CHECKOUT (THE SLOW ONE!):**
   - POST `/api/orders/checkout`
   - Body:
     ```json
     {
       "shipping_address": "123 Main St",
       "payment_method": "credit_card"
     }
     ```
   - ⏰ **WATCH IT TAKE 3-5 SECONDS!**

## What to Observe

### Backend Logs
Watch the terminal where backend is running. You'll see:

```
================================================================================
🛒 [OrderService] Starting order creation...
⚠️  [MONOLITH ALERT] This will BLOCK for 3-5 seconds!
================================================================================

[Step 1/11] Getting user's cart...
✓ Found cart with 2 items

[Step 2/11] Validating cart items and checking inventory...
✓ All items validated. Total: $1999.98

[Step 3/11] Reserving inventory (locking database rows)...
✓ Inventory reserved (rows locked)

[Step 4/11] Creating order record...
✓ Order #1 created

[Step 5/11] Creating order items...
✓ Order items created

[Step 6/11] Processing payment...
💀 BLOCKING OPERATION - Payment gateway call
💳 [PaymentService] Processing payment for order #1
💰 [PaymentService] Amount: $1999.98, Method: credit_card
⏳ [PaymentService] Calling payment gateway... (1s delay)
✅ [PaymentService] Payment successful! Transaction ID: txn_abc123

[Step 7/11] Recording payment...
✓ Payment recorded: txn_abc123

[Step 8/11] Reducing inventory...
✓ Inventory reduced

[Step 9/11] Sending confirmation email...
💀💀 BLOCKING OPERATION - Email sending
📧 [EmailService] Sending email to test@example.com: Order Confirmation #1
⏳ [EmailService] This will take 2 seconds...
✅ [EmailService] Email sent successfully!

[Step 10/11] Creating notification...
✓ Notification created

[Step 11/11] Clearing cart...
✓ Cart cleared

================================================================================
✅ [OrderService] Order #1 created successfully!
⏱️  Total time: 3-5 seconds (user had to WAIT!)
================================================================================
```

### MailHog Email UI
Check sent emails at: http://localhost:8025

You'll see the order confirmation email that took 2 seconds to send!

## The Pain Points You're Experiencing

### 1. Blocking Operations
- Payment API call blocks for 1 second
- Email sending blocks for 2 seconds
- User can't do ANYTHING while waiting

### 2. Tight Coupling
- Order creation depends on:
  - Inventory service
  - Payment service
  - Email service
  - Notification service
- If email fails, entire order fails!

### 3. Single Database Transaction
- Entire process holds database locks
- Other users trying to order are BLOCKED
- Inventory rows are locked for 3-5 seconds

### 4. No Scalability
- Can't scale email service independently
- Can't scale payment service independently
- Must scale ENTIRE monolith

### 5. Poor User Experience
- 3-5 second wait for checkout
- No loading indicators
- No way to continue shopping

## Compare to Microservices Approach

### Monolith (What We Built):
```
User → POST /checkout → [WAIT 3-5 SECONDS] → Order Confirmed
                          ↓
                    Inventory Check
                    Payment Process (1s)
                    Email Send (2s)
                    All or Nothing!
```

### Microservices (Better Way):
```
User → POST /checkout → Order Created (instant!)
         ↓
         Event Bus
         ├→ Payment Service (async, 1s)
         ├→ Email Service (async, 2s)
         ├→ Inventory Service (async)
         └→ Notification Service (async)

User continues shopping immediately!
Order processing happens in background.
```

## Try This: Concurrent Requests

Open two terminal windows and run checkout simultaneously:

**Terminal 1:**
```bash
time curl -X POST http://localhost:8000/api/orders/checkout \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address": "123 Main", "payment_method": "credit_card"}'
```

**Terminal 2 (start immediately after):**
```bash
time curl -X POST http://localhost:8000/api/orders/checkout \
  -H "Authorization: Bearer YOUR_TOKEN2" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address": "456 Oak", "payment_method": "paypal"}'
```

**What Happens:**
- Second request waits for first to complete!
- Database row locks prevent concurrent processing
- Both users wait 3-5 seconds EACH

**In Microservices:**
- Both requests would complete instantly
- Background processing would happen independently
- No blocking, no waiting!

---

## 🎓 Lessons Learned

After testing, you should understand:

1. **Why synchronous operations are bad** - Users wait unnecessarily
2. **Why tight coupling is bad** - Email failure affects orders
3. **Why single database is bad** - Becomes a bottleneck
4. **Why monoliths don't scale** - Can't optimize individual parts
5. **Why microservices exist** - To solve these exact problems!

Now you're ready for **Phase 2: Microservices Decomposition**!

---

**API Documentation:** http://localhost:8000/docs
**Email Viewer:** http://localhost:8025
