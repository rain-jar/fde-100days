import asyncio
import time
from fastapi import FastAPI, BackgroundTasks
import httpx # to support an API client that uses async

app = FastAPI()

async def task(name):
    print(f"{name} START")
    await asyncio.sleep(2)
    print(f"{name} END")

async def main():

    start = time.perf_counter()

    await asyncio.gather(
        task("A"),
        task("B"),
        task("C")
    )

    duration = time.perf_counter() - start
    print(f"It took {duration}seconds to execute")

def generate_report(customer_name: str):
    print(f"Starting report for{customer_name}")
    time.sleep(5)
    print(f"Report generated for {customer_name}")

URL = "https://httpbin.org/delay/2"

@app.post("/reports")
async def reports(customer_name:str, background_tasks:BackgroundTasks):
    background_tasks.add_task(generate_report,customer_name) #After sending the response, run generate_report(for this customer)

    return {
        "status" : "processing",
        "customer" : customer_name
    }


async def fetch(client, number):
    print(f"Request {number} START")
    response = await client.get(URL)

    print(f"Request {number} END")
    return response

async def sequential_requests():
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()

        await asyncio.gather(
            fetch(client,1),
            fetch(client,2),
            fetch(client,3)
        )

        duration = time.perf_counter() - start
        print(f"Concurrent time: {duration}")

#@app.get("/test")
async def test():
    await asyncio.sleep(3)
    return{"status" : "done"}

#asyncio.run(main())
#asyncio.run(sequential_requests())