from dotenv import load_dotenv
import requests
import json
import os


load_dotenv()


service_endpoint = "https://safebrowsing.googleapis.com"


url_to_check = "https://testsafebrowsing.appspot.com/s/phishing.html"

threat_matches = requests.post(f"{service_endpoint}/v4/threatMatches:find?key={os.getenv('GOOGLE_API')}", json={
    "client": {
        "clientId": "guardian-virtual",
        "clientVersion": "0.1"
    },
    "threatInfo": {
        "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", 
                        "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION", 
                        "THREAT_TYPE_UNSPECIFIED"],
        "platformTypes": ["ANY_PLATFORM"],
        "threatEntryTypes": ["URL"],
        "threatEntries": [
            {"url": url_to_check}
        ]
    }
})

print(threat_matches)
print(threat_matches.json())
print(threat_matches.json()["matches"])
