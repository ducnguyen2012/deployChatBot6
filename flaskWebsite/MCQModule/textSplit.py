from pypdf import PdfReader

import random
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf_reader = PdfReader(file)
        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            #! extract text và split lines
            page_text = page.extract_text().splitlines()
            # for qua từng dòng để lấy text
            text += "\n".join([line for line in page_text if line[0].isalpha()])
    return text
def select_text_from_pdf(pdf_path, batch_size=10000, num_batches=2):
    

    pdf_text = extract_text_from_pdf(pdf_path)

    
    total_words = len(pdf_text)

    # random chọn start indices
    selected_start_indices = random.sample(range(total_words - (batch_size * num_batches)), num_batches)

    
    selected_text = ""

    # extract text trong từng patch và concat
    for start_index in selected_start_indices:
        end_index = start_index + batch_size
        selected_text += pdf_text[start_index:end_index]

    return selected_text
