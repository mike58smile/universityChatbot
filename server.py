from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from faq_finder import calculate_semantic, create_list_of_faq
from functions import preprocess_txt
from main import get_most_probable_answers

app = FastAPI()

app.mount("/web", StaticFiles(directory="web"), name="web")
templates = Jinja2Templates(directory="web")

def format_list_answers(answer: list[str]):
    formatted_answer = answer
    formatted_answer = answer.replace("\n", "<br>")
    lines = answer.split("\n\n")
    print(lines[0])
    

    for index, answer_i in enumerate(lines):
        firstAnswer = answer_i.split("\n")
        if len(firstAnswer) >= 3 and firstAnswer[1].startswith("1.") and firstAnswer[2].startswith("2."):
            firstAnswer[0] = f"<b>{firstAnswer[0]}</b>"
            formatted_answer = "\n".join(firstAnswer)
            print(formatted_answer)
            lines[index] = formatted_answer

    original_text = "\n\n".join(lines)
    original_text = original_text.replace("\n", "<br>")
    return original_text

    # firstAnswer = lines[0].split("\n")
    # if len(firstAnswer) >= 3 and firstAnswer[1].startswith("1.") and firstAnswer[2].startswith("2."):
    #     firstAnswer[0] = f"<b>{firstAnswer[0]}</b>"
    #     formatted_answer = "\n".join(firstAnswer)
    #     print(formatted_answer)
    #     lines[0] = formatted_answer
    #     original_text = "\n\n".join(lines)
    #     answer = original_text

# Define the input model (if needed)
class InputData(BaseModel):
    user_input: str

# Create a simple route that renders HTML input form
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Create a POST endpoint to handle the form submission
@app.post("/submit", response_class=HTMLResponse)
async def handle_input(request: Request, user_input: str = Form(...)):
    raw_path = "input/faq_all.txt" # toto menim
    #processed_path = "processed/faq_processed2.txt" # toto menim
    
    #print("Preprocessing text...")
    # Save preprocessed text to a file
    #preprocess_txt(raw_path, processed_path)

    print("Creating list of FAQ...")
    # Create list of faq - without \n
    list_of_faq = create_list_of_faq(raw_path) # jedno z tychto vkladam do calculate_semantic funkcie
    #list_of_faq_processed = create_list_of_faq(processed_path) # jedno z tychto vkladam do calculate_semantic funkcie

    print("Calculating semantic probability...")
    semantic_probability = calculate_semantic(user_input, list_of_faq, SentenceTransformer("paraphrase-multilingual-mpnet-base-v2", device="cpu"))
    print("Getting most probable answers...")
    answer = get_most_probable_answers(list_of_faq, semantic_probability, 3)

    # if len(answer) >= 3 and lines[1].startswith("1.") and answer[2].startswith("2."):
    #     lines[0] = f"<b>{answer[0]}</b>"
    #     answer = "\n".join(lines)
    formatted_answer = format_list_answers(answer)
    # Here, user_input will contain the form data entered by the user
    return templates.TemplateResponse(
        "answer.html", {"request": request, "answer": formatted_answer}
    )