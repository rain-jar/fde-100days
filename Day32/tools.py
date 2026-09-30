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


#SIMULATION_DB_FAILURE = False
SIMULATION_DB_FAILURE = os.getenv("SIMULATION_DB_FAILURE","false").lower() == "true"
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

#Application level authorization
current_user = {
    "user_id" : "USER-101",
    "allowed_customers" : ["Acme"]
}

#FOR USER AUTHORIZATION
USERS = {
    "USER-101": {
        "role": "support_agent",
        "allowed_customers": ["Acme"]
    },
    "USER-102": {
        "role": "manager",
        "allowed_customers": ["Acme", "Globex"]
    }
}

purchase_details = {
    "Acme": {
        "purchase_amount": 5000
    },
    "Globex": {
        "purchase_amount": 8000
    }
}

def isauthorized(user_id,customer_name):
    user = USERS.get(user_id)

    if not user:
        return False

    return customer_name in user["allowed_customers"]



def get_customer_plan(customer_name,trace_id,user_id):
    gcp_timer = time.perf_counter()
    if not isauthorized(user_id,customer_name):
        gcp_end = time.perf_counter() - gcp_timer
        print(f"GET_CUSTOMER_PLAN LATENCY - : {gcp_end}")
        logger.warning(f"{trace_id}: AUTHORIZATION : user_id ={user_id}, customer={customer_name} result = ACCESS_DENIED ")
        return {
            "status": "ACCESS_DENIED"
        }
    
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        SELECT plan FROM customers 
                        WHERE name = %s
                    """,(customer_name,)
                )
                gcp_end = time.perf_counter() - gcp_timer
                print(f"GET_CUSTOMER_PLAN LATENCY - : {gcp_end}seconds")
                plan = cur.fetchone()
                if plan is None:
                    return ("Database READ_ERROR: Customer does not exist")
                return plan[0] #Because fetchone() returns a tuple like ('Enterprise',)
    
    except psycopg.OperationalError:
        gcp_end = time.perf_counter() - gcp_timer
        print(f"GET_CUSTOMER_PLAN LATENCY - : {gcp_end}")
        return("Database READ_ERROR: Customer database unavailable")

def get_customer(customer_name,trace_id,user_id):
    gc_timer = time.perf_counter()
    if not isauthorized(user_id,customer_name):
        gc_end = time.perf_counter() - gc_timer
        print(f"GET_CUSTOMER LATENCY - : {gc_end}seconds")
        logger.warning(
            f"{trace_id} : AUTHORIZATION : "
            f"user_id={user_id} "
            f"customer = {customer_name}"
            f"action=get_customer "
            f"result=ACCESS_DENIED"
        )

        return {
            "status" : "ACCESS_DENIED",
            "customer" : None,
            "error" : "USER_NOT_AUTHORIZED"
        }

    global SIMULATION_DB_FAILURE
    if SIMULATION_DB_FAILURE:
        return {
            "status": "DEPENDENCY_ERROR", 
            "customer": None,
            "error": "CUSTOMER_DATABASE_UNAVAILABLE"
        }

    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                        SELECT name, plan
                        FROM customers
                        WHERE name = %s
                    """,
                    (customer_name,)
                )
                gc_end = time.perf_counter() - gc_timer
                print(f"GET_CUSTOMER LATENCY - : {gc_end}seconds")
                row = cur.fetchone()

                if row is None:
                    return {
                        "status": "NOT_FOUND",
                        "customer": None,
                        "error": "CUSTOMER_NOT_FOUND"
                    }

                return {
                    "status" : "SUCCESS",
                    "customer" : {
                        "name" : row[0],
                        "plan" : row[1]
                    },
                    "error" : None
                }
    
    except psycopg.OperationalError:
        gc_end = time.perf_counter() - gc_timer
        print(f"GET_CUSTOMER LATENCY - : {gc_end}seconds")
        return {
            "status": "DEPENDENCY_ERROR",
            "customer": None,
            "error": "CUSTOMER_DATABASE_UNAVAILABLE"
        }

