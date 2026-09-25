import database
import sqlite3
from pydantic import BaseModel, Field,ValidationError
import logging
import uuid
import time
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

connection = sqlite3.connect("customers.db")
cursor = connection.cursor()

connection2 = sqlite3.connect("tickets.db")
cursor2 = connection2.cursor()


SIMULATION_DB_FAILURE = False
# #SQLITE version
# def get_customer_plan(customer_name,trace_id):
#     cursor.execute(
#         """
#         SELECT plan FROM customers 
#         WHERE customer_name = ?
#         """,(customer_name,)
#     )
#     plan = cursor.fetchone()
#     if plan is None:
#         return ("Database READ_ERROR: Customer does not exist")
#     return plan[0] #Because fetchone() returns a tuple like ('Enterprise',)

#PostgreSQL version
def get_customer_plan(customer_name,trace_id):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                    SELECT plan FROM customers 
                    WHERE name = %s
                """,(customer_name,)
            )
            plan = cur.fetchone()
            if plan is None:
                return ("Database READ_ERROR: Customer does not exist")
            return plan[0] #Because fetchone() returns a tuple like ('Enterprise',)


def get_customer_details(customer_name,trace_id):
    global SIMULATION_DB_FAILURE

    if SIMULATION_DB_FAILURE:
        raise ConnectionError (
            "Customer database temporarily unavailable"
        )
    
    cursor.execute(
        """
            SELECT * FROM customers
            WHERE customer_name = ?
        """,(customer_name,)
    )
    details = cursor.fetchone()
    if details is None:
        return ("Database READ_ERROR: Customer does not exist")

    structure_detail = {
            "customer_name" : details[0],
            "plan" : details[1],
            "purchase_amount" : details[2],
            "purchase_item" : details[3],
            "purchase_date": details[4]
    }
    return structure_detail

def get_open_tickets(customer_name,trace_id):
    cursor2.execute(
        """
            SELECT * FROM tickets
            WHERE customer_name = ?
        """,(customer_name,)
    )
    tickets = cursor2.fetchall()
    structured_tickets = []
    for ticket in tickets:
        structured_tickets.append(
            {
                "ticket_id" : ticket[0],
                "customer_name": ticket[1],
                "issue": ticket[2],
                "priority" : ticket[3],
                "status": ticket[4]
            }
        )
    return structured_tickets

authorization_limits = {
    "support_agent": 100,
    "manager": 500
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CURRENT_USER_ROLE = "support_agent"

class RefundRequest(BaseModel):
    customer_name : str = Field(min_length=1)
    amount : float = Field(gt=0, le=10000)
    reason : str = Field(min_length=10)
    user_role : str = Field(min_length=1)

def create_refund(customer_name,amount,trace_id):
    # start = time.perf_counter()
    # trace_id = str(uuid.uuid4())[:8]

    #Schema Validation Check
    try:
        result = RefundRequest(
            customer_name=customer_name,
            amount=amount,
            reason="Customer requested a reason",
            user_role=CURRENT_USER_ROLE
        )
    except ValidationError as e:
        logger.warning(f"{trace_id} Tool result : REJECTED_SCHEMA_VALIDATION")
        return("REFUND_REJECTED : Invalid request input")

    #Business Logic Validation Check
    logging.info(f"{trace_id}: VALIDATION : STARTED")
    purchase_details = get_customer_details(customer_name,trace_id)
    if result.amount > purchase_details["purchase_amount"]:
        logger.warning(f"{trace_id} Tool result : REJECTED_BUSINESS_RULE")
        return(("REJECTED_BUSINESS_RULE: Requested amount exceeds original purchase amount."))
    logging.info(f"{trace_id}: VALIDATION : PASSED")

    #Authorization Check
    logging.info(f"{trace_id}: AUTHORIZATION : {result.user_role}")
    authorization_limit = authorization_limits[result.user_role]
    if result.amount > authorization_limit:
        logging.info(f"{trace_id}: AUTHORIZATION : FAILED")
        logger.warning(f"{trace_id} Tool result : REJECTED_AUTHORIZATION")
        return(f"REJECTED_AUTHORIZATION : Refund amount can't be authorized by {result.user_role}. It is above the role limit")

    logger.info(f"{trace_id} : Tool result : REFUND_APPROVED")
    # duration = time.perf_counter() - start
    #logger.info(f"{trace_id} : Refund was processed in {duration:.4f}secs")
    return("REFUND_APPROVED : Refund will be processed")

# result = create_refund("Globex", "-50", "manager")
# #print(result)

#print(get_customer_details("Globex"))

#print(get_customer_plan("Globex","1234"))
