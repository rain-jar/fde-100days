from openai import OpenAI
import sqlite3
import json

client = OpenAI()



#Customer Database - Persistent
connection = sqlite3.connect("customers.db") #connect to the sqlite database named customers
cursor = connection.cursor() #create a database cursor, to execute SQL statements and fetch results from SQL queries

#Creating the customers table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS customers (
        name TEXT PRIMARY KEY,
        plan TEXT,
        renewal_days INTEGER,
        usage INTEGER
    )
""")
connection.commit() #committing and saving the changes to the database

#print("BEFORE SELECT")
#Insert customer info into customers table
cursor.execute(
    "INSERT OR IGNORE INTO customers (name,plan,renewal_days,usage) VALUES(?,?,?,?)",
    ("Globex", "Enterprise", 18,42)
) # ?s are placeholders or parameterized queries. 
cursor.execute(
    "INSERT OR IGNORE INTO customers (name, plan, renewal_days, usage) VALUES (?,?,?,?)",
    ("Acme", "Pro", 90, 115)
)
connection.commit()

#Read specific entries from the customer table
cursor.execute(
    "SELECT plan FROM customers WHERE name = ?",
    ("Globex",)
)
result = cursor.fetchone()
#print("RESULT:",result)
#print("AFTER SELECT")

#Create Tickets table
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS tickets (
        id TEXT PRIMARY KEY,
        customer_name TEXT,
        issue TEXT,
        priority TEXT,
        status TEXT
    )
"""
)
connection.commit()

#Tickets list
tickets = [
    ("Ticket-101", "Globex", "Payment page intermittently failing", "urgent", "open"),
    ("TICKET-102", "Globex", "Export occasionally times out", "medium", "open"),
    ("TICKET-103", "Acme", "Button alignment issue", "low", "closed")
]

#Insert all the tickets into the tickets table
cursor.executemany(
    """
    INSERT OR IGNORE INTO tickets (id, customer_name, issue, priority, status)
    VALUES (?,?,?,?,?)
""", tickets)
connection.commit()

#cursor.execute(
#    "DELETE FROM tickets WHERE id = ?", ("Ticket-01",)
#)
#connection.commit()

cursor.execute(
    """
    SELECT * FROM tickets
"""
)
rows2 = cursor.fetchall()
#print(rows2)

#Old local customer & account manager database
customers = {
    "Globex" : {
        "plan" : "Pro",
        "usage_last_30_days" : 42,
        "usage_previous_30_days" : 120,
        "renewal_days" : 18,
        "account_manager_id": "AM-204",
        "open_tickets" : [
            {
                "id" : "TICKET-101",
                "issue" : "Payment page intermittently failing",
                "priority" : "urgent"
            }
        ],
        "recent_feedback" : "The customer said the product has become unreliable and is considering alternatives"
    },
    "Acme" : {
        "plan" : "Pro",
        "usage_last_30_days" : 85,
        "usage_previous_30_days" : 90,
        "renewal_days" : 210,
        "open_tickets" : [],
        "recent_feedback" : "Generally happy with the product"
    }
}

account_managers = {
    "AM-204": {
        "name": "Sarah Chen",
        "email": "sarah@example.com"
    },
    "AM-105": {
        "name": "David Kim",
        "email": "david@example.com"
    }
}




#Tool Definitions
#Ticket ID generator - Temporary function
def get_next_ticket_id():
    cursor.execute("SELECT id FROM tickets")
    rows = cursor.fetchall()

    numbers = []

    for row in rows:
        ticket_id = row[0]
        number = int(ticket_id.split("-")[-1])
        numbers.append(number)

    next_number = max(numbers) + 1

    return f"TICKET-{next_number}"

#To fetch open customer tickets
def get_open_tickets(customer_name):
    cursor.execute(
    """
        SELECT * FROM tickets
        WHERE customer_name = ?
        AND status = "open"
    """, (customer_name,)
    )   
    return cursor.fetchall()

