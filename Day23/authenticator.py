import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ACME_API_KEY")

if not api_key:
    raise RuntimeError("ACME_API_KEY is not set/configured")

r = requests.get(f'')

print(api_key)