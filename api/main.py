from fastapi import FastAPI, Depends
from dotenv import load_dotenv

load_dotenv()

from api.model import generate_demand
from api.auth import verify_api_key

app = FastAPI(title="SmartGridAI API")

@app.get("/")
def root():
    return {"message": "SmartGridAI API is running"}

@app.get("/demand")
def get_demand(auth=Depends(verify_api_key)):
    api_key, plan = auth
    return generate_demand()
