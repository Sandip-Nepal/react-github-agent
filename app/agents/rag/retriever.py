from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os

load_dotenv()

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name="rag_index",
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)


async def retrieve_documents(query):

    docs = await search_client.search(
        search_text=query,
        top=5
    )

    return [doc async for doc in docs]