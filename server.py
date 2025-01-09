from tasks import analyze_pr_task
from redis_client import redis_client
from utils import get_cache, set_cache
from fastapi import FastAPI, HTTPException
from models import PRRequest, CodeReviewBase, CodeReviewWithAnalysis

# Web server init
app = FastAPI(title="Github-AI")

# API Endpoints

# POST /analyze-pr 
# Request Body: PRRequest
# Response Body: CodeReviewBase
@app.post("/analyze-pr", response_model=CodeReviewBase)
async def analyze_pr(pr_request: PRRequest):
    """Endpoint to submit a PR for analysis"""
    task = analyze_pr_task.delay(pr_request.dict())

    return CodeReviewBase(
        task_id=task.id,
        status="pending"
    )

# GET /status/<task_id>
# Request Params: task_id
# Response Body: CodeReviewBase
@app.get("/status/{task_id}", response_model=CodeReviewBase)
async def get_task_status(task_id: str):
    """Check the status of an analysis task"""
    task_info = redis_client.hgetall(f"task:{task_id}")

    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return CodeReviewBase(
        task_id=task_id,
        status=task_info.get("status", "unknown"),
    )

# GET /results/<task_id>
# Request Params: task_id
# Response Body: CodeReviewWithAnalysis
@app.get("/results/{task_id}", response_model=CodeReviewWithAnalysis)
async def get_results(task_id: str):
    """Retrieve the analysis results"""
     # Try to get cached results first
    cached_results = await get_cache(task_id)

    if cached_results:
        return CodeReviewWithAnalysis(
            task_id=task_id,
            status="completed",
            results=cached_results
        )
    
    # If no cache then access main storage
    task_info = redis_client.hgetall(f"task:{task_id}")

    if not task_info:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_info.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Analysis not yet complete")
    
    # Parse results
    results = eval(task_info["results"])
    
    # Cache the results for future requests
    await set_cache(task_id, results)
    
    return CodeReviewWithAnalysis(
        task_id=task_id,
        status=task_info["status"],
        results=results
    )