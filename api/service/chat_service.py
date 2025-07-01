import sys
import os
sys.path.append(os.path.abspath(f"{os.environ.get("APP_API_PATH")}/dto/"))

from dto_model import ChatQuery
from ollama import Client, ChatResponse
from sentence_transformers import CrossEncoder
import chromadb
from chromadb.config import Settings
from langchain_ollama import ChatOllama
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
from datetime import datetime
import numpy as np


prompt_knowledgebase = """
    You are an AI assistant of the backend Alpha site, answer the question based only on the following context:
    
    context will be passed as "Context:"
    user question will be passed as "Question:"

    To answer the question, you need to understand the meaning and logical structure of the question given:
    - If you don't know the answer, please say "Sorry!" as nicely as possible.
    - If the context provided does not contain information about the user question. Say "Sorry!" as nice as possiple.
    - If the question is not meaningful or unreadable or too short. Say "Sorry" to ask for help as naturally as possible then stop answering.
    - If the question is not mentioned in the context, please say "Sorry! I'm just a newbie bot. How can I help you?" as naturally as possible then stop answering.
    - If the question is mentioned in the context, please answer the question based on the context as naturally as possible.
    
    Format your response as follows:
    - Organize your answer into paragraphs for readability.
    - Use bullet points or numbered lists where appropriate to break down complex information.
    - Formulate a detailed answer that directly addresses the question, using only the information provided in the context.

    Important: 
    - Do not include any external knowledge or assumptions if there is no mention in the give document.
    - Do not include any personal opinions or interpretations and explanations.
    - Do not include any disclaimers or unnecessary information.
    - Don't put "Answer:" or "Response:" before your answer.
    - Don't repeat the question in your answer.
"""

### This is a base class for the AlphaService, which initializes the OLLAMA host from environment variables.
### It is not intended to be used directly, but rather as a base for other services that require the OLLAMA host.
class AlphaServiceBase(object):
    def __init__(self, level: str = "super"):
        super().__init__()
        self.level = level
        self.ollama_host = os.environ.get("OLLAMA_HOST")
        self.chat_model = os.environ.get("OLLAMA_MODEL")
        self.collection_name = f"alpha_knowledgebase_{self.level}"

    def __str__(self):
        return f"AlphaServiceBase: {self.ollama_host}"
    
    # def chat_message(self, query: ChatQuery) -> str:
    #     pass
    
### This class is responsible for querying a vector collection using the Ollama embedding function.
### It initializes the ChromaDB client and retrieves relevant documents based on a given prompt.
class AlphaChromaService(AlphaServiceBase):
    def __init__(self, level: str = "super"):
        super().__init__(level)
        # Configuration
        self.chroma_path = os.environ.get("CHROMADB_PATH")
        if not self.chroma_path:
            raise ValueError("CHROMADB_PATH environment variable is not set.")
        self.collection_level = self.collection_name
        self.collection_all = "alpha_knowledgebase_general"
        #self.embed_model = "nomic-embed-text:latest"

    ### The query_collection method takes a search query and returns the results from the collection.
    ### It also handles errors that may occur during the querying process.
    def query_collection(self, question: str, n_results: int = 10):
        """Queries the vector collection with a given prompt to retrieve relevant documents.

        Args:
            prompt: The search query text to find relevant documents.
            n_results: Maximum number of results to return. Defaults to 10.

        Returns:
            dict: Query results containing documents, distances and metadata from the collection.

        Raises:
            ChromaDBError: If there are issues querying the collection.
        """
        merged_documents = []
        try:
            # embedding = OllamaEmbeddingFunction(
            #     url=f"{self.ollama_host}/api/embeddings",
            #     model_name = self.chat_model,
            #     #model_name="nomic-embed-text:latest",
            # )
            
            # Initialize the ChromaDB client
            chroma_client = chromadb.Client(
                database="alpha_knowledgebase", 
                tenant="default_tenant",
                settings = Settings(
                    environment = "local",
                    is_persistent = True,
                    persist_directory = os.environ.get("CHROMADB_PATH"),
                    allow_reset = True
                )
            )
            
            # qvector = embedding(question).tolist()
            # print(qvector)

            cross_ranking = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)

            # Check if the collection_level exists
            collection_level = chroma_client.get_collection(
                    name=self.collection_name,
                    #embedding_function=embedding,
                    #metadata={"hnsw:space": "cosine"},
                )
            if collection_level:
                results = collection_level.query(query_texts=[question], n_results=n_results)
                # results = collection_level.query(query_embeddings=qvector, n_results=n_results)
                
                # rerank the results with original query and documents returned from Chroma
                scores = cross_ranking.predict([(question, doc) for doc in results["documents"][0]])
                # get the highest scoring document
                if len(scores) > 0:
                    # Get the document with the highest score
                    merged_documents += [results["documents"][0][np.argmax(scores)]]

            # Check if the collection_all exists
            collection_all = chroma_client.get_collection(
                    name=self.collection_all,
                    #embedding_function=embedding,
                    #metadata={"hnsw:space": "cosine"},
                )
            
            if collection_all:
                results = collection_all.query(query_texts=[question], n_results=n_results)
                # results = collection_all.query(query_embeddings=qvector, n_results=n_results)
                # rerank the results with original query and documents returned from Chroma
                scores = cross_ranking.predict([(question, doc) for doc in results["documents"][0]])
                if len(scores) > 0:
                    # Get the document with the highest score
                    merged_documents += [results["documents"][0][np.argmax(scores)]]
            
        except Exception as e:
            raise ValueError(f"An error occurred while getting the vector collection: {e} with path: {self.chroma_path}")
            
        return merged_documents

