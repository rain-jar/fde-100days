from openai import OpenAI
from evals import answer_query
from pydantic import BaseModel
import json

client = OpenAI()

class EvalResult(BaseModel):
    passed : bool
    reason : str

def judge_answer(expected_answer, actual_answer):
    response = client.responses.parse(
        model = "gpt-5.6",
        input = [
            {
                "role" : "system",
                "content" : "Evaluate the if the essential factual meaning of the expected answer is contained in the actual answer. Do not require identical wording."
            },
            {
                "role" : "user",
                "content" : f"""
                    ACTUAL ANSWER : {actual_answer},
                    EXPECTED ANSWER : {expected_answer}
                    """
            }
        ],
        text_format=EvalResult
    )
    return response.output_parsed

case = {
    "question": "How many days of maternity leave do Acme employees receive?",
    "expected_sources": [],
    "should_abstain" : True
}

#Reading Evals from a Dataset Json file
with open("eval_dataset.json","r") as file:
    eval_dataset = json.load(file)

total = len(eval_dataset)
passedevalcases = 0

for eval in eval_dataset : 
    actual = answer_query(eval["question"])

    #print("Eval ID: ", eval["id"])

    source_pass = all(
        source in actual["sources"]
        for source in eval["expected_sources"]
    )
    #print("SOURCE_PASS: ",source_pass)

    abstention_pass = (actual["abstained"] == eval["should_abstain"])
    #print("ABSTENTION_PASS: ",abstention_pass)

    correctness_pass = judge_answer(eval["expected_answer"], actual["answer"])
    #print("CORRECTNESS PASS: ", correctness_pass.passed)

    case_pass = (source_pass and abstention_pass and correctness_pass.passed)
    #print("CASE PASS: ", case_pass)

    if case_pass:
        passedevalcases += 1
    if not case_pass:
        print("CASE FAILED: ", eval["id"])
        print("Failed due to Source Pass being ", source_pass, " Abstention pass being ", abstention_pass, " and Correctness being ", correctness_pass.reason)


passrate = passedevalcases/total
print("Total: ", passedevalcases,"/", total)
print("Passrate: ", passrate)



