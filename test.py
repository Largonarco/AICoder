import pytest
from server import app
from utils import fetch_pr_diff
from fastapi import HTTPException
from unittest.mock import patch
from models import PRRequest, CodeReviewBase, CodeReviewWithAnalysis


@patch('utils.Github')
def test_fetch_pr_diff(mock_github):
    repo_url = "https://github.com/user/repo"
    pr_number = 123
    token = "test_token"

    # Mock Github and repo objects
    mock_github.return_value.get_repo.return_value.get_pull.return_value.get_files.return_value = ["file1", "file2"]

    # Call the function
    files = fetch_pr_diff(repo_url, pr_number, token)

    # Assert calls and output
    mock_github.assert_called_once_with(token)
    mock_github.return_value.get_repo.assert_called_once_with("user/repo")
    mock_github.return_value.get_repo.return_value.get_pull.assert_called_once_with(pr_number)
    assert files == ["file1", "file2"]

@patch('utils.Github')
def test_fetch_pr_diff_no_token(mock_github):
    repo_url = "https://github.com/user/repo"
    pr_number = 123

    # Mock Github and repo objects
    mock_github.return_value.get_repo.return_value.get_pull.return_value.get_files.return_value = ["file1", "file2"]

    # Call the function without token
    files = fetch_pr_diff(repo_url, pr_number)

    # Assert calls and output
    mock_github.assert_called_once_with()
    assert files == ["file1", "file2"]

@patch('utils.Github')
def test_fetch_pr_diff_exception(mock_github):
    repo_url = "https://github.com/user/repo"
    pr_number = 123
    mock_github.side_effect = Exception("Mocked exception")

    # Test that it raises HTTPException
    with pytest.raises(HTTPException):
        fetch_pr_diff(repo_url, pr_number)


def test_prrequest_model():
    pr_request = PRRequest(repo_url="https://github.com/user/repo", pr_number=123)
    assert pr_request.repo_url == "https://github.com/user/repo"
    assert pr_request.pr_number == 123

def test_prrequest_invalid_pr_number():
    with pytest.raises(ValueError):
        PRRequest(repo_url="https://github.com/user/repo", pr_number="abc")

def test_codereviewbase_model():
    review = CodeReviewBase(status="pending", task_id="task123")
    assert review.status == "pending"
    assert review.task_id == "task123"

def test_codereviewwithanalysis_model():
    review = CodeReviewWithAnalysis(
        status="completed",
        task_id="task123",
        results={"key": "value"}
    )
    assert review.results == {"key": "value"}
