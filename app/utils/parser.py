from fastapi import HTTPException

def parse_repo(reponame: str):
    parts = reponame.split("/")
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Repository format is incorrect. It should be 'owner/repo'.")
    return parts[0], parts[1]