### This class is responsible for generating chat messages based on user queries.
### It uses the Ollama client to interact with the chat model and the AlphaChromaService to retrieve relevant documents.
### It initializes the chat model and handles the chat message generation process.
### The chat_message method takes a ChatQuery object and returns the generated chat message.     
class ChatService(AlphaServiceBase):
    def __init__(self, level: str = "super"):
        super().__init__(level)
        # Configuration
        self.chat_model = os.environ.get("OLLAMA_MODEL")
        if not self.chat_model:
            raise ValueError("OLLAMA_MODEL environment variable is not set.")

    ### The chat_message method takes a ChatQuery object and generates a chat message based on the provided query.
    ### It uses the Ollama client to interact with the chat model and the AlphaChromaService to retrieve relevant documents.
    ### It returns the generated chat message as a string.
    def chat_message(self, query: ChatQuery)-> str:
        """
            Generates a chat message based on the provided query.
        """
        question = query.data.query
        answer = None

        print(f"Question: {question}")
        #context service
        start_time = datetime.now()
        chroma_service = AlphaChromaService(level=self.level)
        merged_documents = chroma_service.query_collection(question)
        time_diff = datetime.now() - start_time

        print(f"Time taken to query vector DB collection: {time_diff}")

        if merged_documents:
            
            # Convert list of strings to a single string
            relevant_text = "\n\n".join(merged_documents)
            #print (f"Document: {relevant_text}")

            # start_time = datetime.now()
            # encoder_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            # ranks = encoder_model.rank(question, merged_documents, top_k=3, return_documents=True)
            # for rank in ranks:
            #     # relevant_text += document[rank["corpus_id"]]
            #     relevant_text += rank["text"] + "\n"
            answer = relevant_text

            # time_diff = datetime.now() - start_time
            # print(f"Time taken to CrossEncoder: {time_diff} \n\n before relevant_text: \n{relevant_text}")

            
            # Check for relative keywords
            import re
            if not any(re.search(rf'\b{re.escape(keyword)}\b', answer, re.IGNORECASE) for keyword in question.lower().split()):
                answer = ""

            #print(f"After relevant_text: \n{answer}")
            #client config
            start_time = datetime.now()
            client = Client(host=self.ollama_host)
            response: ChatResponse = client.chat(
                model=self.chat_model,
                stream=False,
                messages=[
                    {
                        "role": "system",
                        "content": prompt_knowledgebase,
                    },
                    {
                        "role": "user",
                        "content": f"Context: {answer}, Question: {question}",
                    },
                ],
            )
            time_diff = datetime.now() - start_time
            answer = response["message"]["content"]
            # start_time = datetime.now()
            # answer = self.llm_chat_message(answer, question)
            # time_diff = datetime.now() - start_time
            print(f"Time taken to Chat with LLM: {time_diff}")
            print(f"Answer: {answer}")

            
        return answer
    
    def llm_chat_message(self, context: str, question: str) -> str:
        """
            Generates a chat message based on the provided query.
        """
        messages = [
            ("system", prompt_knowledgebase),
            ("user", f"Context: {context}, Question: {question}"),
        ]
    
        response = ChatOllama(
            model = self.chat_model,
            base_url = self.ollama_host,
            temperature = 0.7,
            num_predict = 256,
            #format="json"
            # other params ...
        ).invoke(messages)

        print(f"LLM Chat Answer: {response.content}")
        return response.content