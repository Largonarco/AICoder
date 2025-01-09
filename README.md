# PotPieAI Code Review Agent

An autonomous code review agent system that leverages AI to analyze GitHub pull requests, process them asynchronously, and provide structured feedback through an API.

## Project Structure

The project is organized into several core components:

```
|-- agent.py        # AI Agent related code using LangChain
|-- logger.py       # Basic logger implementation
|-- models.py       # Pydantic Models for data validation
|-- redis_client.py # Redis client for caching
|-- server.py       # FastAPI web server implementation
|-- tasks.py        # Celery task queue management
|-- utils.py        # Helper functions and utilities
|-- Dockerfile      # Container configuration
|-- docker-compose.yml  # Multi-container orchestration
```

## Installation and Setup

You can run the application using Docker Compose in two ways:

```bash
# Method 1: Single command build and run
docker-compose up --build

# Method 2: Separate build and run
docker-compose build
docker-compose up
```

## API Documentation

The system exposes three main endpoints for interacting with the code review agent:

### 1. Initiate Code Review

Triggers a new code review analysis for a specified pull request.

```
POST http://localhost:8000/analyze-pr
```

**Request Body:**

```json
{
	"repo_url": "https://github.com/user/repo",
	"pr_number": 123,
	"github_token": "optional_token"
}
```

**Response:**

```json
{
	"status": "processing | completed | failed",
	"task_id": 123
}
```

### 2. Check Review Status

Retrieve the current status of a code review task.

```
GET http://localhost:8000/status/<task_id>
```

**Response:**

```json
{
	"status": "processing | completed | failed",
	"task_id": 123
}
```

### 3. Get Review Results

Fetch the detailed results of a completed code review.

```
GET http://localhost:8000/results/<task_id>
```

**Response:**

```json
{
	"status": "processing | completed | failed",
	"task_id": 123,
	"results": {
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

The API provides a comprehensive review of your code, including style issues, potential bugs, and suggestions for improvement, all organized by file and severity level.
