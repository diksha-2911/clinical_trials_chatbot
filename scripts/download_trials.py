import requests
import json
import time

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

all_studies = []

next_page_token = None

while len(all_studies) < 1000:

    params = {
        "query.cond": "cancer",
        "pageSize": 100
    }

    if next_page_token:
        params["pageToken"] = next_page_token

    response = requests.get(BASE_URL, params=params)

    data = response.json()

    studies = data.get("studies", [])

    all_studies.extend(studies)

    print(f"Downloaded: {len(all_studies)}")

    next_page_token = data.get("nextPageToken")

    if not next_page_token:
        break

    time.sleep(0.5)

with open("data/trials.json", "w", encoding="utf-8") as f:
    json.dump({"studies": all_studies}, f)

print("Done")