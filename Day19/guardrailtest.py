from pydantic import BaseModel, Field, ValidationError
import logging
import uuid
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    start = time.perf_counter()
    trace_id = str(uuid.uuid4())[:8]
    logger.info(f"{trace_id} : Refund request received")

    logger.info(f"{trace_id} : Tool called : validate_refund")
    logger.info(f"{trace_id} : tool arguments are :"
                f"customer_id: {customer_id} amount: {amount} user_role: {user_role}"
            )
    try:
        result = RefundRequest(
            customer_id=customer_id,
            amount=amount,
            reason="Customer requested a refund"
        )
    except ValidationError as e:
        logger.warning(f"{trace_id} Tool re : REJECTED_SCHEMA_VALIDATION")
        return("REFUND REJECTED : Invalid request input")

    purchase_amount = purchases[customer_id]
    authorization_limit = authorization_limits[user_role]

    logger.info(f"{trace_id} : Validation check started")
    if result.amount > purchase_amount:
        logger.info(f"{trace_id} : Tool result : REJECTED_VALIDATION")
        return("REFUND REJECTED: Requested amount exceeds original purchase amount.")
    logger.info(f"{trace_id} : validation passed")

    logger.info(f"{trace_id} : Authorization check started")
    if result.amount > authorization_limit:
        logger.info(f"{trace_id} : Tool result: REJECTED_AUTHORIZATION")
        return(f"REFUND REJECTED : Refund amount can't be authorized by {user_role}. It is above the role limit")
    logger.info(f"{trace_id} : Authorization check passed")

    logger.info(f"{trace_id} : refund execution started")
    logger.info(f"{trace_id} : Refund executed")
    logger.info(f"{trace_id} : Tool result : REFUND_APPROVED")
    duration = time.perf_counter() - start
    logger.info(f"{trace_id} : Refund was processed in {duration:.4f}secs")
    return("REFUND APPROVED : Refund will be processed")

result = validate_refund("CUST-101", "banana", "support_agent")
print(result)