def get_customer_details(customer_name,trace_id,user_id):
    gcd_timer = time.perf_counter()
    if not isauthorized(user_id,customer_name):
        gcd_end = time.perf_counter() - gcd_timer
        print(f"GET_CUSTOMER_DETAILS LATENCY - : {gcd_end}seconds")
        logger.warning(
            f"{trace_id} : AUTHORIZATION : "
            f"user_id={user_id} "
            f"customer = {customer_name}"
            f"action=get_customer_details "
            f"result=ACCESS_DENIED"
        )
        return {
            "status": "ACCESS_DENIED"
        }
    
    global SIMULATION_DB_FAILURE
    if SIMULATION_DB_FAILURE:
        raise ConnectionError (
            "Customer database temporarily unavailable"
        )

    with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT name, plan
                    FROM customers
                    WHERE name = %s
                    """,
                    (customer_name,)
                )

                details = cur.fetchone()
                gcd_end = time.perf_counter() - gcd_timer
                print(f"GET_CUSTOMER_DETAILS LATENCY - : {gcd_end}seconds")

                if details is None:
                    return {
                        "status": "NOT_FOUND"
                    }

                return {
                    "status": "SUCCESS",
                    "customer_name": details[0],
                    "plan": details[1]
                }



def get_open_tickets(customer_name,trace_id,user_id):
    got_timer = time.perf_counter()
    if not isauthorized(user_id,customer_name):
        got_end = time.perf_counter() - got_timer
        print(f"GET_OPEN_TICKETS LATENCY - : {got_end}seconds")
        logger.warning(
            f"{trace_id} : AUTHORIZATION : "
            f"user_id={user_id} "
            f"customer = {customer_name}"
            f"action=get_open_tickets "
            f"result=ACCESS_DENIED"
        )
        return {
            "status": "ACCESS_DENIED",
            "open_tickets": [],
            "error": "USER_NOT_AUTHORIZED"
        }

    try:
        with psycopg.connect(DATABASE_URL) as conn2:
                with conn2.cursor() as cur2:
                    cur2.execute(
                        """
                            SELECT ticket_id, customer_name, issue, priority, status
                            FROM tickets
                            WHERE customer_name = %s
                            AND status = 'open'
                        """,(customer_name,)
                    )  
                    tickets = cur2.fetchall()

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

                    got_end = time.perf_counter() - got_timer
                    print(f"GET_OPEN_TICKETS LATENCY - : {got_end}seconds")
                    return {
                        "status": "SUCCESS",
                        "open_tickets": structured_tickets,
                        "error": None
                    }

    except psycopg.OperationalError:
        got_end = time.perf_counter() - got_timer
        print(f"GET_OPEN_TICKETS LATENCY - : {got_end}seconds")
        return {
            "status": "DEPENDENCY_ERROR",
            "open_tickets": [],
            "error": "TICKETS_DATABASE_UNAVAILABLE"
        }


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

def create_refund(customer_name,amount,trace_id,user_id):
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
        return{
            "status": "REJECTED",
            "error": "INVALID_INPUT"
        }



    #Business Logic Validation Check
    logging.info(f"{trace_id}: VALIDATION : STARTED")
    #purchase_details = get_customer_details(customer_name,trace_id)
    purchase_info = purchase_details.get(customer_name)

    #Condition for an unknown customer
    if purchase_info is None:
        logger.warning(f"{trace_id} Tool result : REJECTED_BUSINESS_RULE")
        return{
            "status": "REJECTED",
            "error": "CUSTOMER_NOT_FOUND"
        }
    
    if result.amount > purchase_info["purchase_amount"]:
        logger.warning(f"{trace_id} Tool result : REJECTED_BUSINESS_RULE")
        return{
            "status": "REJECTED",
            "error": "AMOUNT_EXCEEDS_PURCHASE"
        }
    
    logging.info(f"{trace_id}: VALIDATION : PASSED")


    #Authorization Check
    logging.info(f"{trace_id}: AUTHORIZATION : {result.user_role}")
    authorization_limit = authorization_limits[result.user_role]
    if result.amount > authorization_limit:
        logging.info(f"{trace_id}: AUTHORIZATION : FAILED")
        logger.warning(f"{trace_id} Tool result : REJECTED_AUTHORIZATION")
        return{
            "status": "REJECTED",
            "error": "NOT_AUTHORIZED"
        }

    logger.info(f"{trace_id} : Tool result : REFUND_APPROVED")
    # duration = time.perf_counter() - start
    #logger.info(f"{trace_id} : Refund was processed in {duration:.4f}secs")
    return{
        "status": "APPROVED",
        "error": None
    }

# result = create_refund("Globex", "-50", "manager")
# #print(result)

#print(get_customer_details("Globex"))

#print(get_customer_plan("Globex","1234"))

# print(get_customer_details("Globex", "test-123"))
# print(get_customer_details("Acme", "test-123"))


#print(get_customer("Umbrella", "security-test-001"))

