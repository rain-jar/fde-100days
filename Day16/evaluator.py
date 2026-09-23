from openai import OpenAI
from evals import answer_query
from pydantic import BaseModel

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

result = judge_answer(
    "5–7 business days after approval.",
    "Approved refunds generally arrive within five to seven business days."
)
print(result)

#actual = answer_query("How many days of maternity leave do Acme employees receive?")
#print(actual)

# source_pass = all(
#     source in actual["sources"]
#     for source in case["expected_sources"]
# )
# print("SOURCE_PASS: ",source_pass)

# abstention_pass = (actual["abstained"] == case["should_abstain"])
# print("ABSTENTION_PASS: ",abstention_pass)