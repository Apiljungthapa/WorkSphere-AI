import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from schemas.schemas import Introduction
load_dotenv()

# Access the variables
# api_key = "AIzaSyARnfimL36ApPBnP2lJVCJAYtr8E2Fo10o"

api_key = os.getenv("GROQ_API")

def giveIntroduction(content: str) -> dict:
    """
    This tool generates the introduction from the content given by the user.

    Args:
    content: This is the text content which is a document.
    """

    # Initialize the LLM model
    # llm1 = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

    llm1 = ChatGroq(
            model="gemma2-9b-it",
            api_key=api_key
        )

    # Structured output for Introduction
    structured_llm1 = llm1.with_structured_output(Introduction)

    # Define the chat template
    chat_template1 = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant designed to analyze the text given by the user and provide the title, introduction based on the user-provided schema."),
            ("human", "From the below text, analyze properly and provide the proper introduction part:\n{text}")
        ]
    )

    # Combine the chat template with structured output
    llm_f1 = chat_template1 | structured_llm1

    # Get the result from the model
    result1 = llm_f1.invoke({"text": content})

    # Return the result
    return {"Introduction": result1.model_dump()}

