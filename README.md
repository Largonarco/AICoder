## PotPieAI Assignment

#### Task

Build an autonomous code review agent system that uses AI to analyze GitHub pull requests, process them asynchronously, and provide structured feedback through an API.

#### File Structure

|-- agent.py (AI Agent related code using LangChain)
|-- logger.py (Basic logger)
|-- models.py (Pydantic Models)
|-- redis_client.py (Redis client)
|-- server.py (FastAPI web server)
|-- tasks.py (Celery task queue)
|-- utils.py (Helper functions)
|-- Dockerfile
|-- docker-compose.yml

#### Steps to run

```
docker-compose up --build

OR

docker-compose build
docker-compose up
```

#### Test URL

```
POST http://localhost:8000/analyze-pr
Request Body:
{
  "repo_url": "https://github.com/user/repo",
  "pr_number": 123,
  "github_token": "optional_token"
}

Response Body:
{
	status: processing | completed | failed,
  task_id: 123
}


GET http://localhost:8000/status/<task_id>
Params:
task_id: id

Response Body:
{
	status: processing | completed | failed,
  task_id: 123
}

GET http://localhost:8000/results/<task_id>
Params:
task_id: id

Response Body:
{
	status: processing | completed | failed,
  task_id: 123,
	results: {
        "files": [
            {
                "name": "main.py",
                "issues": [
                    {
                        "type": "style",
                        "line": 15,
                        "description": "Line too long",
                        "suggestion": "Break line into multiple lines"
                    },
                    {
                        "type": "bug",
                        "line": 23,
                        "description": "Potential null pointer",
                        "suggestion": "Add null check"
                    }
                ]
            }
        ],
        "summary": {
            "total_files": 1,
            "total_issues": 2,
            "critical_issues": 1
        }
    }
}
```
