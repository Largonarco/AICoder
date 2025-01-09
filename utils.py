import json
from logger import logger
from github import Github
from typing import Optional
from fastapi import HTTPException
from redis_client import redis_client


# Utility to fetch a PR details
def fetch_pr_diff(repo_url: str, pr_number: int, token: Optional[str] = None):
    try:
        g = Github(token) if token else Github()
        repo = g.get_repo("/".join(repo_url.split("/")[-2:]))
        pr = repo.get_pull(pr_number)
        
        return pr.get_files()
    except Exception as e:
        logger.error(f"Error fetching PR diff: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Utility for caching
async def get_cache(task_id: str):
    cached_data = redis_client.get( f"cache:results:{task_id}")
    
    if cached_data:
        return json.loads(cached_data)
    
    return None

# Helper function to cache results
async def set_cache(task_id: str, results: dict):    
    redis_client.setex(
        f"cache:results:{task_id}",
        1800,
        json.dumps(results)
    )