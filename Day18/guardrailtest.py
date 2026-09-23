from pydantic import BaseModel, Field

purchases = {
    "CUST-101": 350.00,
    "CUST-102": 1200.00
}

authorization_limits = {
    "support_agent": 100,
    "manager": 10000
}

class RefundRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    amount: float = Field(gt=0, le=10000)
    reason: str = Field(min_length=10)


def validate_refund(customer_id,amount, user_role):
    result = RefundRequest(
        customer_id=customer_id,
        amount=amount,
        reason="Customer requested a refund"
    )

    purchase_amount = purchases[customer_id]
    authorization_limit = authorization_limits[user_role]

    if result.amount > purchase_amount:
        return("REFUND REJECTED: Requested amount exceeds original purchase amount.")
    elif result.amount > authorization_limit:
        return(f"REFUND REJECTED : Refund amount can't be authorized by {user_role}. It is above the role limit")
    else:
        return("REFUND APPROVED : Refund will be processed")

result = validate_refund("CUST-101", 5000, "support_agent")
print(result)