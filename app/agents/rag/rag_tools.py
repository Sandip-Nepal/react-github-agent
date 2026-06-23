import inspect
from typing import Optional

from app.agents.rag.retriever import retrieve_documents
from app.config.clients import create_llm_client
from app.agents.memory import ConversationMemory


def _ensure_awaitable(value):
    return value if inspect.isawaitable(value) else value


async def rag_search(query: str, memory: Optional[ConversationMemory] = None):
    """
    Search the enterprise knowledge base.

    Args:
        query: User's GitHub-related question.
        memory: Optional conversation memory for additional history.

    Returns:
        Relevant GitHub documentation and tutorial content.
    """

    if memory is not None:
        memory.add_user_message(query)

    docs = await retrieve_documents(query)

    context = "\n".join(
        doc["content"]
        for doc in docs
    )

    history_section = ""
    if memory is not None:
        history = memory.get_history_text()
        if history:
            history_section = f"\n\nConversation history:\n{history}"

    prompt = """
        You are an enterprise knowledge assistant.

        Generate a suitable response from the retrieved context based on the user's query.
        - Do not use your own intelligence, use the context retrieved.
        - Write the response in 3-4 sentences by summarizing the large text in response.
        - If the retrieved context do not have content related to user's query respond:
            - I do not have any information on that in the DB.
        - Do not hallucinate.

        ## Input query
        {query}

        ## context
        {context}
        {history_section}
        """
    
    formatted_prompt = prompt.format(
        query=query,
        context=context,
        history_section=history_section
    )

    llm_client = create_llm_client()
    response = _ensure_awaitable(llm_client.invoke(formatted_prompt))
    if inspect.isawaitable(response):
        response = await response

    assistant_response = response.content
    if memory is not None:
        memory.add_assistant_message(assistant_response)

    return assistant_response