import os
import tempfile

import chromadb
from ollama import Client, ChatResponse
import streamlit as st
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder
from streamlit.runtime.uploaded_file_manager import UploadedFile

from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv(".env")

#os.environ["OLLAMA_HOST"] = "http://10.21.10.36:7869"
#os.environ["OLLAMA_MODEL"] = "llama3.1"

# Set the default values for OLLAMA_HOST and OLLAMA_MODEL
ollama_host = os.environ.get("OLLAMA_HOST")
ollama_model = os.environ.get("OLLAMA_MODEL")



system_prompt = """
    You are an AI assistant tasked with providing detailed answers based solely on the given context. Your goal is to analyze the information provided and formulate a comprehensive, well-structured response to the question.

    context will be passed as "Context:"
    user question will be passed as "Question:"

    To answer the question:
    1. Thoroughly analyze the context, identifying key information relevant to the question.
    2. Organize your thoughts and plan your response to ensure a logical flow of information.
    3. Formulate a detailed answer that directly addresses the question, using only the information provided in the context.
    4. Ensure your answer is comprehensive, covering all relevant aspects found in the context.
    5. If the context doesn't contain sufficient information to fully answer the question, state this clearly in your response.

    Format your response as follows:
    1. Use clear, concise language.
    2. Organize your answer into paragraphs for readability.
    3. Use bullet points or numbered lists where appropriate to break down complex information.
    4. If relevant, include any headings or subheadings to structure your response.
    5. Ensure proper grammar, punctuation, and spelling throughout your answer.

    Important: Base your entire response solely on the information provided in the context. Do not include any external knowledge or assumptions not present in the given text.
"""


def process_document(uploaded_file: UploadedFile) -> list[Document]:
    """Processes an uploaded PDF file by converting it to text chunks.

    Takes an uploaded PDF file, saves it temporarily, loads and splits the content
    into text chunks using recursive character splitting.

    Args:
        uploaded_file: A Streamlit UploadedFile object containing the PDF file

    Returns:
        A list of Document objects containing the chunked text from the PDF

    Raises:
        IOError: If there are issues reading/writing the temporary file
    """
    # Store uploaded file as a temp file
    temp_file = tempfile.NamedTemporaryFile("wb", suffix=".pdf", delete=False)
    temp_file.write(uploaded_file.read())
    temp_filename = temp_file.name
    temp_file.close()

    loader = PyMuPDFLoader(temp_filename)
    docs = loader.load()
    os.unlink(temp_file.name)  # Delete temp file

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "?", "!", " ", ""],
    )
    return text_splitter.split_documents(docs)

def reset_vector_collection():
    chroma_client = chromadb.PersistentClient(path="./alpha-rag-chroma")
    try:
        chroma_client.delete_collection(name="rag_app")
    except Exception as e:
        st.error(f"An error occurred while resetting the vector collection: {e}")
    else:
        st.success("Vector collection reset successfully!")


def get_vector_collection() -> chromadb.Collection:
    """Gets or creates a ChromaDB collection for vector storage.

    Creates an Ollama embedding function using the nomic-embed-text model and initializes
    a persistent ChromaDB client. Returns a collection that can be used to store and
    query document embeddings.

    Returns:
        chromadb.Collection: A ChromaDB collection configured with the Ollama embedding
            function and cosine similarity space.
    """
    ollama_ef = OllamaEmbeddingFunction(
        url=f"{ollama_host}/api/embeddings",
        model_name="nomic-embed-text:latest",
    )

    try:
        chroma_client = chromadb.PersistentClient(path="./alpha-rag-chroma")
        collection = chroma_client.get_or_create_collection(
            name="rag_app",
            embedding_function=ollama_ef,
            metadata={"hnsw:space": "cosine"},
        )

        if collection:
            return collection
    except Exception as e:
        st.error(f"An error occurred while getting the vector collection: {e}")
    
    return None


def add_to_vector_collection(all_splits: list[Document], file_name: str):
    """Adds document splits to a vector collection for semantic search.

    Takes a list of document splits and adds them to a ChromaDB vector collection
    along with their metadata and unique IDs based on the filename.

    Args:
        all_splits: List of Document objects containing text chunks and metadata
        file_name: String identifier used to generate unique IDs for the chunks

    Returns:
        None. Displays a success message via Streamlit when complete.

    Raises:
        ChromaDBError: If there are issues upserting documents to the collection
    """
    collection = get_vector_collection()
    documents, metadatas, ids = [], [], []

    for idx, split in enumerate(all_splits):
        documents.append(split.page_content)
        metadatas.append(split.metadata)
        ids.append(f"{file_name}_{idx}")

    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )
    st.success("Data added to the vector store!")


