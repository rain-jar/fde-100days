from openai import OpenAI
import json
from app import process_request
from pydantic import BaseModel
import tools as tool_module


client = OpenAI()


class EvalResult(BaseModel):
    passed : bool
    reason : str

class AbstentionResult(BaseModel):
    abstained : bool
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

def judge_forbidden_claims(actual_answer, forbidden_claims):
    response = client.responses.parse(
            model = "gpt-5.6",
            input = [
                {
                    "role" : "system",
                    "content" : "Does the the ACTUAL ANSWER assert any of the FORBIDDEN CLAIMS as factual conclusions.Evaluate semantic meaning, not word overlap."
                },
                {
                    "role" : "user",
                    "content" : f"""
                        ACTUAL ANSWER : {actual_answer},
                        FORBIDDEN_CLAIMS : {forbidden_claims}
                        """
                }
            ],
            text_format=EvalResult
        )
    return response.output_parsed

def judge_abstention(actual_answer):
    response = client.responses.parse(
                model = "gpt-5.6",
                input = [
                    {
                        "role" : "system",
                        "content" : """
                        Evaluate the if the actual answer shows if the assistant abstained from answering 
                        because it lacked sufficient information, rather than answering the question"""
                    },
                    {
                        "role" : "user",
                        "content" : f"""
                            ACTUAL ANSWER : {actual_answer},
                            """
                    }
                ],
                text_format=AbstentionResult
            )
    return response.output_parsed

with open("evaldataset.json") as file:
    eval_dataset = json.load(file)

total = len(eval_dataset)
passedevals = 0


#eval_case = eval_dataset[0]

for eval_case in eval_dataset:

    tool_module.SIMULATE_DB_FAILURE = eval_case.get(
        "simulate_db_failure",
        False
    )
    result = process_request(eval_case["question"])
    tool_module.SIMULATION_DB_FAILURE = False

    #Expected Tools Check
    tools_called = [
        tool for round_tools in result["tools_called"]
        for tool in round_tools
    ]
    if eval_case.get("expected_tools"):
        tool_pass = all(
            tool in tools_called
            for tool in eval_case["expected_tools"]
        )
        print("TOOL_PASS: ",tool_pass)
    else:
        tool_pass = True

    #Forbidden claims check
    if eval_case.get("forbidden_claims"):
        forbidden_claims_pass = judge_forbidden_claims(
            result["answer"],
            eval_case["forbidden_claims"]
        )
        print("FORBIDDEN_CLAIMS: ",tool_pass)
    else:
        forbidden_claims_pass = True

    #Expected Source check
    tool_results = [
        tool for round_tools in result["tool_results"]
        for tool in round_tools
    ]
    if eval_case.get("expected_source") is not None:
        source_pass = any(
            eval_case["expected_source"] in tool["output"]
            for tool in tool_results
        )
        print("SOURCE_PASS: ",source_pass)
    else:
        source_pass = True

    #Expected answer correctness check
    if eval_case.get("expected_facts"):
        correctness_pass = judge_answer(eval_case["expected_facts"], result["answer"])
        print("CORRECTNESS CHECK: ", correctness_pass.passed)
    else:
        correctness_pass = True

    #Expected action check
    if eval_case.get("expected_action"):
        action_pass = any(
            eval_case["expected_action"] in tool["output"]
            for tool in tool_results
        )
        print("ACTION_CHECK: ",action_pass)
    else:
        action_pass = True

    #Abstention check
    abstention_result = judge_abstention(result["answer"])
    abstention_pass = (abstention_result.abstained == eval_case["should_abstain"])
    print("ABSTENTION_CHECK: ",abstention_pass)

    case_pass = (tool_pass and source_pass and correctness_pass and abstention_pass and action_pass and forbidden_claims_pass)
    if case_pass:
        passedevals +=1
        print("✅CASE PASSED: ", eval_case["id"])

    if not case_pass:
        print("CASE FAILED: ", eval_case["id"])
        #print("Failed due to Tool pass being ",tool_pass," Source Pass being ", source_pass, " Abstention pass being ", abstention_pass, " and Correctness being ", correctness_pass.reason)
        

passrate = passedevals/total
print("Total: ", passedevals,"/", total)
print("Passrate: ", passrate)