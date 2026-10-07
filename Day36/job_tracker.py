from pydantic import BaseModel
from fastapi import FastAPI
import uuid
import psycopg 
from dotenv import load_dotenv
import os

load_dotenv()

class InvestigationRequest(BaseModel):
    customer_name: str

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

MAX_ATTEMPTS = 3

@app.post("/investigations", status_code=202)
def create_investigation(request: InvestigationRequest):
    job_id = f"JOB-{uuid.uuid4().hex[:8]}"

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO investigation_jobs (id, customer_name, status) VALUES (%s, %s, %s)",
                (job_id, request.customer_name, "QUEUED")
            )

    return {"job_id": job_id, "status": "QUEUED"}

#Read the persisted job 
@app.get("/investigations/{job_id}")
def get_investigation(job_id: str):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, customer_name, status, result, error, attempt_count FROM investigation_jobs WHERE id = %s",
                (job_id,)
            )
            job = cur.fetchone()

    if job:
        return {"job_id": job[0], 
                "customer_name": job[1], 
                "status": job[2],
                "result": job[3],
                "error": job[4],
                "attempt_count": job[5]
                }
    else:
        return {"error": "Job not found"}, 404


#Function to run the job and update the status in the database
def process_job(job_id: str):
    attempt_count = 0
    try:
        #first update the job status to RUNNING
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE investigation_jobs
                    SET status = 'RUNNING',
                        attempt_count = attempt_count + 1,
                        updated_at = NOW()
                    WHERE id = %s
                    RETURNING attempt_count
                    """,
                    (job_id,),
                )
                attempt_count = cur.fetchone()[0]

        #Simulate customer-data loading step
        customer = "Globex customer data"

        #Simulate worker crash
        raise RuntimeError("Simulated worker crash")

    except Exception as e:
        new_status = (
            "QUEUED"
            if attempt_count < MAX_ATTEMPTS
            else "FAILED"
        )

        #Update the job status to COMPLETED and store the result
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE investigation_jobs
                    SET status = %s,
                        error = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (new_status, str(e), job_id),
                )

        return {"job_id": job_id, 
                "status": new_status, 
                "attempt_count": attempt_count}
    

#Expose the fake worker endpoint to process the job
@app.post("/investigations/{job_id}/run", status_code=202)
def run_investigation(job_id: str):

    process_job(job_id)

    return {
        "job_id": job_id, 
        "status": "COMPLETED"
    }