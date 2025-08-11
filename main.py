import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.responses import JSONResponse, HTMLResponse    
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import Optional
from mangum import Mangum
import boto3

app = FastAPI(title="GitHub Colab API")
GITHUB_BASE_URL = "https://api.github.com"
class clientAdd(BaseModel):
    repository: str
    username: str
    permission: Optional[str] = "pull"


@app.post("/addCollab")
def add_client(clientreq: clientAdd, logging_user: str,request: Request):

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No Authorization token provided.")

    splittedRepoUser = clientreq.repository.split("/")
    checkFormat = len(splittedRepoUser)
    if checkFormat != 2:
        logger.error("Repository format is incorrect. It should be 'owner/repo'.")
        raise HTTPException(status_code=400, detail="Repository format is incorrect. It should be 'owner/repo'.")
    owner, repo = splittedRepoUser[0], splittedRepoUser[1]
    urlToSend = f"{GITHUB_BASE_URL}/repos/{owner}/{repo}/collaborators/{clientreq.username}"
    payload = {
        "permission": clientreq.permission
    }

    token = auth_header[len("Bearer "):]
    headers = {
            "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.put(
        urlToSend,
        headers=headers,
        json=payload
    )
    return {
        "status_code": response.status_code,
        "message": response.json()
    }
@app.get("/listCollaborators")
def list_collaborators(reponame: str, logging_user: str, request: Request):

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No Authorization token provided.")
    splittedRepoUser = reponame.split("/")
    checkFormat = len(splittedRepoUser)
    if checkFormat != 2:
        raise HTTPException(status_code=400, detail="Repository format is incorrect. It should be 'owner/repo'.")
    owner, repo = splittedRepoUser[0], splittedRepoUser[1]
    urlToSend=f"{GITHUB_BASE_URL}/repos/{owner}/{repo}/collaborators"

    token = auth_header[len("Bearer "):]
    headers = {
            "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    response = requests.get(
        urlToSend,
        headers=headers,
    )
    return {
        "status_code": response.status_code,
        "message": response.json()
    }
@app.delete("/removeCollab")
def removeCollaborator(reponame: str, logging_user:str, tobedeleted_user: str,request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No Authorization token provided.")
    splittedRepoUser = reponame.split("/")
    checkFormat = len(splittedRepoUser)
    if checkFormat != 2:
        raise HTTPException(status_code=400, detail="Repository format is incorrect. It should be 'owner/repo'.")
    
    owner, repo = splittedRepoUser[0], splittedRepoUser[1]
    urlToSend = f"{GITHUB_BASE_URL}/repos/{owner}/{repo}/collaborators/{tobedeleted_user}"

    token = auth_header[len("Bearer "):]
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    response = requests.delete(url=urlToSend, headers=headers)
    return {"status_code": response.status_code, "message": f"{tobedeleted_user} is removed."}
handler = Mangum(app)


