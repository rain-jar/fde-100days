from pydantic import BaseModel #Importing BaseModel from Pydantic. Gives the data Pydantic's validation/schema behavior.

class CustomerAnalysis(BaseModel): #creating our own class called CustomerAnalysis, based on Pydantic's BaseModel. 
    #BaseModel itself is a class provided by Pydantic and CustomerAnalysis inherits from it.
    customer_problem: str
    current_process: str
    business_impact: str
    potential_ai_solution: str

##The class has following fields/attributes :
##customer_problem       → string
##current_process        → string
##business_impact        → string
##potential_ai_solution  → string



from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()


class CalendarEvent(BaseModel): #creating our own class called CustomerAnalysis, based on Pydantic's BaseModel. 
    #BaseModel itself is a class provided by Pydantic and CustomerAnalysis inherits from it.
    name: str
    date: str
    participants: list[str]


response = client.responses.parse( #Calling the "parse" API method. 
    #Use when you want the response parsed into a Python structure you've defined, such as a Pydantic model.
    model="gpt-5.6", #LLM Model
    input=[ #input is now a Python list containing two dictionaries.
        {"role": "system", "content": "Extract the event information."},  #Instruction to the AI: Your job is to extract event information.
        #system is a specific role value defined by the API to denote system instructions.
        {
            "role": "user", #this is another specific role defined by the API to denote user data. 
            "content": "Alice and Bob are going to a science fair on Friday.", #This could also be a variable that contains a list of different events. 
            #Instructions stay constant. Data changes.
        }, #Python itself doesn't give those dictionaries special meaning. The OpenAI API does.  
    ],  
    text_format=CalendarEvent, #calls the class that defines the required format. 
)

event = response.output_parsed