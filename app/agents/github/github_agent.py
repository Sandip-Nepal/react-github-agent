import os

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


class GitHubAgent:

    def __init__(self):
        self.agent = None
        self.mcp_client = None

    async def initialize(self):

        github_token = os.getenv("GITHUB_TOKEN")

        if not github_token:
            raise ValueError(
                "GITHUB_TOKEN environment variable is not set."
            )

        self.mcp_client = MultiServerMCPClient(
            {
                "github": {
                    "transport": "stdio",
                    "command": "docker",
                    "args": [
                        "run",
                        "-i",
                        "--rm",
                        "-e",
                        "GITHUB_PERSONAL_ACCESS_TOKEN",
                        "ghcr.io/github/github-mcp-server",
                        "stdio",
                        "--toolsets=all"
                    ],
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN":
                            os.getenv("GITHUB_TOKEN")
                    }
                }
            }
        )

        tools = await self.mcp_client.get_tools()
        print(f"Loaded {len(tools)} tools")

        print(f"Loaded {len(tools)} GitHub MCP tools")

        from app.config.clients import create_llm_client

        llm_client = create_llm_client()
        self.agent = create_agent(
            model=llm_client,
            tools=tools,
            system_prompt="""
            You are a GitHub assistant.

            Always use GitHub MCP tools for:
            - repositories
            - branches
            - commits
            - pull requests
            - issues
            - workflows
            - releases

            Never hallucinate GitHub information.

            Always call tools when GitHub data is required.
            """
        )

    async def invoke(
        self,
        query,
        history
    ):

        messages = history + [
            {
            "role":"user",
            "content":query
            }
        ]

        response = await self.agent.ainvoke(
            {
            "messages":messages
            }
        )

        return response["messages"][-1].content