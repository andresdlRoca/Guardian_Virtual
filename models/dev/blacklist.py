from dotenv import load_dotenv
import requests
import json
import os


load_dotenv()


service_endpoint = "https://safebrowsing.googleapis.com"


# url_to_check = "https://testsafebrowsing.appspot.com/s/phishing.html"

def check_url(url):
    try:
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
                    {"url": url}
                ]
            }
        })
        print(threat_matches)
        return threat_matches.json()
    except Exception as e:
        print(e)
        return {"error": "Error al verificar la URL"}


