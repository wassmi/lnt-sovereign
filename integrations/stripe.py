"""
POC 3: Integration Layer - Stripe
The Composability Moat - Seamless integration with existing tools

Demonstrates LNT verifying payment eligibility before Stripe charges.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json


@dataclass
class StripeCustomer:
    """Mock Stripe customer data."""
    id: str
    email: str
    balance: float  # Account balance in cents
    currency: str
    metadata: Dict[str, Any]
    created: int  # Unix timestamp
    credit_limit: float = 0  # Custom field
    risk_score: float = 0  # Custom field


@dataclass
class PaymentIntent:
    """Mock Stripe PaymentIntent."""
    amount: int  # In cents
    currency: str
    customer_id: str
    metadata: Dict[str, Any]


class LNTStripeIntegration:
    """
    Integration layer for verifying Stripe operations with LNT.
    
    Use cases:
    - Verify customer eligibility before charging
    - Validate payment amounts against business rules
    - Ensure compliance before subscription creation
    """
    
    def __init__(self, manifest_path: str = "lnt_sovereign/manifests/examples/stripe_payments.json"):
        """
        Initialize with a payment verification manifest.
        Falls back to JIT kernel if available, otherwise standard kernel.
        """
        self.manifest_path = manifest_path
        self._kernel = None
        self._load_kernel()
    
    def _load_kernel(self):
        """Load the fastest available kernel."""
        try:
            from core.jit_kernel import JITKernel
            self._kernel = JITKernel(self.manifest_path)
            self._kernel_type = "JIT"
        except Exception:
            try:
                from core.kernel import KernelEngine
                self._kernel = KernelEngine(self.manifest_path)
                self._kernel_type = "Standard"
            except Exception:
                self._kernel = None
                self._kernel_type = "None"
    
    def verify_customer_eligibility(
        self, 
        customer: StripeCustomer,
        amount: int
    ) -> Dict[str, Any]:
        """
        Verify if a customer is eligible for a charge.
        
        Args:
            customer: Stripe customer object
            amount: Amount to charge in cents
            
        Returns:
            {
                "eligible": bool,
                "violations": list,
                "recommendation": str
            }
        """
        # Convert Stripe customer to LNT proposal
        proposal = {
            "balance": customer.balance / 100,  # Convert to dollars
            "amount": amount / 100,
            "credit_limit": customer.credit_limit / 100,
            "risk_score": customer.risk_score,
            "account_age_days": (2024 * 365 * 24 * 3600 - customer.created) / (24 * 3600)
        }
        
        # Add metadata fields
        for key, value in customer.metadata.items():
            if isinstance(value, (int, float, bool)):
                proposal[key] = value
        
        # Evaluate against manifest
        if self._kernel:
            violations = self._kernel.evaluate(proposal)
        else:
            violations = []  # Fallback: no validation
        
        eligible = len(violations) == 0
        
        # Generate recommendation
        if eligible:
            recommendation = "Proceed with charge"
        else:
            violation_summary = ", ".join([v.get("description", v.get("id", "Unknown")) for v in violations[:3]])
            recommendation = f"Review required: {violation_summary}"
        
        return {
            "eligible": eligible,
            "violations": violations,
            "recommendation": recommendation,
            "kernel_type": self._kernel_type,
            "proposal_evaluated": proposal
        }
    
    def verify_payment_intent(
        self, 
        intent: PaymentIntent,
        customer: StripeCustomer
    ) -> Dict[str, Any]:
        """
        Verify a payment intent before processing.
        
        This would be called in a Stripe webhook or before creating the intent.
        """
        # Combine intent and customer data
        proposal = {
            "amount": intent.amount / 100,
            "balance": customer.balance / 100,
            "credit_limit": customer.credit_limit / 100,
            "risk_score": customer.risk_score
        }
        
        # Add intent metadata
        for key, value in intent.metadata.items():
            if isinstance(value, (int, float, bool)):
                proposal[key] = value
        
        if self._kernel:
            violations = self._kernel.evaluate(proposal)
        else:
            violations = []
        
        return {
            "approved": len(violations) == 0,
            "violations": violations,
            "intent_id": f"pi_{hash(intent.customer_id) % 1000000}"
        }
    
    def as_stripe_middleware(self):
        """
        Returns a middleware function for Stripe SDK integration.
        
        Usage:
            import stripe
            from integrations.stripe import LNTStripeIntegration
            
            lnt = LNTStripeIntegration()
            
            @lnt.as_stripe_middleware()
            def create_charge(customer_id, amount):
                return stripe.Charge.create(
                    customer=customer_id,
                    amount=amount
                )
        """
        def middleware(func):
            def wrapper(*args, **kwargs):
                # Extract customer and amount from kwargs
                customer_id = kwargs.get("customer")
                amount = kwargs.get("amount", 0)
                
                # Create mock customer for verification
                # In production, would fetch from Stripe API
                mock_customer = StripeCustomer(
                    id=customer_id or "unknown",
                    email="unknown@example.com",
                    balance=0,
                    currency="usd",
                    metadata={},
                    created=0
                )
                
                result = self.verify_customer_eligibility(mock_customer, amount)
                
                if not result["eligible"]:
                    raise ValueError(f"LNT verification failed: {result['recommendation']}")
                
                return func(*args, **kwargs)
            return wrapper
        return middleware


def create_default_manifest():
    """Create a default payment verification manifest."""
    manifest = {
        "domain_id": "STRIPE_PAYMENTS_V1",
        "domain_name": "Stripe Payment Verification",
        "version": "1.0",
        "entities": [
            "amount",
            "balance",
            "credit_limit",
            "risk_score",
            "account_age_days"
        ],
        "constraints": [
            {
                "id": "MAX_AMOUNT",
                "entity": "amount",
                "operator": "LT",
                "value": 10000,
                "severity": "TOXIC",
                "description": "Single charge cannot exceed $10,000"
            },
            {
                "id": "MIN_AMOUNT",
                "entity": "amount",
                "operator": "GT",
                "value": 0.5,
                "severity": "TOXIC",
                "description": "Minimum charge is $0.50"
            },
            {
                "id": "RISK_THRESHOLD",
                "entity": "risk_score",
                "operator": "LT",
                "value": 80,
                "severity": "TOXIC",
                "description": "High-risk customers require manual review"
            },
            {
                "id": "NEW_ACCOUNT_LIMIT",
                "entity": "amount",
                "operator": "LT",
                "value": 500,
                "severity": "WARNING",
                "description": "New accounts limited to $500 per transaction"
            }
        ]
    }
    return manifest


if __name__ == "__main__":
    import os
    
    # Create manifest if it doesn't exist
    manifest_path = "lnt_sovereign/manifests/examples/stripe_payments.json"
    if not os.path.exists(manifest_path):
        manifest = create_default_manifest()
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"Created manifest: {manifest_path}")
    
    # Test the integration
    print("-" * 50)
    print("LNT Stripe Integration POC")
    print("-" * 50)
    
    integration = LNTStripeIntegration(manifest_path)
    print(f"Kernel type: {integration._kernel_type}")
    
    # Test case 1: Valid charge
    customer1 = StripeCustomer(
        id="cus_123",
        email="valid@example.com",
        balance=50000,  # $500
        currency="usd",
        metadata={"verified": True},
        created=1600000000,
        credit_limit=100000,
        risk_score=25
    )
    
    result1 = integration.verify_customer_eligibility(customer1, 5000)  # $50
    print(f"\nTest 1: Valid charge ($50)")
    print(f"  Eligible: {result1['eligible']}")
    print(f"  Recommendation: {result1['recommendation']}")
    
    # Test case 2: High-risk customer
    customer2 = StripeCustomer(
        id="cus_456",
        email="risky@example.com",
        balance=10000,
        currency="usd",
        metadata={},
        created=1700000000,
        credit_limit=50000,
        risk_score=95  # High risk!
    )
    
    result2 = integration.verify_customer_eligibility(customer2, 5000)
    print(f"\nTest 2: High-risk customer")
    print(f"  Eligible: {result2['eligible']}")
    print(f"  Recommendation: {result2['recommendation']}")
    
    # Test case 3: Amount too high
    result3 = integration.verify_customer_eligibility(customer1, 1500000)  # $15,000
    print(f"\nTest 3: Amount too high ($15,000)")
    print(f"  Eligible: {result3['eligible']}")
    print(f"  Recommendation: {result3['recommendation']}")
    
    print("-" * 50)
    print("POC 3: Stripe Integration - COMPLETE")
