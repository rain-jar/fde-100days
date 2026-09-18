from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model = "gpt-5.6",
    input = [
        {"role":"user","content":"Globex is one of our customers and their account manager is Sarah Chen."},
        {"role":"user", "content":"Who is Globex's account manager?"}
    ]
)

print(response.output_text)

response2 = client.responses.create(
    model = "gpt-5.6",
    previous_response_id=response.id,
    input = "What's her name again?"
)

print(response2.output_text)
