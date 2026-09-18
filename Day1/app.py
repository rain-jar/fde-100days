from openai import OpenAI ##From the openai library, import the OpenAI class so we can use it in our program.

client = OpenAI() ##OpenAI = blueprint/class ; OpenAI() = create an object from that blueprint ; client = variable holding that object

response = client.responses.create (
    model = "gpt-5.6", 
    input = "say hello to me in one sentence"
)

print(response.output_text)

## client → your OpenAI client object.
##responses → gives access to the Responses API .
##create(...) → makes the API request 
##returned response → stored in the variable response