import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from schemas.schemas import Body
load_dotenv()

# # Access the variables
# api_key = "AIzaSyARnfimL36ApPBnP2lJVCJAYtr8E2Fo10o"

api_key = os.getenv("GROQ_API")

def giveBody(content: str) -> dict:
    """
    This tool generates the body from the content given by the user.

    Args:
    content: This is the text content which is a document.
    """

    print("str ma k aaux a hai", content)

    # Initialize the LLM model
    # llm2 = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

    llm2 = ChatGroq(
            model="gemma2-9b-it",
            api_key=api_key
        )

    # Structured output for Body
    structured_llm2 = llm2.with_structured_output(Body)

    chat_template2 = ChatPromptTemplate.from_messages(
    [
        ("system", """You are a helpful assistant designed to analyze the text given by the user and provide the title, body based on the user-provided schema.
        
        IMPORTANT: Each heading MUST have a list of bullet points. Example structure:
        {{
            "Pages": [
                {{
                    "Headings": "Introduction",
                    "Bulletpoints": ["First point", "Second point", "Third point"]
                }},
                {{
                    "Headings": "Next Section",
                    "Bulletpoints": ["First point", "Second point", "Third point"]
                }}
            ]
        }}"""),
        ("human", "From the below text, analyze properly and provide the proper body part:\n{text}")
    ]
)

    llm_f2 = chat_template2 | structured_llm2

    result2 = llm_f2.invoke({"text": content})

    return {"Body": result2.model_dump()}