print(get_open_tickets("Globex"))

#Count the open tickets for a given customer
def count_open_tickets(customer_name):
    cursor.execute(
        """
            SELECT COUNT(*)
            FROM tickets
            WHERE customer_name = ?
            AND status = "open"
        """, (customer_name,)
    )
    result = cursor.fetchone()
    return result[0]
#print(count_open_tickets("Globex"))

#Create a support ticket
def create_support_ticket(customer_name, issue, priority):
    ticket_id = get_next_ticket_id()
    cursor.execute(
        """
        INSERT OR IGNORE INTO tickets (id,customer_name,issue,priority,status)
        VALUES (?,?,?,?,?)
        """, (ticket_id,customer_name,issue,priority,"open")
    )
    connection.commit()
    return ticket_id
#print(create_support_ticket("Acme", "Product is laggy", "medium"))
#print(get_open_tickets("Acme"))

def get_customer_plan(customer_name):
    cursor.execute(
    "SELECT plan FROM customers WHERE name = ?",
    (customer_name,)
)
    plans = cursor.fetchone()
    return plans[0]

def update_customer_plan(customer_name,new_plan):
    #Write specific updates to the customers table
    cursor.execute(
        """UPDATE customers
        SET plan = ?
        WHERE name = ?
        """, (new_plan,customer_name)
    )
    connection.commit()
    return ("Plan Updated Successfully")

#def get_customer_plan(customer_name):
#    plans = customers.get(customer_name)["plan"]
#    return plans

def get_recent_feedback(customer_name) :
    feedback = customers.get(customer_name)["recent_feedback"]
    return feedback


#def get_open_tickets(customer_name):
#    tickets = customers.get(customer_name)["open_tickets"]
#    return tickets

def get_usage_stats(customer_name):
    usagestats = {
        "usage_last_30_days" : customers.get(customer_name)["usage_last_30_days"],
        "usage_previous_30_days" : customers.get(customer_name)["usage_previous_30_days"]
    }
    return usagestats

def get_account_manager_id(customer_name):
    manager_id = customers.get(customer_name)["account_manager_id"]
    return manager_id

def get_account_manager(managerid):
    manager = {
        "Name" : account_managers.get(managerid)["name"],
        "Email" : account_managers.get(managerid)["email"]
    }
    return manager

def get_renewal_status(customer_name):
    renewaldays = customers.get(customer_name)["renewal_days"]
    return renewaldays


