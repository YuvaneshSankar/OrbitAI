import requests
import os
from dotenv import load_dotenv

load_dotenv()

headers = {
    "Authorization": f"Bearer {os.getenv('NOTION_API_TOKEN')}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28" 
}

page_id = os.getenv("NOTION_DATABASE_ID")
url = f"https://api.notion.com/v1/blocks/{page_id}/children"
response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print("Response:", response.json())
