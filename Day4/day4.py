from openai import OpenAI
import json

client = OpenAI()

#Customer Database
customers = {
    "Globex" : {
        "plan" : "Enterprise",
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
def get_customer_plan(customer_name):
    plans = customers.get(customer_name)["plan"]
    return plans

def get_recent_feedback(customer_name) :
    feedback = customers.get(customer_name)["recent_feedback"]
    return feedback

def get_open_tickets(customer_name):
    tickets = customers.get(customer_name)["open_tickets"]
    return tickets

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
]

#Function map to handle each tool call dynamically
function_map = {
    "get_customer_plan" : get_customer_plan,
    "get_recent_feedback" : get_recent_feedback,
    "get_open_tickets" : get_open_tickets,
    "get_usage_stats" : get_usage_stats,
    "get_account_manager_id" : get_account_manager_id,
    "get_account_manager" : get_account_manager,
    "get_renewal_status" : get_renewal_status
}

#User prompt
user_question = """
“Who is Globex's account manager? Give me their name and email.”
"""

#Initial LLM call based on user request
response = client.responses.create(
    model="gpt-5.6",
    input =user_question,
    tools=tools,
)

#Agent loop
while True : 
    tool_outputs = [] #To store tool outputs to be sent back to the LLM
    tool_calls = [] #To store the list of tool calls by the LLM

    #creating the list of tools called by the LLM 
    for item in response.output:
        if item.type == "function_call":
            tool_calls.append(item)

    #check if the LLM didn't actually make any more tool calls
    if not tool_calls:
        print(response.output_text) 
        break #If no more calls, then print the output and end the program

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

