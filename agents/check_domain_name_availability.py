import requests
from langchain.tools import Tool
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv('WHOISJSON_API_KEY')
if not api_key:
    raise ValueError("Please set the WHOISJSON_API_KEY environment variable")

def check_domain_availability(domain_name: str) -> bool:
    url = f"https://whoisjsonapi.com/v1/status/{domain_name}"
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('status') == 'inactive'
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

def check_multiple_domains(domains: List[str]) -> List[str]:
    available_domains = []
    for domain in domains:
        if check_domain_availability(domain):
            available_domains.append(domain)
    return available_domains

domain_availability_tool = Tool(
    name="Domain Availability Checker",
    func=check_multiple_domains,
    description="Check the availability of multiple domain names."
)
