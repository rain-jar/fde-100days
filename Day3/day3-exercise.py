from openai import OpenAI
import json

client = OpenAI()

tools = [
    {
        "type" : "function",
        "name" : "get_customer_plan",
        "description" : "Call this tool to find out what plan a given customer is currently on",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "the customer's name"
                }
            },
            "required" : ["customer_name"]
        }
    },
    {
        "type" : "function",
        "name" : "get_open_tickets",
        "description" : "Get the number of currently open support tickets for a customer.",
        "parameters" : {
            "type" : "object", 
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "the customer's name"
                }
            },
            "required" : ["customer_name"]
        }
    },
    {
        "type" : "function",
        "name" : "create_support_ticket",
        "description" : "Call this function to create a support ticket for a customer with a given issue and a given priority",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "the customer's name"
                },
                "issue" : {
                    "type" : "string",
                    "description" : "the issue for which the ticket is being created"
                },
                "priority" : {
                    "type" : "string",
                    "description" : "the priority for resolving the ticket"
                }
            },
            "required" : ["customer_name","issue","priority"]
        }
    }
]

def get_open_tickets(customer_name) :
    tickets = {
        "Acme" : 17,
        "Globex" : 4,
        "Initech" : 9
    }

    return tickets.get(customer_name,0)

def create_support_ticket(customer_name,issue,priority):
    print(customer_name)
    print(issue)
    print(priority)
    return_text = "Ticket created successfully: TICKET-101"

    return return_text


def get_customer_plan(customer_name):
    plans = {
        "Acme" : "Enterprise",
        "Globex" : "Pro", 
        "Initech" : "Starter"
    }

    return plans.get(customer_name,0)

response = client.responses.create(
    model= "gpt-5.6",
    input = "Globex's payment page is completely down. Create an urgent support ticket.",
    tools = tools,
)

for item in response.output :
    if item.type == "function_call":
        if item.name == "get_customer_plan" : 

            arguments = json.loads(item.arguments)
            customer_name = arguments["customer_name"]
            result = get_customer_plan(customer_name)

            plan_response = client.responses.create(
                model="gpt-5.6",
                previous_response_id=response.id,
                input = [
                    {
                        "type" : "function_call_output",
                        "call_id" : item.call_id,
                        "output" : str(result)
                    }
                ], 
                tools = tools,
            )

            print(plan_response.output_text)

        if item.name == "get_open_tickets" : 
            arguments = json.loads(item.arguments)
            customer_name = arguments["customer_name"]
            result = get_open_tickets(customer_name)

            tickets_response = client.responses.create(
                model="gpt-5.6",
                previous_response_id=response.id,
                input = [
                    {
                        "type" : "function_call_output",
                        "call_id" : item.call_id,
                        "output" : str(result)
                    }
                ],
                tools = tools,
            )

            print(tickets_response.output_text)

        if item.name == "create_support_ticket" :
            arguments = json.loads(item.arguments)
            customer_name = arguments["customer_name"]
            issue = arguments["issue"]
            priority = arguments["priority"]
            result = create_support_ticket(customer_name,issue, priority)

            createticket_response = client.responses.create(
                model="gpt-5.6",
                previous_response_id=response.id,
                input = [
                    {
                        "type" : "function_call_output",
                        "call_id" : item.call_id,
                        "output" : str(result)
                    }
                ],
                tools = tools,
            )

            print(createticket_response.output_text)

