from openai import OpenAI
import json

client = OpenAI()

tools = [
    {
        "type" : "function",
        "name" : "get_open_tickets",
        "description" : "Get the number of currently open support tickets for a customer.",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "The customer's name"
                }
            },
            "required" : ["customer_name"]
        }
    }
]

response = client.responses.create(
    model = "gpt-5.6",
    input = "How many open support tickets does Initech have?",
    tools = tools,
)

def get_open_tickets(customer_name):
    tickets = {
        "Acme" : 17,
        "Globex" : 4,
        "Initech" : 9
    }

    return tickets.get(customer_name,0) #Find the value associated with customer_name. If that customer doesn't exist, return 0.

for item in response.output:
    if item.type == "function_call" : 
        if item.name == "get_open_tickets" : 
            arguments = json.loads(item.arguments) #converts the JSON string format of the arguments
            #from the LLM's first tool call
            customer_name = arguments["customer_name"] #extracts the value for the "customer_name" key. 
            result = get_open_tickets(customer_name) #actual execution of the funcion

            print(result)

            final_response = client.responses.create(
                model = "gpt-5.6",
                previous_response_id=response.id, #provides broader conversational continuity 
                # - which previous model response we're continuing from
                input = [
                    {
                        "type" : "function_call_output", #type of input
                        "call_id" : item.call_id, #exactly which tool request this result belongs to.
                        "output" : str(result) # result of the tool request
                    }
                ],
                tools = tools,
            )

            print (final_response.output_text)