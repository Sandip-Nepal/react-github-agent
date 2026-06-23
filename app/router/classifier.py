from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .schema import RouteDecision
from .prompt import CLASSIFIER_PROMPT


class QueryClassifier:

    def initialize(self):

        from app.config.clients import create_llm_client
        
        llm_client = create_llm_client()
        self.llm = llm_client.with_structured_output(
            RouteDecision
        )

        self.prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CLASSIFIER_PROMPT),
            MessagesPlaceholder("history"),
            ("human", "{query}")
        ]
        )

    def classify(
        self,
        query: str,
        history=None
    ) -> str:

        messages = []

        if history:
            messages.extend(history)

        messages.append(
            {
                "role": "user",
                "content": query
            }
        )

        result = self.llm.invoke(
            messages
        )

        return result.route