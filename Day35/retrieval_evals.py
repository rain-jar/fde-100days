from vector_search import semantic_search
from vector_search import hybrid_search


eval_cases = [
    {
        "id": "retrieval-01",
        "query": "How long do Canadian refunds take?",
        "expected_policy_id": "REF-17B",
        "filters": {"country": "CA"},
    },
    {
        "id": "retrieval-02",
        "query": "How long will Canadian customers wait to get their money back?",
        "expected_policy_id": "REF-17B",
        "filters": {"country": "CA"},
    },
    {
        "id": "retrieval-03",
        "query": "What does REF-17B say about refund processing?",
        "expected_policy_id": "REF-17B",
        "filters": {},
    },
    {
        "id": "retrieval-04",
        "query": "What is the refund policy for US customers?",
        "expected_policy_id": "REF-17C",
        "filters": {"country": "US"},
    },
    {
        "id": "retrieval-05",
        "query": "What is the sick leave policy in Australia?",
        "expected_policy_id": None,
        "filters": {"country": "AU"},
    },
    {
        "id": "retrieval-06",
        "query": "How long do UK refunds take?",
        "expected_policy_id": "REF-17D",
        "filters": {"country": "UK"},
    },
    {
        "id": "retrieval-07",
        "query": "When should a UK customer expect their refund?",
        "expected_policy_id": "REF-17D",
        "filters": {"country": "UK"},
    },
    {
        "id": "retrieval-08",
        "query": "What does REF-18A say?",
        "expected_policy_id": "REF-18A",
        "filters": {},
    },
    {
        "id": "retrieval-09",
        "query": "How quickly are refunds processed?",
        "expected_policy_id": "REF-17B",
        "filters": {"country": "CA"},
    },
    {
        "id": "retrieval-10",
        "query": "What is the parental leave policy for Northstar?",
        "expected_policy_id": None,
        "filters": {},
    },
]

def hit_at_k(results, expected_policy_id, k):
    top_k_results = results[:k]
    for result in top_k_results:
        if result["policy_id"] == expected_policy_id:
            return True
    return False

def reciprocal_rank(results, expected_policy_id):
    for rank, result in enumerate(results, start=1):
        if result["policy_id"] == expected_policy_id:
            return 1 / rank
    return 0.0


for case in eval_cases:
    results = hybrid_search(case["query"], top_k=5, country=case["filters"].get("country"))

    if case["expected_policy_id"] is None:
        passed = len(results) == 0
        print(f"Case {case['id']}: Expected no results, got {len(results)}. Passed: {passed}")
    else:
        hit_at_1 = hit_at_k(results, case["expected_policy_id"], 1)
        hit_at_3 = hit_at_k(results, case["expected_policy_id"], 3)
        rr = reciprocal_rank(results, case["expected_policy_id"])
        print (results)
        print(f"Case {case['id']}: Hit@1: {hit_at_1}, Hit@3: {hit_at_3}, RR: {rr:.2f}")