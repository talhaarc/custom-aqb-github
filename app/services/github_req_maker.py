import requests
from fastapi import HTTPException

GITHUB_BASE_URL = "https://api.github.com"

def git_request(method: str, endpoint: str, token: str, payload: dict = None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    url = f"{GITHUB_BASE_URL}{endpoint}"
    response = requests.request(method, url, headers=headers, json=payload)

    if response.status_code >= 400:
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = {"error": "Unknown error from GitHub"}
        raise HTTPException(status_code=response.status_code, detail=error_detail)

    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, {"message": "Operation successful"}