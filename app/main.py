from app.services.orchestrator import AgentOrchestrator
from app.router.classifier import QueryClassifier
from app.config.clients import llm_client
from app.agents.github.github_agent import GitHubAgent
from app.agents.memory import ConversationMemory

classifier = QueryClassifier(llm_client)

async def main():
    memory = ConversationMemory(max_length=40)
    github_agent = GitHubAgent(memory=memory)
    await github_agent.initialize()
    orchestrator = AgentOrchestrator(
        classifier=classifier,
        github_agent=github_agent,
        memory=memory,
    )
    response = await orchestrator.invoke("list all the repositories?")
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())