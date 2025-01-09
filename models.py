from typing import Optional
from pydantic import BaseModel

class PRRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: Optional[str] = None

class CodeReviewBase(BaseModel):
    status: str
    task_id: str

class CodeReviewWithAnalysis(CodeReviewBase):
    results: Optional[dict] 