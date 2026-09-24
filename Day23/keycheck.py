import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ACME_API_KEY")

if not api_key:
    raise RuntimeError("ACME_API_KEY is not set/configured")

print(api_key)