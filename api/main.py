from fastapi import FastAPI, Depends
from api.model import generate_demand
from api.auth import verify_api_key

app = FastAPI(title="SmartGridAI API")

@app.get("/")
def root():
    return {"message": "SmartGridAI API is running"}

@app.get("/demand")
def get_demand(api_key: str = Depends(verify_api_key)):
    return generate_demand()
