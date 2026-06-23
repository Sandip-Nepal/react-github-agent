import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

load_dotenv()


def create_llm_client():
    return AzureChatOpenAI(
        azure_deployment="gpt-4.1-mini",
        api_version=os.getenv("api_version"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
    )


embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-large",
    api_version=os.getenv("api_version"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    )

di_client = DocumentIntelligenceClient(
    endpoint=os.getenv("DI_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("DI_KEY"))
)