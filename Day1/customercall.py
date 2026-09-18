from openai import OpenAI

client = OpenAI()

customer_note = """
Customer: Acme Law Firm

A 40-person law firm receives hundreds of contracts by email. 
Junior associates manually review them for unusual clauses 
before senior lawyers inspect them.
"""
##Triple quotes is used to create string spanning multiple lines. Normal quotes "" are for single line strings


response = client.responses.create(
    model = "gpt-5.6",
    input = f"""
    Analyze the following customer note.

    Identify:
    1. Customer problem
    2. Current process
    3. Business impact
    4. Potential AI solution

    Customer note:
    {customer_note}
    """
)
##The f makes this an f-string, which lets you insert variables directly into a string.

print(response.output_text)
