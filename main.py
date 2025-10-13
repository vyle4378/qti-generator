from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import zipfile
from xml.etree.ElementTree import Element, SubElement, ElementTree

class UserInput(BaseModel):
    message: str

class GenerateProblems(BaseModel):
    problems: str

PROMPT = "Generate problems given the user's topic. \
        Format the problems as follows: \
        Each question must start with the question number followed by a period and space and then the question text. Each question must be separated with a single blank line \
        Examples: \
        Multiple Choice: Each choice needs to start with a lower case alphabet, a, b, c, d, etc. with a close parenthesis. The correct choice is designated with an asterisk. \
        1. What is 2+3? \
        a) 6 \
        b) 1 \
        *c) 5 \
        d) 10 \
        Multiple-answers / multiple-select / select-all-that-apply: Each choice use [] to make the incorrect answers and [*] for the correct answers. \
        1. Which of the following are dinosaurs? \
        [ ] Woolly mammoth \
        [*] Tyrannosaurus rex \
        [*] Triceratops \
        [ ] Smilodon fatalis \
        Short-answer (fill-in-the-blank): The correct answers will use an asterisk followed by one or more spaces or tabs followed by an answer. \
        1. Who lives at the North Pole? \
        * Santa \
        * Santa Claus \
        * Father Christmas \
        * Saint Nicholas \
        * Saint Nick \
        Free-response or Essay: This type of question is indicated by a sequence of three or four hashtags. \
        1. Write an essay. \
        #### \
        File-upload: This type of question is indicated by a sequence of three or four carets. \
        1. Upload a file. \
        ^^^^ \
        True/False: True and False statements start with a) and b). The correct choice is designated with an asterisk. \
        1. Water is liquid. \
        *a) True \
        b) False \
        Do not add any other text to your response. Only output the problems."

MODEL = "gpt-4o-mini"

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_model=GenerateProblems)
async def generate_problems(input: UserInput):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": PROMPT,
            },
            {
                "role": "user",
                "content": input.message
            }
        ]
    )

    assert len(response.choices) == 1
    reply = response.choices[0].message.content

    return GenerateProblems(problems=reply)

@app.post("/convert")
async def convert_problems(input: UserInput):
    data = await generate_problems(input)
    problems = data.problems



    
    