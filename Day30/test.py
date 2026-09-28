import time
from openai import OpenAI

client = OpenAI()

prompt = """
Acme reports that its checkout page crashes whenever customers attempt payment.
This is blocking purchases and requires immediate attention.

Extract:
- customer name
- urgency
- issue category

Return JSON.
"""

start = time.perf_counter()

response = client.responses.create(
    model="gpt-5.4",
    input=prompt
)

latency = time.perf_counter() - start

print(response.output_text)
print("Latency:", latency)
print("Usage:", response.usage)