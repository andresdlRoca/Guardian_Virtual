import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

service_endpoint = "https://openpagerank.com"

url_to_check = "https://www.minecraft.net"

page_rank = requests.get(f"{service_endpoint}/api/v1.0/getPageRank", 
                         headers={"API-OPR": os.getenv("OPENPAGERANK_API")}, 
                         params={"domains[]": url_to_check})

print(page_rank)
print(page_rank.json())