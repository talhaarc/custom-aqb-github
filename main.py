from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.responses import JSONResponse, HTMLResponse    
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import os
import logging
import dotenv
from typing import Optional
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GitHub Colab API")

dotenv.load_dotenv()
token_storage = {}
CLIENT_ID = os.getenv("GITHUB_CLIENT")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing only
    allow_methods=["*"],
    allow_headers=["*"],
)
# GITHUB_PAT = os.environ.get("GITHUB_PAT")
GITHUB_BASE_URL = "https://api.github.com"

class clientAdd(BaseModel):
    repository: str
    username: str
    permission: Optional[str] = "pull"

@app.get("/login")
def login_url():
    urltoRedirect = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo"
    return RedirectResponse(urltoRedirect)
@app.get("/callback")
def callback(request: Request, code: str):
    bearer_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code
    }
    print("hereee")
    headers = {
        "Accept": "application/json"
    }
    response = requests.post(bearer_url, json=payload, headers=headers)
    response_code = response.status_code
    if response_code != 200:
        raise HTTPException(status_code=response_code, detail="Failed to obtain access token.")

    access_token = response.json().get("access_token")
    user_resp = requests.get(f"{GITHUB_BASE_URL}/user",
                             headers={"Authorization": f"token {access_token}"})
    if user_resp.status_code != 200:
        raise HTTPException(status_code=user_resp.status_code, detail=user_resp.text)
    login_name = user_resp.json()["login"]
    token_storage[login_name] = access_token
    html_content = """
    <html>
        <body>
            <h1>✅ GitHub login successful</h1>
            <p>You can now close this window and return to the app.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
@app.get("/")
def read_root():
    print("Welcome to the GitHub Colab API")
    return {"message": "Welcome to the GitHub Colab API"}

@app.post("/addCollab")
def add_client(clientreq: clientAdd, logging_user: str):
    print("Adding collaborator")
    token = token_storage.get(logging_user)
    if not token:
        print("token error")
        logger.error(f"No access token found for user {logging_user}.")
        raise HTTPException(status_code=401, detail="User not authenticated.")

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
    headers = {
            "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    # headers = make_headers()
    # return JSONResponse(status_code=200, content=headers)
    response = requests.put(
        urlToSend,
        headers=headers,
        json=payload
    )
    return {
        "status_code": response.status_code,
        "message": response.json()
    }
    status_code = response.status_code
    if status_code == 204 or status_code == 201:
        logger.info(f"Successfully added {clientreq.username} as a collaborator to {clientreq.repository}.")
    elif status_code == 404:
        logger.error(f"Repository {clientreq.repository} not found.")
        raise HTTPException(status_code=404, detail="Repository not found.")
@app.get("/listCollaborators")
def list_collaborators(reponame: str, logging_user: str):
    print("Listing collaborators")
    token = token_storage.get(logging_user)
    if not token:
        print("token error")
        logger.error(f"No access token found for user {logging_user}.")
        raise HTTPException(status_code=401, detail="User not authenticated.")

    splittedRepoUser = reponame.split("/")
    checkFormat = len(splittedRepoUser)
    if checkFormat != 2:
        logger.error("Repository format is incorrect. It should be 'owner/repo'.")
        raise HTTPException(status_code=400, detail="Repository format is incorrect. It should be 'owner/repo'.")
    owner, repo = splittedRepoUser[0], splittedRepoUser[1]
    urlToSend=f"{GITHUB_BASE_URL}/repos/{owner}/{repo}/collaborators"
    headers = {
            "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    # headers = make_headers()
    # return JSONResponse(status_code=200, content=headers)
    response = requests.get(
        urlToSend,
        headers=headers,
    )
    return {
        "status_code": response.status_code,
        "message": response.json()
    }
@app.delete("/removeCollab")
def removeCollaborator(reponame: str, logging_user:str, tobedeleted_user: str):
    token = token_storage.get(logging_user)
    if not token:
        raise HTTPException(status_code=401, detail="User not authenticated.")
    
    splittedRepoUser = reponame.split("/")
    checkFormat = len(splittedRepoUser)
    if checkFormat != 2:
        raise HTTPException(status_code=400, detail="Repository format is incorrect. It should be 'owner/repo'.")
    
    owner, repo = splittedRepoUser[0], splittedRepoUser[1]
    urlToSend = f"{GITHUB_BASE_URL}/repos/{owner}/{repo}/collaborators/{tobedeleted_user}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    response = requests.delete(url=urlToSend, headers=headers)
    return {"status_code": response.status_code, "message": f"{tobedeleted_user} is removed."}
