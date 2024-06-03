import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

service_endpoint = "https://openpagerank.com"

def get_page_rank(url):
    try:
        page_rank = requests.get(f"{service_endpoint}/api/v1.0/getPageRank", 
                                headers={"API-OPR": os.getenv("OPENPAGERANK_API")}, 
                                params={"domains[]": url})
        print(page_rank)
        return page_rank.json()
    except Exception as e:
        print(e)
        return {"error": "Error while obtaining PageRank"}