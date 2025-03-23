import os
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

class RAGSystem:
    def __init__(self, pdf_path, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the RAG system with file path and embedding model."""
        self.pdf_path = pdf_path
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.llm = ChatGroq(
            model="mixtral-8x7b-32768",
            api_key="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"
        )
        self.vector_store = None
    
    async def load_pdf(self):
        """Reads a PDF file and returns its pages as Document objects."""
        loader = PyPDFLoader(self.pdf_path)
        return loader.load()
    
    async def split_text(self, docs, chunk_size=1000, chunk_overlap=150):
        """Splits extracted text into chunks for better embedding and retrieval."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return splitter.split_documents(docs)
    
    async def load_and_process_documents(self):
        """Loads, processes, and stores embeddings in ChromaDB."""
        documents = await self.load_pdf()
        final_documents = await self.split_text(documents)
        
        self.vector_store = Chroma.from_documents(
            documents=final_documents,
            embedding=self.embeddings,
            collection_name="agentic-rag_collection",
            persist_directory="./chroma_langchain_db"
        )
    
    async def query_documents(self, query, top_k=5):
        """Queries the document store and returns a response based on the context."""
        docs_chroma = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        context_text = "\n\n".join([doc.page_content for doc, _ in docs_chroma])
        
        if not context_text.strip():
            return "Your question is outside the document's content."
        
        prompt_template = ChatPromptTemplate.from_template(
            """
            Answer the question based only on the given CONTEXT:
            
            CONTEXT:
            {context}
            
            Question: {question}
            
            Rules:
            - If the answer exists in the context, provide a **detailed answer**.
            - **Do NOT include any information that is not present in the context**.
            - If the answer is **not** in the context, reply: "Your question is outside the document's content."
            - Do NOT say "according to the context" or similar phrases.
            """
        )
        prompt = prompt_template.format(context=context_text, question=query)
        
        llm_response = self.llm.invoke(prompt) 
        
        return llm_response.content if hasattr(llm_response, "content") else str(llm_response)

async def process_pdf_query(pdf_path, query):
    """Processes a PDF query using the RAG system."""
    rag_system = RAGSystem(pdf_path)
    await rag_system.load_and_process_documents()  
    return await rag_system.query_documents(query) 

# Example usage:
# import asyncio
# response = asyncio.run(process_pdf_query("path/to/pdf", "Your query here"))
# print(response)