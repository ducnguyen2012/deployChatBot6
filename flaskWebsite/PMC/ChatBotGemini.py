
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from io import BytesIO
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores.faiss import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("KEY"))

def get_pdf_text(pdf_docs):
    text = ''
    if pdf_docs is not None:
        if isinstance(pdf_docs, list):
            for pdf in pdf_docs:
                pdf_reader = PdfReader(BytesIO(pdf.read()))
                for page in pdf_reader.pages:
                    text += page.extract_text()
        else:  # If pdf_docs is a single file
            pdf_reader = PdfReader(BytesIO(pdf_docs.read()))
            for page in pdf_reader.pages:
                text += page.extract_text()
    return text



def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001', google_api_key=os.getenv('KEY'))
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local('faiss-index')

def get_conversational_chain():
    prompt_template = '''
    The answer must be in 50 words and details.\ 
    Answer all the question as detailed as possible from the provided context.\
    \n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    '''
    model = ChatGoogleGenerativeAI(model='gemini-pro', temperature=0.1)

    prompt = PromptTemplate(template=prompt_template, input_variables=['context', 'question'])
    chain = load_qa_chain(model, chain_type='stuff', prompt=prompt)
    return chain

def ChatBot(pdf_path: str,user_question: str):
    embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001', google_api_key=os.getenv('KEY'))

    try:
        new_db = FAISS.load_local('faiss-index', embeddings, allow_dangerous_deserialization=True)
    except ValueError as e:
        print("error!")
        return

    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()

    response = chain(
        {'input_documents': docs, 'question': user_question}
    )

    return response['output_text']

# print(ChatBot("./Cells and Chemistry of Life.pdf", "What is a cell? answer in detail!"))





