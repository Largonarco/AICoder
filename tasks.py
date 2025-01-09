import os
import json
from celery import Celery
from models import PRRequest
from datetime import datetime
from utils import fetch_pr_diff
from redis_client import redis_client
from agent import init_ai_pr_review_agent
from celery.utils.log import get_task_logger

# Celery task-queue init
celery_app = Celery(
    'code_review',
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

# Get Celery task-specific logger
logger = get_task_logger(__name__)

# Celery Tasks
@celery_app.task(bind=True)
def analyze_pr_task(self, pr_request: PRRequest):
    """Asynchronous task to analyze PR"""
    try:
        logger.info(f"Task {self.request.id}: Starting analysis on PR #{pr_request['pr_number']} of repo {pr_request['repo_url']}")
        
        # Update task status to processing
        redis_client.hset(
            f"task:{self.request.id}",
            mapping={
                "status": "processing",
                "started_at": datetime.utcnow().isoformat()
            }
        )

        # Prepare results dict
        results = {
            "files": [],
            "summary": {
                "total_files": 0,
                "total_issues": 0,
                "critical_issues": 0
            }
        }
        
        # Init AI Agent
        agent = init_ai_pr_review_agent()
        logger.info(f"Task {self.request.id}: Created code review agent")

        # Get the files attached to the PR
        pr_files = fetch_pr_diff(
            pr_request['repo_url'],
            pr_request['pr_number'],
            pr_request.get('github_token')
        )
        logger.info(f"Task {self.request.id}: Fetched PR diff for PR #{pr_request['pr_number']}.")
        
        for file in pr_files:
            # Analyze each file
            analysed_output = agent.invoke({
                "input": f"Review this code:\n{file.patch}"
            })
            final_analysed_output = json.loads(analysed_output["output"])

            # Update analysis
            results["files"].append({
                "name": file.filename,
                "issues": final_analysed_output.get("issues", [])
            })
            
            # Update summary
            results["summary"]["total_files"] += 1
            results["summary"]["total_issues"] += len(final_analysed_output.get("issues", []))
            results["summary"]["critical_issues"] += len([issue for issue in final_analysed_output.get("issues", []) if issue.get("type") == "bug"])
            
        # Store results in Redis
        redis_client.hset(
            f"task:{self.request.id}",
            mapping={
                "status": "completed",
                "results": str(results),
                "completed_at": datetime.utcnow().isoformat()
            }
        )

        logger.info(f"Completed analysis on PR #{pr_request['pr_number']} of repo {pr_request['repo_url']}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in analysis task with PR #{pr_request['pr_number']} of repo {pr_request['repo_url']}: {e}")
        redis_client.hset(
            f"task:{self.request.id}",
            mapping={
                "status": "failed",
                "error": str(e)
            }
        )
        raise