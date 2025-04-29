import os
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import asyncio

api_key = "AIzaSyCZZVyJ-68pMNJbJMXTaDIdSu7XZA9hKqc"

print("DOne")

class RAGSystem:
    def __init__(self, pdf_path, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the RAG system with file path and embedding model."""
        self.pdf_path = pdf_path
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
        self.vector_store = None
        self.documents_loaded = False
    
    async def load_pdf(self):
        """Reads a PDF file and returns its pages as Document objects."""
        try:
            # Using asyncio.to_thread to make the synchronous PyPDFLoader operation non-blocking
            return await asyncio.to_thread(lambda: PyPDFLoader(self.pdf_path).load())
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return []
    
    async def split_text(self, docs, chunk_size=1000, chunk_overlap=200):
        """Splits extracted text into chunks for better embedding and retrieval."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        # Using asyncio.to_thread to make the synchronous split_documents operation non-blocking
        return await asyncio.to_thread(lambda: splitter.split_documents(docs))
    
    async def load_and_process_documents(self):
        """Loads, processes, and stores embeddings in ChromaDB in an asynchronous manner."""
        documents = await self.load_pdf()
        
        if not documents:
            print("No documents were loaded from the PDF.")
            return False
            
        final_documents = await self.split_text(documents)
        
        if not final_documents:
            print("No text chunks were created from the documents.")
            return False
        
        # Using asyncio.to_thread to make the synchronous Chroma operation non-blocking
        self.vector_store = await asyncio.to_thread(
            lambda: Chroma.from_documents(
                documents=final_documents,
                embedding=self.embeddings,
                collection_name="agentic-rag_collection",
                persist_directory="./chroma_langchain_db"
            )
        )
        
        self.documents_loaded = True
        return True
    
    async def query_documents(self, query, top_k=5):
        """Queries the document store and returns a response based on the context."""
        if not self.documents_loaded or not self.vector_store:
            return "I don't have any documents loaded. Please upload documents first or try another query."
        
        # Using asyncio.to_thread for the similarity search which is synchronous
        docs_chroma = await asyncio.to_thread(
            lambda: self.vector_store.similarity_search_with_score(query, k=top_k)
        )
        
        # Filter out documents with low relevance scores (higher score = less relevant)
        relevant_docs = [(doc, score) for doc, score in docs_chroma if score < 1.2]
        
        if not relevant_docs:
            return "I don't have any answer for this query in the documents. Please upload different documents or ask another query."
        
        context_text = "\n\n---\n\n".join([f"[Document {i+1}]\n{doc.page_content}" 
                                         for i, (doc, _) in enumerate(relevant_docs)])
        
        print("Yaha ayo__________________")
        
        prompt_template = ChatPromptTemplate.from_template(
            """
            You are WorkSphere Bot, a helpful assistant that provides information from documents and handles user queries professionally.
            
            CONTEXT DOCUMENTS:
            {context}
            
            USER QUERY: {question}
            
            SYSTEM INSTRUCTIONS (NOT TO BE MENTIONED IN YOUR RESPONSE):
            1. If the user's query is a greeting (like "hi", "hello", "hey", "good morning", etc.) or general introduction:
            - Respond with: "Hello! I'm WorkSphere Bot. How may I assist you today? I can help answer questions about the documents you've uploaded."
            - Do NOT reference any document content for greetings.
            
            2. For document-specific queries:
            a. For resume/CV documents:
                - Provide factual information about qualifications, experience, skills, etc.
                - Be precise about dates, job titles, and educational qualifications
            
            b. For business documents:
                - Focus on extracting key business information, figures, and insights
            
            c. For images or photos:
                - If the query relates to visual content that you cannot access, state: "I'm unable to process or view images directly. Please describe what you'd like to know about the document."
            
            3. For regular document queries:
            a. Analyze the document context carefully.
            b. If the answer is clearly present in the context:
                - Provide a comprehensive and detailed answer
                - Include specific details, names, dates, and facts from the context
                - Format your answer to improve readability when appropriate
            c. If the answer is partially present:
                - Answer only the part that can be answered from the context
                - For missing information, clearly state: "The document doesn't contain information about [specific aspect]"
            d. If the answer is not present in the context at all:
                - Respond ONLY with: "I don't have any answer for this query in the documents. Please upload different documents or ask another query."
            
            4. CRITICAL RULES:
            - Do NOT include any information that is not present in the context
            - Do NOT use phrases like "based on the context", "according to the documents", etc.
            - Do NOT make up or infer information that isn't explicitly stated in the context
            - Always verify information before providing it in your answer
            - Keep responses concise yet complete
            
            ANSWER:
            """
        )
        
        prompt = prompt_template.format(context=context_text, question=query)
        
        # Using the async invoke method
        llm_response = await self.llm.ainvoke(prompt)
        
        response_content = llm_response.content if hasattr(llm_response, "content") else str(llm_response)
        
        # Double-check if the response indicates no answer was found
        no_answer_indicators = [
            "i don't have", "cannot find", "no information", "not mentioned", 
            "not present", "not provided", "not available", "not found",
            "document doesn't contain", "documents don't contain"
        ]
        
        if any(indicator in response_content.lower() for indicator in no_answer_indicators):
            return "I don't have any answer for this query in the documents. Please upload different documents or ask another query."
            
        return response_content

async def process_pdf_query(pdf_path, query):
    """Processes a PDF query using the RAG system in a fully asynchronous manner."""
    rag_system = RAGSystem(pdf_path)
    documents_loaded = await rag_system.load_and_process_documents()
    
    if not documents_loaded:
        return "I couldn't process the documents. Please check if the PDF is valid and try again, or upload different documents."
    
    return await rag_system.query_documents(query)

# # # Example usage:
# if __name__ == "__main__":
#     import asyncio
    
#     async def main():
#         try:
#             pdf_path = r"C:\Users\apilt\Desktop\WorkSphere AI\Apil_Thapa_CV.pdf"
#             query = input("Enter your query: ")
            
#             if not os.path.exists(pdf_path):
#                 print(f"File not found: {pdf_path}")
#                 return
                
#             print("Processing your query...")
#             response = await process_pdf_query(pdf_path, query)
#             print("\nResponse:")
#             print(response)
#         except Exception as e:
#             print(f"An error occurred: {e}")
    
#     asyncio.run(main())