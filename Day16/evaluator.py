from evals import answer_query

case = {
    "question": "How many days of maternity leave do Acme employees receive?",
    "expected_sources": [],
    "should_abstain" : True
}

actual = answer_query("How many days of maternity leave do Acme employees receive?")
print(actual)

source_pass = all(
    source in actual["sources"]
    for source in case["expected_sources"]
)
print("SOURCE_PASS: ",source_pass)

abstention_pass = (actual["abstained"] == case["should_abstain"])
print("ABSTENTION_PASS: ",abstention_pass)