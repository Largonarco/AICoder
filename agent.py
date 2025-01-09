from pydantic import Field
from typing import Optional
from utils import fetch_pr_diff
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_openai_functions_agent

# Agentic tools
class FetchPRDiffTool(BaseTool):
    name: str = Field(default="fetch_pr_diff")  
    description: str = Field(default="""
    Fetch the PR diff from GitHub
    
    Args:
        repo_url (str): URL of the GitHub repository
        pr_number (int): Number of the pull request
        token (Optional[str]): GitHub authentication token
    
    Returns:
        str: Fetched PR files
    """)
    
    def _run(
        self, 
        repo_url: str, 
        pr_number: int, 
        token: Optional[str] = None
    ) -> str:
      fetch_pr_diff(repo_url=repo_url, pr_number=pr_number, token=token)

# AI Agent initialiser
def init_ai_pr_review_agent():
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert code reviewer. Analyze the code for:
        1. Style and formatting issues
        2. Potential bugs or errors
        3. Performance improvements
        4. Security concerns
        5. Best practices

        Provide specific, actionable feedback as issues in a json format and should follow this structure.
        For each file analysed return exactly a JSON object beginning and ending with curly braces, as this output needs to be fed to another system and it only takes in json.
        The JSON has a name field specifying the name of the file along with an issues field which is an array of issues.
        Every issue must comprise of type, line, description, suggestion. type specifies the kind of issue, there are 4 types: style, bug, perf improvement, and best practice. line is the line number in the code. 
       """),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    
    tools = [FetchPRDiffTool()]
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


