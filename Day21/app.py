from openai import OpenAI
from tools import get_customer_details
from tools import get_open_tickets
from tools import create_refund
from retrieval import semantic_search
import json
import time
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI()

def search_knowledge(user_question, trace_id):
    #Do a semantic search
    results = semantic_search(user_question,5,0.2)
    logger.info(f"{trace_id} : RETRIEVAL : {len(results)} chunks retrieved")
    logger.info(
    f"{trace_id} : RETRIEVAL SOURCES : {[r['source'] for r in results]}"
)
    # print("RETRIEVED:")
    # for result in results:
    #     print(result["source"], result["score"], "-" ,result["text"])
    return results

    # #Structure the search results for an LLM
    # llm_input = []
    # for result in results:
    #     llm_input.append(f"""
    #         SOURCE : {result["source"]}
    #         CONTENT : {result["text"]}
    #         """
    #     )
    # return llm_input


#Tools List for the Agent/LLM
tools = [
    {
        "type" : "function",
        "name" : "get_customer_details",
        "description" : "Call to get details about the customer like purchases and plans",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "this is the name of the customer"
                },
            },
            "required" : ["customer_name"]
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
        "name" : "search_knowledge",
        "description" : "Search the our (Initech's) internal knowledge base and retrieve semantically useful supporting evidence",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "user_question" : {
                    "type" : "string",
                    "description" : "the question asked by the user"
                }
            },
            "required" : ["user_question"]
        }
    },
        {
        "type" : "function",
        "name" : "create_refund",
        "description" : "Call to process a refund based on a customer request",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "customer_name" : {
                    "type" : "string",
                    "description" : "name of the customer"
                },
                "amount" : {
                    "type" : "number",
                    "description" : "request refund amount"
                }
            },
            "required" : ["customer_name", "amount"]
        }
    },
]

#Function map to handle each tool call dynamically
function_map = {
    "get_customer_details" : get_customer_details,
    "get_open_tickets" : get_open_tickets,
    "search_knowledge" : search_knowledge,
    "create_refund" : create_refund
}

#ToolFailure Handling

def execute_with_retry(function,arguments,max_attempts,trace_id):
    attempt = 1
    while attempt <=max_attempts:
        try:
            result = function(**arguments,trace_id=trace_id)
            if result == None:
                print("Returning None")
                return ("TOOL_ERROR: Not a valid output")
            logger.info(f"{trace_id}: TOOL RESULT : COMPLETED")
            return result
        except ConnectionError as e:
            print("Tool failed: ", e)
            if attempt == max_attempts:
                print("No more attempts")
                logger.info(f"{trace_id} : TOOL RESULT : FAILED")
                return (f"TOOL_ERROR: {str(e)} after {max_attempts} attempts")

            base_wait = 0.1
            wait = time.sleep(base_wait*(2**attempt))

            attempt +=1
            print("Trying again. Attempt# ", attempt)


#Agent loop function
def run_agent(response, trace_id):
    tools_called =[]
    tools_results = []
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
            return {
                "response" : response, #If no more calls, then return the final response back to the LLM
                "answer" : response.output_text,
                "tools_called" : tools_called,
                "tool_results" : tools_results
            }

        # execute the actual tools called by the LLM
        for tool_call in tool_calls:
            tool_name = tool_call.name
            logger.info(f"{trace_id} : Tool Requested : {tool_name}")
            arguments = json.loads(tool_call.arguments) #get the function arguments
            logger.info(f"{trace_id} : Tool Args : {arguments}")
            function_to_call = function_map[tool_name] #use the function map to map the tool call to the right function

            result = execute_with_retry(function_to_call,arguments,3,trace_id)

            #append the output of each tool call to a list of outputs
            tool_outputs.append(
                {
                    "type" : "function_call_output",
                    "call_id" : tool_call.call_id, #use the call_id for each tool call to associate with the output of each tool call
                    "output" : str(result) #output of each tool call
                }
            )
        tools_called.append([tool_call.name for tool_call in tool_calls])
        tools_results.append(tool_outputs)

        response = client.responses.create(
            model = "gpt-5.6",
            previous_response_id=response.id, #for conversational continuity with the LLM
            input = tool_outputs, #pass the tool outputs
            tools = tools, #pass the list of tools to the LLM
        )


#Agent Eval function
def process_request(user_question):

    trace_id = str(uuid.uuid4())[:8]
    request_start = time.perf_counter()
    logger.info(f"{trace_id} : REQUEST STARTED")

    AGENT_INSTRUCTIONS = """
            You are our (Initech's) Customer Operations Copilot.
    
            When investigating a customer issue:
            - Inspect relevant customer/account information.
            - Inspect the customer's open support tickets.
            - Search the internal knowledge base for relevant policies or procedures.
            - Base conclusions and recommendations only on information returned by tools.
            - When using information retrieved from the internal knowledge base, cite the source filename using [filename].
            - Do not invent missing customer information or company policy.
        """
  
    response = client.responses.create(
        model="gpt-5.6",
        instructions=AGENT_INSTRUCTIONS,
        input =user_question,
        tools=tools,   
    )

    logger.info(f"{trace_id} : LLM_RESPONSE_RECEIVED")
    response = run_agent(response, trace_id)
    logger.info(f"{trace_id} : LLM_RESPONSE_RECEIVED")
    logger.info(f"{trace_id}: REQUEST COMPLETED")
    duration = time.perf_counter() - request_start
    logger.info(f"{trace_id}: TOTAL_LATENCY : {duration:.4f} seconds")
    return {
        "response": response,
        "trace_id": trace_id
    }

#LLM Conversation loop
if __name__ == "__main__" : 

    AGENT_INSTRUCTIONS = """
        You are our (Initech's) Customer Operations Copilot.

        When investigating a customer issue:
        - Inspect relevant customer/account information.
        - Inspect the customer's open support tickets.
        - Search the internal knowledge base for relevant policies or procedures.
        - Base conclusions and recommendations only on information returned by tools.
        - When using information retrieved from the internal knowledge base, cite the source filename using [filename].
        - Do not invent missing customer information or company policy.
    """
    response = None
    while True:
        user_question = input("You: ")  #User prompt
        trace_id = str(uuid.uuid4())[:8]
        request_start = time.perf_counter()
        logger.info(f"{trace_id} : REQUEST STARTED")
        if not response:
            response = client.responses.create(
                model="gpt-5.6",
                instructions=AGENT_INSTRUCTIONS,
                input =user_question,
                tools=tools,   
            )
            logger.info(f"{trace_id} : LLM_RESPONSE_RECEIVED")
            response = run_agent(response, trace_id)
            logger.info(f"{trace_id} : LLM_RESPONSE_RECEIVED")
            logger.info(f"{trace_id}: REQUEST COMPLETED")
            duration = time.perf_counter() - request_start
            logger.info(f"{trace_id}TOTAL_LATENCY : {duration:.4f} seconds")
            
        else:
            response = client.responses.create(
                model="gpt-5.6",
                previous_response_id=response.id,
                input = user_question,
                tools=tools,   
            )
            logger.info(f"{trace_id} : LLM_RESPONSE_RECEIVED")
            response = run_agent(response, trace_id)
            logger.info(f"{trace_id} : LLM_RESPONSE_RECEIVED")
            logger.info(f"{trace_id}: REQUEST COMPLETED")
            duration = time.perf_counter() - request_start
            logger.info(f"{trace_id}TOTAL_LATENCY : {duration:.4f} seconds")