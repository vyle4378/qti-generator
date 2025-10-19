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
from fastapi import BackgroundTasks
import tempfile

class UserInput(BaseModel):
    message: str

class GeneratedProblems(BaseModel):
    problems: str

PROMPT = Path("txt_format.txt").read_text()

MODEL = "gpt-4o-mini"

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()

# Serve CSS, JS, images from the "static" folder
app.mount("/static", StaticFiles(directory="static"), name="static")
# Serve HTML templates from the "templates" folder
templates = Jinja2Templates(directory="templates")

# Serve the index.html file
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
async def convert_problems(input: GeneratedProblems, background_tasks: BackgroundTasks):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp:
        tmp.write(input.problems)
        tmp.flush()
        input_file = Path(tmp.name)

    try:
        subprocess.run(["text2qti", str(input_file)], check=True)
    except subprocess.CalledProcessError as e:
        input_file.unlink(missing_ok=True)
        return {"error": f"text2qti failed: {e}"}

    zip_path = Path(input_file).with_suffix(".zip")
    if not zip_path.exists():
        input_file.unlink(missing_ok=True)
        return {"error": "Zip not found"}

    # Clean up the temporary files after the response is sent
    background_tasks.add_task(input_file.unlink, missing_ok=True)
    background_tasks.add_task(zip_path.unlink, missing_ok=True)

    return FileResponse(
        path=zip_path,
        filename=zip_path.name,
        media_type="application/zip",
        background=background_tasks
    )