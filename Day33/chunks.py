import json
from openai import OpenAI

client = OpenAI()

chunks = [
    {
        "text": "Refunds for Canadian customers are processed within 5–7 business days.",
        "source": "refunds_canada.txt",
        "country": "CA",
        "department": "support",
        "document_type": "policy",
        "policy_id": "REF-17B"
    },
    {
        "text": "Refunds for US customers are processed within 3–5 business days.",
        "source": "refunds_us.txt",
        "country": "US",
        "department": "support",
        "document_type": "policy",
        "policy_id": "REF-17C"
    },
    {
        "text": "Refunds for UK customers are processed within 7–10 business days.",
        "source": "refunds_uk.txt",
        "country": "UK",
        "department": "support",
        "document_type": "policy",
        "policy_id": "REF-17D"
    },
    {
        "text": "Employees may work internationally for up to 30 days per calendar year.",
        "source": "remote_work_global.txt",
        "country": "GLOBAL",
        "department": "hr",
        "document_type": "policy",
        "policy_id": "REMOTE-22"
    },
    {
        "text": "Canadian employees working remotely must use a company-managed device.",
        "source": "remote_work_canada.txt",
        "country": "CA",
        "department": "hr",
        "document_type": "policy",
        "policy_id": "REMOTE-23"
    },
    {
        "text": "Compromised accounts require an immediate password reset and MFA verification.",
        "source": "security_accounts.txt",
        "country": "GLOBAL",
        "department": "security",
        "document_type": "policy",
        "policy_id": "SEC-91"
    },
    {
        "text": "Enterprise customers receive priority support and a dedicated account manager.",
        "source": "account_plans.txt",
        "country": "GLOBAL",
        "department": "sales",
        "document_type": "plan",
        "policy_id": "PLAN-ENT"
    },
    {
        "text": "Pro customers receive standard support with a four-hour response target.",
        "source": "account_plans.txt",
        "country": "GLOBAL",
        "department": "sales",
        "document_type": "plan",
        "policy_id": "PLAN-PRO"
    },
    {
        "text": "Canadian refund requests above $5,000 require manager approval.",
        "source": "refund_approvals_canada.txt",
        "country": "CA",
        "department": "support",
        "document_type": "procedure",
        "policy_id": "REF-18A"
    },
    {
        "text": "Refund requests involving suspected fraud must be escalated to the security team.",
        "source": "refund_security.txt",
        "country": "GLOBAL",
        "department": "security",
        "document_type": "procedure",
        "policy_id": "SEC-REF-4"
    },
    {
        "text": "Support tickets marked critical require an initial response within 30 minutes.",
        "source": "support_sla.txt",
        "country": "GLOBAL",
        "department": "support",
        "document_type": "policy",
        "policy_id": "SUP-30"
    },
    {
        "text": "UK employees must receive manager approval before international remote work.",
        "source": "remote_work_uk.txt",
        "country": "UK",
        "department": "hr",
        "document_type": "policy",
        "policy_id": "REMOTE-24"
    }
]

def chunk_embeddings(chunks):
    chunk_embeddings = []
    for chunk in chunks:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk["text"]
        )
        chunk_embeddings.append(
            {
                "source" : chunk["source"],
                "text" : chunk["text"],
                "country" : chunk["country"],
                "department" : chunk["department"],
                "document_type" : chunk["document_type"],
                "policy_id" : chunk["policy_id"],
                "embedding" : response.data[0].embedding
            }
        )
    return chunk_embeddings


current_chunks = chunk_embeddings(chunks)
#Store the embeddings in a json file
with open("current_knowledge_base.json","w") as file:
    json.dump(current_chunks,file)



