from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import TextLoader
import docx2txt
import os
from tenacity import retry, wait_exponential, stop_after_attempt
from langchain_groq import ChatGroq

class DocumentSummarizer:
    def __init__(self, model="gemini-pro", api_key="AIzaSyDiR9XUm72YuSDrfZSdxdVkQLOSHGI7Xzg"):
        # Initialize LLM and summarizer chain
        self.llm =  ChatGroq(
    model="mixtral-8x7b-32768",
    api_key="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")
        
        self.summary_chain = self._setup_summary_chain()

    def _setup_summary_chain(self):
        # Summarization prompt template
        ap_prompt_template = """
        You are an expert summarizer with a deep understanding of extracting key insights from lengthy and complex documents. Your task is to summarize the provided chunk of text effectively by:

        Using clear, concise, and professional language that retains the core message.

        Extracting and highlighting critical details such as important concepts, key findings, dates, numbers, or statistics.

        Preserving the original context and meaning without adding personal opinions or interpretations.

        Generating a comprehensive summary with sufficient depth. If the provided text is extensive, structure the summary into well-formed paragraphs that flow logically, covering all major points. For shorter content, provide a concise summary in a few lines.

        Ensuring smooth readability and logical connections between key ideas.

        Chunk of Text:
        {text}

        Provide a clear and detailed summary of the above text, scaling the length based on the amount of information. Begin directly with the core information, avoiding introductory phrases like "The text discusses" or "This section explains." Focus solely on delivering the summary in a structured and coherent manner. Do not use bullet points, asterisks, or any formatting symbols. Present the summary in plain, continuous text.


        """
        
        map_prompt = PromptTemplate(template=ap_prompt_template, input_variables=["text"])

        return load_summarize_chain(
            llm=self.llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=map_prompt,
            return_intermediate_steps=False,
            verbose=False,
        )

    # Retry mechanism for API rate limits and temporary errors
    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
    async def invoke_summary_chain(self, chunks):
        return self.summary_chain.invoke(chunks)

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

    def chunk_content(self, text, chunk_size=1000, chunk_overlap=150):
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.create_documents([text])
        return chunks

    async def summarize_document(self, file_path):
        try:
            # Load file content
            content = self.load_file_content(file_path)

            # Split content into chunks
            chunks = self.chunk_content(content)

            # Summarize using the summary chain
            summary_result = self.invoke_summary_chain(chunks)

            # Extract and return the final summary
            return summary_result['output_text']

        except Exception as e:
            return f"Error: {e}"

# Main execution
if __name__ == "__main__":
    file_path = "/content/Nepal.pdf"
    summarizer = DocumentSummarizer()
    final_summary = summarizer.summarize_document(file_path)
    print(final_summary)
