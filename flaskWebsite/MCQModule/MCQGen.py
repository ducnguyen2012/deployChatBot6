import json
import re
import os
from MCQModule.textSplit import select_text_from_pdf
import google.generativeai as genai
from dotenv import load_dotenv
#! Giữ api key ở file .env và cho vào gitignore khi đẩy lên git
load_dotenv()
genai.configure(api_key=os.getenv("KEY"))

def MCQResponse(num_questions, difficulty):
    #! Fixing bug: Hiện tại chưa prompt được để khiến cho mô hình gen ra câu hỏi phù hợp
    if (difficulty == "Hard" or difficulty == "Medium"):
        difficulty = "Easy"
    pdf_path = "../pdfData/Cells and Chemistry of Life.pdf"
    # prompt answer
    Ans_format = """Please generate Answer Key in the following Format:
    ## Answer Key:
    **Q{question_number}. {correct_option} , Q{question_number}. {correct_option} ,**"""

    q_format = """Please generate multiple choice questions in the following format:

     **Question No. {question_number}:** {question}

   a. {option_a}
   b. {option_b}
   c. {option_c}
   d. {option_d}

  Based on the given text only: {text}"""
    #! extract text từ pdf
    pdf_text = select_text_from_pdf(pdf_path)
    # Tạo prompt cho mô hình dựa trên độ khó
    difficulty_prompt = {
        "Easy": f"Please generate {num_questions} very easy MCQ questions. These questions should be straightforward and have an answer key based solely on the given text. {q_format}{Ans_format}{pdf_text}",
        "Medium": f"Please generate {num_questions} very easy MCQ questions. These questions should be straightforward and have an answer key based solely on the given text. {q_format}{Ans_format}{pdf_text}",
        "Hard": f"Please generate {num_questions} very easy MCQ questions. These questions should be straightforward and have an answer key based solely on the given text. {q_format}{Ans_format}{pdf_text}"
    }

    prompt = difficulty_prompt.get(difficulty, "Invalid difficulty level. Please choose from 'easy', 'medium', or 'hard'.")

    
    model = genai.GenerativeModel('gemini-1.5-pro')

    
    response = model.generate_content(prompt)
    model_response = response.text
    #! xử lý response của model, loại bỏ ký tự [,],#,*
    cleaned_text = re.sub(r'[*#]', '', model_response)
    start_index = cleaned_text.find("Answer Key")
    answer_key = cleaned_text[start_index:]
    generated_que = cleaned_text[:start_index]
    
    # tách response thành ans và question
    questions = []
    key_answers = [key.split(". ")[1] for key in answer_key.split(", ")]  
    #print("This is key_answers:" + str(key_answers))
    #print("this is generated_que: " +str(generated_que))
    for index, q in enumerate(generated_que.split("Question No. ")[1:]):
        parts = q.split("\n")
        
        question_text = parts[0].strip()
        question_text = question_text[question_text.find(":")+1:]
        
        
        options = {}
        for part in parts[1:]:
            
            if part.strip() == '':
                continue
            if ". " in part:
                key, value = part.split(". ", 1)
                options[key] = value
        
            
        print("This is my option: "+str(options))

    
    
        correct_answer = key_answers[index-1]

        questions.append({
            'text': question_text,
            'options': options,
            'correct': correct_answer.strip()  # Include the correct answer
        })
    
    # tạo dictionary response
    response_dict = {
        'questions': questions
    }
    
    # chuyển về json nhằm đẩy lên frontend
    response_json = json.dumps(response_dict, indent=2)

    print("THis is response json from MCQGen: " + str(response_json))
    return response_json
