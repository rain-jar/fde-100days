from openai import OpenAI
import time
import json

client = OpenAI()

call_count = 0

def get_customer_plan(customer_name):
    global call_count
    call_count += 1
    if call_count == 1:
        SIMULATE_FAILURE = True
    else:
        SIMULATE_FAILURE = False

    print("CallCount: ", call_count," Simulate Failure: ", SIMULATE_FAILURE)
    if SIMULATE_FAILURE:
        raise ConnectionError(
            "ERROR: Customer database temporarily unavailable"
        )
    if customer_name == "Banana":
        raise ValueError(
            "ERROR: Customer cannot be found"
        )
    if customer_name == "Stooopid":
        return None

    return "Enterprise"

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
    }
]

function_map = {
    "get_customer_plan" : get_customer_plan
}

def execute_with_retry(function_name,arguments,max_attempts):
    base_wait = 1
    attempt = 1
    while attempt<=max_attempts:
        try:
            result = function_name(**arguments)
            if result == None:
                print("Returning None")
                return ("ERROR: Not a valid output")
            print("Success Attempt: ", attempt, "Plan: ", result)
            return result

        except ConnectionError as e:
            print("Tool failed: ", e)
            if attempt==max_attempts:
                print("No more attempts left")
                return e
            
            wait_time = base_wait*(2**(attempt-1))
            print("Waiting: ", wait_time, " seconds")
            time.sleep(wait_time)

            attempt += 1
            print("Trying again. Attempt: ", attempt)

        except ValueError as e:
            print("Tool failed: ", e)
            return e


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
            return response #If no more calls, then return the final response back to the LLM

        # execute the actual tools called by the LLM
        for tool_call in tool_calls:
            print("Tool called:", tool_call.name)
            tool_name = tool_call.name
            arguments = json.loads(tool_call.arguments) #get the function arguments
            function_to_call = function_map[tool_name] #use the function map to map the tool call to the right function

            result = execute_with_retry(function_to_call, arguments, 3)

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

user_question = "What plan is Banana on?"  #User prompt
response = client.responses.create(
    model="gpt-5.6",
    input =user_question,
    tools=tools,   
)
result = run_agent(response)
print(result.output_text)


# helperresult = execute_with_retry(get_customer_plan,"Stooopid",3,call_count)
# print("Helper returned: ", helperresult)