from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
from azure.storage.blob import BlobServiceClient
import os
from uuid import uuid4
from datetime import datetime, timezone
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config.clients import embeddings, llm_client, di_client
import json

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name="rag_index",
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)


def ensure_search_index_exists():
        index_client = SearchIndexClient(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
        )

        try:
            index_client.get_index("rag_index")
            print("Search index already exists")
            return
        except Exception:
            pass

        fields = [
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
            ),

            SearchableField(
                name="title",
                type=SearchFieldDataType.String,
            ),

            SearchableField(
                name="section_heading",
                type=SearchFieldDataType.String,
            ),

            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
            ),

            SimpleField(
                name="page_url",
                type=SearchFieldDataType.String,
                filterable=True,
            ),

            SimpleField(
                name="chunk_index",
                type=SearchFieldDataType.Int32,
                filterable=True,
                sortable=True,
            ),

            SimpleField(
                name="scraped_at",
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
                sortable=True,
            ),

            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(
                    SearchFieldDataType.Single
                ),
                retrievable=True,
                vector_search_dimensions=3072,
                vector_search_profile_name="vector-search-profile",
            ),
        ]

        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="hnsw-config",
                    kind="hnsw",
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="vector-search-profile",
                    algorithm_configuration_name="hnsw-config",
                )
            ],
        )

        semantic_config = SemanticConfiguration(
            name="semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                keywords_fields=[
                    SemanticField(field_name="title"),
                    SemanticField(field_name="content"),
                ],
                content_fields=[
                    SemanticField(field_name="content")
                ],
            ),
        )

        semantic_search = SemanticSearch(
            configurations=[semantic_config]
        )

        index = SearchIndex(
            name="rag_index",
            fields=fields,
            vector_search=vector_search,
            semantic_search=semantic_search,
        )

        index_client.create_index(index)
        print("Created Azure Search index")

def save_chunks():

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string
    )

    container_name = "rag-container123"
    blob_name = "legacy-manual.pdf"

    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_name
    )

    blob_data = blob_client.download_blob().readall()

    poller = di_client.begin_analyze_document(
        model_id="prebuilt-layout",
        body=blob_data
    )

    

    result = poller.result()

    chunks = create_chunks(blob_client.url, result)

    BATCH_SIZE = 50

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i+BATCH_SIZE]

        print(f"Uploading {len(batch)} documents")

        search_client.upload_documents(batch)
        print(f"Uploaded documents {i} to {i+len(batch)}")

def create_chunks(
    page_url: str,
    result: str
):

    title = None
    current_section = None

    sections = []

    for paragraph in result.paragraphs:

        role = paragraph.role
        content = paragraph.content.strip()

        if not content:
            continue

        # Document title
        if role == "title":
            title = content

        elif role == "sectionHeading":
            current_section = {
                "title": title,
                "section_heading": content,
                "content": []
            }
            sections.append(current_section)

        elif role in ["pageHeader", "pageFooter", "pageNumber"]:
            continue

        else:
            if current_section:
                current_section["content"].append(content)

    for section in sections:
        section["content"] = "\n".join(section["content"])

    # Create chunks from sections
    chunks = []
    metadata = []

    for section in sections:

        text = section["content"]

        if not text:
            continue

        chunks.append(text)

        metadata.append(
            {
                "document_title": section["title"],
                "section_heading": section["section_heading"]
            }
        )

    print(f"Generating embeddings for {len(chunks)} chunks")

    vectors = embeddings.embed_documents(chunks)

    #chunk_titles = generate_chunk_titles(chunks)

    documents = []

    for idx, (chunk, vector, meta) in enumerate(
        zip(chunks, vectors, metadata)
    ):
        documents.append(
            {
                "id": str(uuid4()),
                "title": meta["document_title"],
                "section_heading": meta["section_heading"],
                "content": chunk,
                "page_url": page_url,
                "chunk_index": idx,
                "scraped_at": datetime.now(timezone.utc),
                "content_vector": vector,
            }
        )

    return documents

def generate_chunk_titles(chunks):
    prompt = f"""
    Generate a short title (3-8 words) for each chunk.

    Return JSON only.

    Example:

    [
        {{
            "chunk_index": 0,
            "title": "Authentication"
        }}
    ]

    Chunks:

    {chr(10).join(
        f"Chunk {i}:{chr(10)}{chunk[:1000]}"
        for i, chunk in enumerate(chunks)
    )}
    """

    response = llm_client.invoke(prompt)

    response_text = (
        response.content
        if hasattr(response, "content")
        else str(response)
    )

    response_text = response_text.strip()

    if response_text.startswith("```json"):
        response_text = response_text.replace("```json", "", 1)

    if response_text.startswith("```"):
        response_text = response_text.replace("```", "", 1)

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    results = json.loads(response_text)

    return [
        item["title"]
        for item in sorted(
            results,
            key=lambda x: x["chunk_index"]
        )
    ]
