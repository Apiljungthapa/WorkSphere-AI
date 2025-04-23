
from imports import *
from schemas.schemas import Goals, Introduction, BodySlides, Body, Conclusion, Document, FinalPPT
from tools.bodytool import giveBody
from tools.conclusiontool import giveConclusion
from tools.introtool import giveIntroduction
from tools.finalizetool import Finalize
from utils.state import ContentState  
from langchain_groq import ChatGroq

api_key = os.getenv("GROQ_API")
# self.llm = GoogleGenerativeAI(model="gemini-1.5-flash", google_api_key="AIzaSyAgz_TNz-6aQV0mSwWPxcy9aaGKwWjr7U4")

def process_pdf(pdf_path,api_key):
    def doc_words_join(inp):
        loader = PyPDFLoader(inp)
        pages = loader.load_and_split()

        whole_doc_text = ''
        for i in range(len(pages)):
            whole_doc_text+=pages[i].page_content
        return whole_doc_text
    
    allwords=doc_words_join(pdf_path)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
    chunks = text_splitter.create_documents([allwords])
    chunks_prompt="""
    Please summarize the below Document. The summary must be very clear with proper phrases and easy words:
    Document:`{text}'
    Summary:
    """
    map_prompt_template=PromptTemplate(input_variables=['text'], template=chunks_prompt)

    system = """

    You are an expert summarizer with a deep understanding of extracting key insights from lengthy and complex documents.

    Your task is to carefully analyze the given text chunks and capture all the important details. Ensure that no information is missed and present everything in clear, continuous text.
    
    """

    human="{text}"


    final_combine_prompt=ChatPromptTemplate.from_messages([SystemMessagePromptTemplate.from_template(system),
                                                    HumanMessagePromptTemplate.from_template(human)])
    
    
    # llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

    llm_model = ChatGroq(
            model="gemma2-9b-it",
            api_key=api_key
        )

    
    summary_chain = load_summarize_chain(llm=llm_model, chain_type='map_reduce', map_prompt=map_prompt_template, combine_prompt=final_combine_prompt,
                                            verbose=False)


    resultss = summary_chain.invoke(chunks)

    data=resultss['input_documents'][0].page_content

    graph_builder = StateGraph(ContentState)

    graph_builder.add_node("intro_Agent", giveIntroduction)
    graph_builder.add_node("body_Agent", giveBody)
    graph_builder.add_node("conclusion_Agent", giveConclusion)
    graph_builder.add_node("PPT_Agent", Finalize)

    graph_builder.add_edge(START, "intro_Agent")
    graph_builder.add_edge(START, "body_Agent")
    graph_builder.add_edge(START, "conclusion_Agent")


    graph_builder.add_edge("intro_Agent","PPT_Agent")
    graph_builder.add_edge("body_Agent","PPT_Agent")
    graph_builder.add_edge("conclusion_Agent","PPT_Agent")

    graph_builder.add_edge("PPT_Agent",END)

    graph = graph_builder.compile()

    output = graph.invoke({'messages': [{"role": "user", "content": data}]})

    introsection = output['FinalResult']['Introduction_']

    bodysection = output['FinalResult']['Body_']

    concsection = output['FinalResult']['Conclusion_']

    introsection = output['FinalResult']['Introduction_']
    bodysection = output['FinalResult']['Body_']
    concsection = output['FinalResult']['Conclusion_']

    return introsection, bodysection, concsection


# print(process_pdf(r"C:\Users\apilt\Desktop\WorkSphere AI\22067753 Apil Thapa (11).pdf",api_key))