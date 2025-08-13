from fastapi import APIRouter, Request, HTTPException
from app.utils import auth, parser
from app.services import github_req_maker
from app.models import github_model

router = APIRouter()

@router.post("/addCollab")
def add_client(client: github_model.ClientAdd, currentUser: str = "", request: Request = None):
    token = auth.get_github_token(request)
    owner, repo = parser.parse_repo(client.repository)
    payload = {"permission": client.permission}
    status, message = github_req_maker.git_request("PUT", f"/repos/{owner}/{repo}/collaborators/{client.username}", token, payload)
    return {"status_code": status, "message": message}

@router.get("/listCollaborators")
def list_collaborators(repositoryName: str, currentUser: str = "", request: Request = None):
    token = auth.get_github_token(request)
    owner, repo =  parser.parse_repo(repositoryName)
    status, message = github_req_maker.git_request("GET", f"/repos/{owner}/{repo}/collaborators", token)
    return {"status_code": status, "message": message}

@router.delete("/removeCollab")
def remove_collaborator(repositoryName: str, tobedeleted_user: str, currentUser: str = "", request: Request = None):
    token = auth.get_github_token(request)
    owner, repo = parser.parse_repo(repositoryName)
    status, _ = github_req_maker.git_request("DELETE", f"/repos/{owner}/{repo}/collaborators/{tobedeleted_user}", token)
    return {"status_code": status, "message": f"{tobedeleted_user} is removed."}

# ---------- Pull Requests ----------
@router.get("/listPullRequests")
def list_pull_requests(repositoryName: str, currentUser: str = "", request: Request = None):
    token = auth.get_github_token(request)
    owner, repo = parser.parse_repo(repositoryName)
    status, message = github_req_maker.git_request("GET", f"/repos/{owner}/{repo}/pulls", token)
    return {"status_code": status, "message": message}

@router.post("/createPullRequest")
def create_pull_request(repositoryName: str, currentUser: str = "", request: Request = None):
    token = auth.get_github_token(request)
    owner, repo = parser.parse_repo(repositoryName)
    status, message = github_req_maker.git_request("POST", f"/repos/{owner}/{repo}/pulls", token)
    return {"status_code": status, "message": message}

@router.get("/checkIfCollaborator")
def check_if_collaborator(repositoryName: str, username: str, request: Request = None):
    token = auth.get_github_token(request)
    owner, repo = parser.parse_repo(repositoryName)
    status, message = github_req_maker.git_request("GET", f"/repos/{owner}/{repo}/collaborators/{username}", token)
    return {"status_code": status, "message": message}

# ---------- Repositories ----------
@router.post("/createRepository")
def create_repository(repositoryName: str, currentUser: str = "", request: Request = None):
    token = auth.get_github_token(request)
    payload = {"name": repositoryName, "description": "Created by aws lambda function on GitHub"}
    status, message = github_req_maker.git_request("POST", "/user/repos", token, payload)
    if status >= 400:
        raise HTTPException(status_code=status, detail=message)
    return {"status_code": status, "message": message}

@router.delete("/deleteRepository")
def delete_repository(repositoryName: str, currentUser: str = "", request: Request = None):
    token = auth.get_github_token(request)
    owner, repo = parser.parse_repo(repositoryName)
    status, message = github_req_maker.git_request("DELETE", f"/repos/{owner}/{repo}", token)
    if status == 204:
        return {"status_code": status, "message": "Repository deleted successfully."}
    return {"status_code": status, "message": message}

@router.post("/createOrgRepository")
def create_org_repo(repositoryName: str, org: str = "", request: Request = None):
    token = auth.get_github_token(request)
    payload = {"name": repositoryName, "description": "Created by aws lambda function on GitHub"}
    status, message = github_req_maker.git_request("POST", f"/orgs/{org}/repos", token, payload)
    if status >= 400:
        raise HTTPException(status_code=status, detail=message)
    return {"status_code": status, "message": message}

# ---------- Issues ----------
@router.post("/createIssues")
def create_issues(repositoryName: str, currentUser: str = "", request: Request = None, title: str = ""):
    token = auth.get_github_token(request)
    owner, repo = parser.parse_repo(repositoryName)
    payload = {"title": title, "body": "Created by XXX lambda function on GitHub"}
    status, message = github_req_maker.git_request("POST", f"/repos/{owner}/{repo}/issues", token, payload)
    if status >= 400:
        raise HTTPException(status_code=status, detail=message)
    return {"status_code": status, "message": message}

@router.patch("/editIssue")
def edit_issue(repositoryName: str, issue_number: int, currentUser: str = "", request: Request = None, title: str = ""):
    token = auth.get_github_token(request)
    owner, repo = parser.parse_repo(repositoryName)
    payload = {}
    if title:
        payload["title"] = title
    status, message = github_req_maker.git_request("PATCH", f"/repos/{owner}/{repo}/issues/{issue_number}", token, payload)
    if status >= 400:
        raise HTTPException(status_code=status, detail=message)
    return {"status_code": status, "message": message}

# ---------- Releases ----------
@router.post("/createRelease")
def create_release(repositoryName: str, currentUser: str = "", request: Request = None, tag_name: str = ""):
    token = auth.get_github_token(request)
    owner, repo = parser.parse_repo(repositoryName)
    payload = {"tag_name": tag_name}
    status, message = github_req_maker.git_request("POST", f"/repos/{owner}/{repo}/releases", token, payload)
    if status >= 400:
        raise HTTPException(status_code=status, detail=message)
    return {"status_code": status, "message": message}

@router.delete("/deleteRelease")
def delete_release(repositoryName: str, release_id: int, currentUser: str = "", request: Request = None):
    token = auth.get_github_token(request)
    owner, repo = parser.parse_repo(repositoryName)
    status, message = github_req_maker.git_request("DELETE", f"/repos/{owner}/{repo}/releases/{release_id}", token)
    if status == 204:
        return {"status_code": status, "message": "Release deleted successfully."}
    return {"status_code": status, "message": message}

# ---------- Commits -----------
@router.get("/listCommits")
def list_commits(repositoryName: str, currentUser: str = "", request: Request=None):
    token = auth.get_github_token(request)
    owner, repo = parser.parse_repo(repositoryName)
    status, message = github_req_maker.git_request("GET", f"/repos/{owner}/{repo}/commits", token)
    return {"status_code": status, "message": message}