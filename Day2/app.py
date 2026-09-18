from openai import OpenAI ##From the openai library, import the OpenAI class so we can use it in our program.
from pydantic import BaseModel

client = OpenAI() ##OpenAI = blueprint/class ; OpenAI() = create an object from that blueprint ; client = variable holding that object

class CustomerAnalysis(BaseModel):
    customer_problem : str
    current_process : str
    business_impact : str
    potential_ai_solution : str

customer_note = """The recruiter spends considerable time looking through poorly formatted resumes to find the relevant skills 
that qualify each applicant for the given job description  
"""

response = client.responses.parse(
    model = "gpt-5.6",
    input = [
        {"role":"system","content":"Analyze the customer note"},
        {"role":"user", "content":customer_note},
    ],
    text_format = CustomerAnalysis,
)

analysis = response.output_parsed
print(analysis.business_impact)
print(type(analysis.business_impact))


## client → your OpenAI client object.
##responses → gives access to the Responses API .
##create(...) → makes the API request 
##returned response → stored in the variable response


response = client.responses.parse(
    model="gpt-5.6",
    input = [
        {"role":"system", "content":"Analyse the customer note"},
        {"role":"user", "content":customer_note},
    ],
    text_format=CustomerAnalysis,
)

analysis = response.output_parsed