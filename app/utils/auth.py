from fastapi import Request, HTTPException

def get_github_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="No authorization token provided")
    return auth_header[len("Bearer "):]