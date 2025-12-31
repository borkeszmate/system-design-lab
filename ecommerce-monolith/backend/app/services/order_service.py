"""
Order Service - The MONOLITH NIGHTMARE!

This is the crown jewel of monolith anti-patterns:
- Everything happens synchronously in ONE transaction
- Blocks for 3-5 seconds on EVERY order!
- If ANY step fails, EVERYTHING rolls back
- Inventory, payment, email all tightly coupled
- User waits for EVERYTHING to complete

In microservices, this would be:
- Event-driven architecture
- Saga pattern for distributed transactions
- Async message queues
- Each service independent
- Eventual consistency
- User gets instant response, processing happens in background
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import time

from app.models.order import Order, OrderItem, Payment, OrderStatus
from app.models.cart import Cart, CartItem
from app.models.product import Inventory
from app.models.review import Notification
from app.services.email_service import EmailService
from app.services.payment_service import PaymentService


class OrderService:
    """
    Order processing service - demonstrates ALL monolith pain points!
    """

    @staticmethod
    def create_order_from_cart(
        db: Session,
        user_id: int,
        shipping_address: str,
        payment_method: str
    ) -> Order:
        """
        Create an order from a user's cart.

        This is the NIGHTMARE SCENARIO that demonstrates why monoliths are painful!

        What happens here (ALL SYNCHRONOUSLY):
        1. Get user's cart ← Database query
        2. Validate cart items ← Database queries
        3. Check inventory for ALL items ← Database queries + row locks!
        4. Reserve inventory ← Database updates
        5. Create order record ← Database insert
        6. Process payment ← BLOCKS for 1 second! 💀
        7. Update order status ← Database update
        8. Reduce inventory ← Database updates
        9. Send confirmation email ← BLOCKS for 2 seconds! 💀
        10. Create notification ← Database insert
        11. Clear cart ← Database delete

        Total blocking time: 3-5 seconds!

        Problems:
        - User waits for email to be sent!
        - If email fails, entire order fails
        - Database transaction held for 3-5 seconds
        - All other orders blocked during this time (row locks)
        - No way to scale email or payment independently
        """

        # Start timing
        start_time = time.time()

        print("\n" + "="*80)
        print("🛒 [OrderService] Starting order creation...")
        print("⚠️  [MONOLITH ALERT] This will BLOCK for 3-5 seconds!")
        print("="*80 + "\n")

        try:
            # Step 1: Get user's cart
            print("[Step 1/11] Getting user's cart...")
            cart = db.query(Cart).filter(Cart.user_id == user_id).first()

            if not cart or not cart.items:
                raise ValueError("Cart is empty")

            print(f"✓ Found cart with {len(cart.items)} items")

            # Step 2 & 3: Validate cart and check inventory
            print("[Step 2/11] Validating cart items and checking inventory...")
            total_amount = 0

            for cart_item in cart.items:
                # Check inventory
                inventory = db.query(Inventory).filter(
                    Inventory.product_id == cart_item.product_id
                ).first()

                if not inventory or inventory.available < cart_item.quantity:
                    raise ValueError(f"Insufficient stock for product {cart_item.product_id}")

                total_amount += float(cart_item.price_snapshot) * cart_item.quantity

            print(f"✓ All items validated. Total: ${total_amount:.2f}")

            # Step 4: Reserve inventory (pessimistic locking!)
            print("[Step 3/11] Reserving inventory (locking database rows)...")
            for cart_item in cart.items:
                inventory = db.query(Inventory).filter(
                    Inventory.product_id == cart_item.product_id
                ).with_for_update().first()  # Row-level lock!

                inventory.reserved_quantity += cart_item.quantity

            db.flush()  # Write to DB but don't commit yet
            print(f"✓ Inventory reserved (rows locked)")

            # Step 5: Create order record
            print("[Step 4/11] Creating order record...")
            order = Order(
                user_id=user_id,
                status=OrderStatus.PENDING,
                total_amount=total_amount,
                shipping_address=shipping_address
            )
            db.add(order)
            db.flush()  # Get order ID
            print(f"✓ Order #{order.id} created")

            # Step 6: Create order items
            print("[Step 5/11] Creating order items...")
            for cart_item in cart.items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price_snapshot=cart_item.price_snapshot
                )
                db.add(order_item)

            db.flush()
            print(f"✓ Order items created")

            # Step 7: Process payment - BLOCKS FOR 1 SECOND! 💀
            print("[Step 6/11] Processing payment...")
            print("💀 BLOCKING OPERATION - Payment gateway call")

            success, status, transaction_id = PaymentService.process_payment(
                order_id=order.id,
                amount=total_amount,
                payment_method=payment_method
            )

            if not success:
                raise ValueError("Payment failed")

            # Step 8: Create payment record
            print("[Step 7/11] Recording payment...")
            payment = Payment(
                order_id=order.id,
                amount=total_amount,
                status=status,
                payment_method=payment_method,
                transaction_id=transaction_id
            )
            db.add(payment)
            order.status = OrderStatus.PAID
            db.flush()
            print(f"✓ Payment recorded: {transaction_id}")

            # Step 9: Reduce inventory
            print("[Step 8/11] Reducing inventory...")
            for cart_item in cart.items:
                inventory = db.query(Inventory).filter(
                    Inventory.product_id == cart_item.product_id
                ).first()

                inventory.quantity -= cart_item.quantity
                inventory.reserved_quantity -= cart_item.quantity

            db.flush()
            print(f"✓ Inventory reduced")

            # Step 10: Send confirmation email - BLOCKS FOR 2 SECONDS! 💀💀
            print("[Step 9/11] Sending confirmation email...")
            print("💀💀 BLOCKING OPERATION - Email sending")

            from app.models.user import User
            user = db.query(User).filter(User.id == user_id).first()

            email_sent = EmailService.send_order_confirmation(
                order_id=order.id,
                user_email=user.email,
                total=float(total_amount)
            )

            if not email_sent:
                # In monolith, we might want to rollback everything if email fails!
                # But that would be ridiculous... so we just log it
                print("⚠️  Email failed but continuing anyway")

            # Step 11: Create notification
            print("[Step 10/11] Creating notification...")
            notification = Notification(
                user_id=user_id,
                type="order_confirmation",
                message=f"Your order #{order.id} has been confirmed!",
                read=0
            )
            db.add(notification)
            db.flush()
            print(f"✓ Notification created")

            # Step 12: Clear cart
            print("[Step 11/11] Clearing cart...")
            db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
            db.flush()
            print(f"✓ Cart cleared")

            # Calculate and save processing duration
            end_time = time.time()
            duration_ms = int((end_time - start_time) * 1000)
            order.processing_duration_ms = duration_ms

            # Commit everything!
            db.commit()
            db.refresh(order)

            print("\n" + "="*80)
            print(f"✅ [OrderService] Order #{order.id} created successfully!")
            print(f"⏱️  Total time: {duration_ms}ms ({duration_ms/1000:.2f}s) - user had to WAIT!")
            print("="*80 + "\n")

            return order

        except Exception as e:
            # Rollback EVERYTHING if any step fails!
            db.rollback()
            print("\n" + "="*80)
            print(f"❌ [OrderService] Order creation FAILED: {e}")
            print("🔄 Rolling back ENTIRE transaction")
            print("="*80 + "\n")
            raise

    @staticmethod
    def get_order(db: Session, order_id: int, user_id: int) -> Optional[Order]:
        """Get an order by ID"""
        return db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user_id
        ).first()

    @staticmethod
    def list_user_orders(db: Session, user_id: int, skip: int = 0, limit: int = 20):
        """List all orders for a user"""
        return db.query(Order).filter(
            Order.user_id == user_id
        ).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_order_status(db: Session, order_id: int, status: OrderStatus) -> Order:
        """Update order status (admin only)"""
        order = db.query(Order).filter(Order.id == order_id).first()

        if not order:
            raise ValueError("Order not found")

        order.status = status
        db.commit()
        db.refresh(order)

        # Optionally send notification
        if status == OrderStatus.SHIPPED:
            from app.models.user import User
            user = db.query(User).filter(User.id == order.user_id).first()
            EmailService.send_shipping_notification(order.id, user.email)

        return order