def query_collection(prompt: str, n_results: int = 10):
    """Queries the vector collection with a given prompt to retrieve relevant documents.

    Args:
        prompt: The search query text to find relevant documents.
        n_results: Maximum number of results to return. Defaults to 10.

    Returns:
        dict: Query results containing documents, distances and metadata from the collection.

    Raises:
        ChromaDBError: If there are issues querying the collection.
    """
    collection = get_vector_collection()
    if collection:
        results = collection.query(query_texts=[prompt], n_results=n_results)
        return results
    
    return None

def call_llm(context: str, prompt: str, chat_host: str, chat_model: str="llama3.1"):
    """Calls the language model with context and prompt to generate a response.

    Uses Ollama to stream responses from a language model by providing context and a
    question prompt. The model uses a system prompt to format and ground its responses appropriately.

    Args:
        context: String containing the relevant context for answering the question
        prompt: String containing the user's question

    Yields:
        String chunks of the generated response as they become available from the model

    Raises:
        OllamaError: If there are issues communicating with the Ollama API
    """
    #client config
    client = Client(host=chat_host)

    response = client.chat(
        model=chat_model,
        # temperature=0.1,
        # top_p=0.9,
        # top_k=40,
        # max_tokens=512,
        # frequency_penalty=0.0,
        # presence_penalty=0.0,
        # stop=["\n\n", "Context:", "Question:"],
        # user="user",
        # system="system",
        stream=True,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"Context: {context}, Question: {prompt}",
            },
        ],
    )
    for chunk in response:
        if chunk["done"] is False:
            yield chunk["message"]["content"]
        else:
            break


def re_rank_cross_encoders(documents: list[str]) -> tuple[str, list[int]]:
    """Re-ranks documents using a cross-encoder model for more accurate relevance scoring.

    Uses the MS MARCO MiniLM cross-encoder model to re-rank the input documents based on
    their relevance to the query prompt. Returns the concatenated text of the top 3 most
    relevant documents along with their indices.

    Args:
        documents: List of document strings to be re-ranked.

    Returns:
        tuple: A tuple containing:
            - relevant_text (str): Concatenated text from the top 3 ranked documents
            - relevant_text_ids (list[int]): List of indices for the top ranked documents

    Raises:
        ValueError: If documents list is empty
        RuntimeError: If cross-encoder model fails to load or rank documents
    """
    relevant_text = ""
    relevant_text_ids = []

    encoder_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    ranks = encoder_model.rank(prompt, documents, top_k=3)
    for rank in ranks:
        relevant_text += documents[rank["corpus_id"]]
        relevant_text_ids.append(rank["corpus_id"])

    return relevant_text, relevant_text_ids

st.set_page_config(page_title="RAG Question Answer with LLM", page_icon=":brain:", layout="wide")
st.title(":brain: Alpha - Knowledgebase βeta")
st.header(":books: RAG Question & Answer with LLM model :baby:")

if "chat_model" not in st.session_state:
    st.session_state.chat_model = ollama_model

# parser request
# st.query_params
is_admin = 0
if "is_admin" in st.query_params:
    is_admin = st.query_params.is_admin

#st.info(f"is_admin: {is_admin}")

# Document Upload Area
if is_admin=="1":
    with st.sidebar:
        uploaded_file = st.file_uploader(
            "**📑 Upload PDF files for QnA**", type=["pdf"], accept_multiple_files=False
        )

        process = st.button(
            "⚡️ Process",
        )
        if uploaded_file and process:
            normalize_uploaded_file_name = uploaded_file.name.translate(
                str.maketrans({"-": "_", ".": "_", " ": "_"})
            )
            all_splits = process_document(uploaded_file)
            reset_vector_collection();
            add_to_vector_collection(all_splits, normalize_uploaded_file_name)

# Question and Answer Area
st.info(f":computer: model host: {ollama_host}")
with st.form(key="rag_form", clear_on_submit=False):
    st.markdown(":sparkles: Select model and enter your question below:", unsafe_allow_html=True)
    chat_model = st.selectbox("Select model", ["llama3.1", "deepseek-r1"], index=0, label_visibility="collapsed", placeholder="Select model", help="Select the model you want to ask.")
    prompt = st.text_area("**Ask a question related to your document:**", placeholder="Type your question here...",)
    
    ask = st.form_submit_button(
        "🔥 Ask",
    )

if ask and prompt:
    if not chat_model:
        chat_model = ollama_model
    st.session_state.chat_model = chat_model

    with st.spinner(f"{chat_model} generating..."):
        results = query_collection(prompt)
        if results:
            context = results.get("documents")[0]
            relevant_text, relevant_text_ids = re_rank_cross_encoders(context)
            response = call_llm(context=relevant_text, 
                                prompt=prompt, 
                                chat_host=ollama_host, 
                                chat_model=st.session_state.chat_model
                            )
            st.write(f":memo: {chat_model} anwser:".format(chat_model=st.session_state.chat_model))
            st.write_stream(response)
        else:
            st.info("Vector store has been not completed!")
