"""
Payment integration module
Supports Stripe payment gateway
"""
import stripe
import uuid
from typing import Tuple, Optional, Dict
import config.settings as settings
from modules.database import db


class PaymentError(Exception):
    """Custom exception for payment errors"""
    pass


class PaymentProcessor:
    """Handle payment operations"""
    
    def __init__(self):
        """Initialize payment processor"""
        # Initialize Stripe with API key
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY
        self.currency = settings.PAYMENT_CURRENCY
        self.amount = settings.PAYMENT_AMOUNT
    
    def create_payment_intent(self, user_id: int, 
                             image_filename: str = None) -> Tuple[bool, Optional[str], str]:
        """
        Create a Stripe payment intent
        Returns: (success, payment_intent_id, message)
        """
        try:
            # Create unique transaction ID
            transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
            
            # For demo purposes, simulate successful payment
            # In production, integrate with actual payment gateway
            if not settings.STRIPE_SECRET_KEY or settings.DEBUG:
                # Demo mode - auto-approve payment
                db.create_transaction(
                    user_id=user_id,
                    transaction_id=transaction_id,
                    amount=self.amount / 100,  # Convert cents to dollars
                    image_filename=image_filename,
                    payment_method="demo"
                )
                db.update_transaction_status(transaction_id, "completed")
                return True, transaction_id, "Payment successful (Demo Mode)"
            
            # Real Stripe integration
            intent = stripe.PaymentIntent.create(
                amount=self.amount,
                currency=self.currency,
                metadata={
                    'user_id': user_id,
                    'transaction_id': transaction_id,
                    'image_filename': image_filename
                }
            )
            
            # Store transaction in database
            db.create_transaction(
                user_id=user_id,
                transaction_id=transaction_id,
                amount=self.amount / 100,
                image_filename=image_filename,
                payment_method="stripe"
            )
            
            return True, intent.id, "Payment intent created"
            
        except stripe.error.StripeError as e:
            return False, None, f"Payment error: {str(e)}"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    def confirm_payment(self, payment_intent_id: str) -> Tuple[bool, str]:
        """
        Confirm payment completion
        Returns: (success, message)
        """
        try:
            # Demo mode - always confirm
            if not settings.STRIPE_SECRET_KEY or settings.DEBUG:
                # Update transaction status
                db.update_transaction_status(payment_intent_id, "completed")
                return True, "Payment confirmed"
            
            # Real Stripe confirmation
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                # Update transaction in database
                transaction_id = intent.metadata.get('transaction_id')
                if transaction_id:
                    db.update_transaction_status(transaction_id, "completed")
                return True, "Payment confirmed"
            else:
                return False, f"Payment status: {intent.status}"
                
        except stripe.error.StripeError as e:
            return False, f"Payment confirmation error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def process_demo_payment(self, user_id: int, 
                           image_filename: str = None) -> Tuple[bool, str, str]:
        """
        Process a demo payment (for testing without actual payment gateway)
        Returns: (success, transaction_id, message)
        """
        try:
            # Generate transaction ID
            transaction_id = f"demo_{uuid.uuid4().hex[:16]}"
            
            # Create transaction record
            db.create_transaction(
                user_id=user_id,
                transaction_id=transaction_id,
                amount=settings.DOWNLOAD_PRICE,
                image_filename=image_filename,
                payment_method="demo"
            )
            
            # Mark as completed
            db.update_transaction_status(transaction_id, "completed")
            
            return True, transaction_id, "Demo payment processed successfully"
            
        except Exception as e:
            return False, "", f"Demo payment error: {str(e)}"
    
    def verify_payment(self, transaction_id: str) -> bool:
        """
        Verify if a transaction is completed
        Returns: True if payment is verified, False otherwise
        """
        transaction = db.get_transaction_by_id(transaction_id)
        if transaction and transaction['status'] == 'completed':
            return True
        return False
    
    def get_user_purchase_history(self, user_id: int) -> list:
        """Get user's purchase history"""
        return db.get_user_transactions(user_id)
    
    @staticmethod
    def create_payment_link(amount: float, description: str = None) -> str:
        """
        Create a payment link (for future implementation)
        """
        # Placeholder for creating shareable payment links
        return f"https://payment.toonify.com/pay?amount={amount}"
    
    @staticmethod
    def format_price(amount: float, currency: str = "USD") -> str:
        """Format price for display"""
        symbols = {
            "usd": "$",
            "eur": "€",
            "gbp": "£",
            "inr": "₹"
        }
        symbol = symbols.get(currency.lower(), "$")
        return f"{symbol}{amount:.2f}"
    
    def get_payment_status_message(self, status: str) -> str:
        """Get user-friendly payment status message"""
        messages = {
            "pending": "⏳ Payment pending",
            "processing": "🔄 Processing payment",
            "completed": "✅ Payment completed",
            "failed": "❌ Payment failed",
            "refunded": "↩️ Payment refunded"
        }
        return messages.get(status, "Unknown status")


import razorpay

# Real Razorpay Processor
class RazorpayProcessor:
    """Razorpay payment processor for secure checkouts"""
    
    def __init__(self):
        """Initialize Razorpay Client"""
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret)) if self.key_id else None
    
    def create_order(self, amount: float, user_id: int, 
                    image_filename: str = None) -> Tuple[bool, Optional[Dict], str]:
        """Create a Razorpay order"""
        try:
            if not self.client:
                # Return demo order if no keys
                return True, {
                    "id": f"order_demo_{uuid.uuid4().hex[:12]}",
                    "amount": int(amount * 100),
                    "currency": "INR",
                    "notes": {"user_id": user_id, "image": image_filename}
                }, "Demo order created (Keys missing)"

            # Standard Razorpay Order creation
            order_data = {
                "amount": int(amount * 100),  # In Paise
                "currency": "INR",
                "receipt": f"rcpt_{uuid.uuid4().hex[:12]}",
                "notes": {
                    "user_id": user_id,
                    "image_filename": image_filename
                }
            }
            order = self.client.order.create(data=order_data)
            
            # Save pending transaction
            db.create_transaction(
                user_id=user_id,
                transaction_id=order['id'],
                amount=amount,
                image_filename=image_filename,
                payment_method="razorpay"
            )
            
            return True, order, "Order created successfully"
            
        except Exception as e:
            return False, None, f"Razorpay order error: {str(e)}"

    def verify_payment(self, razorpay_order_id: str, 
                      razorpay_payment_id: str, 
                      razorpay_signature: str) -> bool:
        """Verify the payment signature from Razorpay callback"""
        try:
            if not self.client:
                # Demo auto-verification
                db.update_transaction_status(razorpay_order_id, "completed")
                return True

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            self.client.utility.verify_payment_signature(params_dict)
            
            # Mark transaction as completed
            db.update_transaction_status(razorpay_order_id, "completed")
            return True
            
        except Exception:
            return False

    def get_order_details(self, order_id: str) -> Optional[Dict]:
        """Fetch order details from Razorpay"""
        try:
            return self.client.order.fetch(order_id) if self.client else None
        except Exception:
            return None


# Global payment processor instance
payment_processor = PaymentProcessor()
razorpay_processor = RazorpayProcessor()
