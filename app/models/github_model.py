from pydantic import BaseModel
from typing import Optional

class ClientAdd(BaseModel):
    repository: str
    username: str
    permission: Optional[str] = "pull"