from contextlib import asynccontextmanager
from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from faq_finder import reload_embeddings, calculate_semantic, create_list_of_faq
from functions import preprocess_txt
from main import get_most_probable_answers
import time
import os

model = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2", device="cpu") # Load the pre-trained model
raw_path = "input/faq_all.txt" # this is the file with all FAQs

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here
    print("Application startup: save the time of edit of FAQ")
    app.state.last_modified_time_faq = os.path.getmtime(raw_path)
    yield  # This separates startup and shutdown logic
    # Shutdown logic
    print("Application shutdown")

app = FastAPI(lifespan=lifespan) # Create the FastAPI app instance

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

# Define the input model (if needed)
class InputData(BaseModel):
    user_input: str

# Create a simple route that renders HTML input form
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    print("Monitoring file for changes...")
    app.state.current_modified_time_faq = os.path.getmtime(raw_path)
    if app.state.current_modified_time_faq != app.state.last_modified_time_faq:
        print("FAQ has changed, calculating embedings...")
        app.state.last_modified_time_faq = app.state.current_modified_time_faq
        list_of_faq = create_list_of_faq(raw_path)
        reload_embeddings(list_of_faq, model) # Calculate embeddings for the new FAQ list
    print("FAQ is up to date")
    # Render the HTML template with an input form
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/edit-faq", response_class=HTMLResponse)
async def edit_faq(request: Request):
    print("Reading FAQ file...")
    with open(raw_path, "r", encoding="utf-8") as file:
        faq_content = file.read()
    return templates.TemplateResponse("faq_edit.html", {"request": request, "faq_content": faq_content})

@app.post("/edit-faq", response_class=HTMLResponse)
async def update_faq(request: Request, faq_content: str = Form(...)):
    print("Writing to FAQ file...")
    with open(raw_path, "w", encoding="utf-8", newline='') as file:
        file.write(faq_content)
    print("Finished writing to FAQ file.")
    return RedirectResponse(url="/", status_code=303)

# Create a POST endpoint to handle the form submission
@app.post("/submit", response_class=HTMLResponse)
async def handle_input(request: Request, user_input: str = Form(...)):
    #processed_path = "processed/faq_processed2.txt" # toto menim
    
    #print("Preprocessing text...")
    # Save preprocessed text to a file
    #preprocess_txt(raw_path, processed_path)

    print("Creating list of FAQ...")
    # Create list of faq - without \n
    list_of_faq = create_list_of_faq(raw_path) # jedno z tychto vkladam do calculate_semantic funkcie
    #list_of_faq_processed = create_list_of_faq(processed_path) # jedno z tychto vkladam do calculate_semantic funkcie

    print("Calculating semantic probability...")
    semantic_probability = calculate_semantic(user_input, list_of_faq, model)
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