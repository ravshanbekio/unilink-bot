import requests
import os
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("API_URL")

def get_universities(page: int, perPage: int):
    params = {
        "page":page,
        "perPage":perPage
    }
    response = requests.get(f"{URL}/university/all", params=params).json()
    return {"response":response, "total":response['meta']['total']}

def check_application_status(application_code):
    response = requests.get(f"{URL}/application/status/{application_code}").json()
    return response