import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_external_user(user_id,trace_id):

    r = requests.get(f'https://jsonplaceholder.typicode.com/users/{user_id}', timeout=5)

    if r.status_code==200:
        data = r.json()
        #print(data["name"])
        logger.info(f"{trace_id}: API GET REQUEST SUCCESFUL")
        return {
            "username": data["name"],
            "user_email" : data["email"],
            "user_company": data["company"]
        }
    else:
        logger.warning(f"{trace_id}: API GET REQUEST FAILED")
        return {"error": f"Request failed: {r.status_code}"}


# r = requests.post(
#     'https://jsonplaceholder.typicode.com/posts',
#     json = {
#         "title" : "Globex investigation",
#         "body": "Payment issue detected",
#         "userId": 1
#     }
# )


#print(get_external_user(999999))
# print(r.status_code)
# print(r.json())
