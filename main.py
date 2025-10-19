from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import zipfile
from xml.etree.ElementTree import Element, SubElement, ElementTree
import subprocess
from pathlib import Path

class UserInput(BaseModel):
    message: str

class GeneratedProblems(BaseModel):
    problems: str

PROMPT = Path("txt_format.txt").read_text()

MODEL = "gpt-4o-mini"

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_model=GeneratedProblems)
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

    return GeneratedProblems(problems=reply)

@app.post("/convert")
async def convert_problems(input: GeneratedProblems):
    # format the problems or check if the problems are already formatted

    input_file = 'placeholder.txt'

    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(input.problems)
        f.flush()

    if not Path(input_file).exists():
        return {"error": "File not found"}

    try:
        subprocess.run(["text2qti", input_file], check=True)
    except subprocess.CalledProcessError as e:
        return {"error": f"text2qti failed: {e}"}

    zip_path = Path(input_file).with_suffix(".zip")
    if not zip_path.exists():
        return {"error": "Zip not found"}

    return FileResponse(
        path=zip_path,
        filename=zip_path.name,
        media_type="application/zip"
    )