#Tools List for the Agent/LLM
tools = [
    {
        "type" : "function",
        "name" : "get_customer_plan",
        "description" : "Call to get the plan that the customer is enrolled in",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "the name of the customer"
                }
            },
            "required" : ["customer_name"]
        }
    },
    {
        "type" : "function",
        "name" : "get_recent_feedback",
        "description" : "Call to get the most recent feedback from the customer",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "the name of the customer"
                }
            },
            "required" : ["customer_name"]
        }
    },
    {
        "type" : "function",
        "name" : "get_open_tickets",
        "description"  : "Call to get the list of open tickets for a given customer",
        "parameters" : {
            "type" : "object",
            "properties":{
                "customer_name" : {
                    "type" : "string",
                    "description" : "the name of the customer"
                }
            },
            "required" : ["customer_name"]
        }
    },
    {
        "type" : "function",
        "name" : "get_usage_stats",
        "description" : "Get the customer's product usage for the last 30 days and the previous 30 days",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "name of the customer"
                }
            },
            "required" : ["customer_name"]
        }
    },
    {
        "type" : "function",
        "name" : "get_account_manager_id",
        "description" : "Call to get the ID of the account manager assigned to this customer",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "the name of the customer"
                }
            },
            "required" : ["customer_name"]
        }
    },
    {
        "type" : "function",
        "name" : "get_account_manager",
        "description" : "Call to get the account manager based on their ID",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "managerid" : {
                    "type" : "string",
                    "description" : "the ID of the manager"
                }
            },
            "required" : ["managerid"]
        }
    },
    {
        "type" : "function",
        "name" : "get_renewal_status",
        "description" : "Call to get the renewal days remaining for the given customer",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "the name of the customer"
                }
            },
            "required" : ["customer_name"]
        }
    },
    {
        "type" : "function",
        "name" : "update_customer_plan",
        "description" : "Call to update the plan for a customer",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "this is the name of the customer"
                },
                "new_plan" : {
                    "type" : "string",
                    "description" : "this is the new plan for this customer"
                }
            },
            "required" : ["customer_name", "new_plan"]
        }
    },
    {
        "type" : "function",
        "name" : "get_open_tickets",
        "description" : "Call to fetch the list of all open tickets for this customer",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "name of the customer"
                }
            },
            "required" : ["customer_name"]
        }
    },
    {
        "type" : "function",
        "name" : "count_open_tickets",
        "description" : "Call this to get the count/number of open tickets",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "name of the customer"
                }
            },
            "required" : ["customer_name"]
        }
    },
    {
        "type" : "function",
        "name" : "create_support_ticket",
        "description" : "Call to create a new support ticket for a customer",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" :{
                    "type" : "string",
                    "description" : "name of the customer"
                },
                "issue" : {
                    "type" : "string",
                    "description" : "a description of the issue faced by the customer"
                },
                "priority" : {
                    "type" : "string",
                    "description" : "what is the priority for this issue to be resolved"
                }
            },
            "required" : ["customer_name", "issue", "priority"]
        }
    }
]

#Function map to handle each tool call dynamically
function_map = {
    "get_customer_plan" : get_customer_plan,
    "get_recent_feedback" : get_recent_feedback,
    "get_open_tickets" : get_open_tickets,
    "get_usage_stats" : get_usage_stats,
    "get_account_manager_id" : get_account_manager_id,
    "get_account_manager" : get_account_manager,
    "get_renewal_status" : get_renewal_status,
    "update_customer_plan" : update_customer_plan,
    "count_open_tickets" : count_open_tickets,
    "create_support_ticket" : create_support_ticket 
}

#Agent loop function
def run_agent(response):
    while True:
        tool_outputs = [] #To store tool outputs to be sent back to the LLM
        tool_calls = [] #To store the list of tool calls by the LLM

        #creating the list of tools called by the LLM 
        for item in response.output:
            if item.type == "function_call":
                tool_calls.append(item)

        #check if the LLM didn't actually make any more tool calls
        if not tool_calls:
            print(response.output_text)
            return response #If no more calls, then return the final response back to the LLM

        # execute the actual tools called by the LLM
        for tool_call in tool_calls:
            print("Tool called:", tool_call.name)
            tool_name = tool_call.name
            arguments = json.loads(tool_call.arguments) #get the function arguments
            function_to_call = function_map[tool_name] #use the function map to map the tool call to the right function
            result = function_to_call(**arguments) #call the right function

            #append the output of each tool call to a list of outputs
            tool_outputs.append(
                {
                    "type" : "function_call_output",
                    "call_id" : tool_call.call_id, #use the call_id for each tool call to associate with the output of each tool call
                    "output" : str(result) #output of each tool call
                }
            )

        response = client.responses.create(
            model = "gpt-5.6",
            previous_response_id=response.id, #for conversational continuity with the LLM
            input = tool_outputs, #pass the tool outputs
            tools = tools, #pass the list of tools to the LLM
        )

response = None
while True:
    user_question = input("You: ")  #User prompt
    if not response:
        response = client.responses.create(
            model="gpt-5.6",
            input =user_question,
            tools=tools,   
        )
        response = run_agent(response)

    else:
        response = client.responses.create(
            model="gpt-5.6",
            previous_response_id=response.id,
            input = user_question,
            tools=tools,   
        )
        response = run_agent(response)
    