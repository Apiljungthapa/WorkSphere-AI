import asyncio
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import docx2txt
import os
import time

api_key = "AIzaSyDL2j-N_dmxTLMcIzjJuaWnPrlnlmzO2Qk"

class DocumentSummarizer:
    def __init__(self, model="gemini-1.5-flash", api_key=api_key):
        self.llm = ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
        self.prompt_template = self._create_prompt_template()

    def _create_prompt_template(self):
        template = """
        Summarize the following document effectively:

        {text}

        Provide a clear and comprehensive summary that captures all key points in well-structured paragraphs.
        """
        return PromptTemplate(template=template, input_variables=["text"])

    async def load_file_content(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()
            content = ''.join([page.page_content for page in pages])
        elif ext == '.txt':
            loader = TextLoader(file_path)
            docs = loader.load()
            content = ''.join([doc.page_content for doc in docs])
        elif ext in ['.docx', '.doc']:
            content = docx2txt.process(file_path)
        else:
            raise ValueError("Unsupported file format")
        return content

    def create_optimized_chunks(self, text, max_chunk_size=8000):
        """Create larger chunks to minimize API calls"""
        # First break into paragraphs to maintain context
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) < max_chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        # If we have very few or very small chunks, just return a single chunk
        if len(chunks) <= 1 or all(len(chunk) < max_chunk_size / 4 for chunk in chunks):
            return [text]
            
        return chunks

    async def summarize_chunk(self, chunk_text):
        """Summarize a single chunk of text"""
        try:
            prompt = self.prompt_template.format(text=chunk_text)
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            print(f"Error during summarization: {str(e)}")
            # Add a delay if we hit an error to avoid rapid retries
            await asyncio.sleep(5)
            return f"Error summarizing this section: {str(e)}"

    async def summarize_document(self, file_path):
        try:
            # Load file content
            content = await self.load_file_content(file_path)
            
            # For small documents, just do a single API call
            if len(content) < 8000:
                return await self.summarize_chunk(content)
            
            # For larger documents, create optimized chunks
            chunks = self.create_optimized_chunks(content)
            
            # Summarize each chunk (with fewer API calls)
            print(f"Processing document in {len(chunks)} chunks")
            
            # Process chunks sequentially to avoid rate limits
            summaries = []
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}")
                summary = await self.summarize_chunk(chunk)
                summaries.append(summary)
                
                # Add a small delay between chunks to avoid rate limits
                if i < len(chunks) - 1:
                    await asyncio.sleep(2)
            
            # If we have multiple chunks, we need a final summary
            if len(summaries) > 1:
                # Join the summaries and create a final summary
                combined_summary = "\n\n".join(summaries)
                
                # Don't exceed context window
                if len(combined_summary) > 12000:
                    combined_summary = combined_summary[:12000]
                
                print("Creating final summary")
                final_prompt = f"""
                Synthesize these section summaries into one coherent document summary:
                
                {combined_summary}
                
                Provide a clear, comprehensive final summary that integrates all key points.
                """
                final_summary = await self.llm.ainvoke(final_prompt)
                return final_summary.content
            else:
                # If only one chunk, return its summary
                return summaries[0]
                
        except Exception as e:
            return f"Error: {str(e)}"

# # Example usage
# async def main():
#     file_path = r"C:\Users\apilt\Desktop\WorkSphere AI\Apil_Thapa_CV.pdf"  # Change to your file path
#     summarizer = DocumentSummarizer()
#     final_summary = await summarizer.summarize_document(file_path)
#     print("\nFINAL SUMMARY:")
#     print(final_summary)

# if __name__ == "__main__":
#     asyncio.run(main())