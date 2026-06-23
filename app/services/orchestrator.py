from app.agents.rag.rag_tools import rag_search
from app.agents.memory import ConversationMemory


class AgentOrchestrator:

    def __init__(
        self,
        classifier,
        github_agent,
        memory: ConversationMemory | None = None,
    ):
        self.classifier = classifier
        self.github_agent = github_agent
        self.memory = memory
        # self.search_agent = search_agent

    async def invoke(self, query):

        history = []

        if self.memory:
            history = self.memory.get_messages()


        route = self.classifier.classify(
            query,
            history
        )

        if route == "github":
           answer = await self.github_agent.invoke(query, history)

        elif route == "rag":
            answer = await rag_search(query, memory=self.memory)

        self.memory.add_user_message(query)
        self.memory.add_assistant_message(answer)

        return answer