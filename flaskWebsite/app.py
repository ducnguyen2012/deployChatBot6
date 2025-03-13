
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
import os
import traceback
# Load key từ env
load_dotenv()
genai.configure(api_key=os.getenv('KEY'))

from flask import Flask, jsonify, request, render_template
from MCQModule.MCQGen import MCQResponse
from PMC.ChatBotGemini import ChatBot

app = Flask(__name__)


# Use an absolute path or configurable environment variable
FILEPATH = '../pdfData/Cells and Chemistry of Life.pdf'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            user_message = request.get_json().get('message')
            if not user_message:
                return jsonify({"error": "Message is required"}), 400
            
            
            bot_response = ChatBot(FILEPATH, user_message)


            return jsonify({"response": bot_response})
        except Exception as e:
            print("An error occurred:", e)
            print(traceback.format_exc())
            return jsonify({"error": "An error occurred: " + str(e)}), 500
    else:
        return render_template('index.html')

@app.route('/question', methods=['GET', 'POST'])
def mcq():
    if request.method == 'POST':
        data = request.json
        num_questions = data.get('numQuestions')
        difficulty = data.get('tone')
        
        mcq_json = MCQResponse(num_questions, difficulty)
       
        return mcq_json, 200, {'Content-Type': 'application/json'}
    else:
        return render_template('MCQ.html')



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
