import requests
import os
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("API_URL")

def get_universities():
    params = {
        "page":1,
        "perPage":20
    }
    response = requests.get(f"{URL}/university/all", params=params).json()
    return response

def check_application_status(application_code):
    response = requests.get(f"{URL}/application/status/{application_code}").json()
    return response