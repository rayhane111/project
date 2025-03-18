"""from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from transformers import pipeline
import textwrap
import fitz  # PyMuPDF for PDF
from docx import Document
import openpyxl  # For Excel
from pptx import Presentation
import os

app = FastAPI()

# Serve static files (like index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

# Language codes mapping
LANGUAGE_CODES = {
    "Anglais": "en",
    "Français": "fr",
    "Arabe": "ar",
    "Espagnol": "es",
    "Allemand": "de",
    "Italien": "it",
    "Portugais": "pt",
    "Néerlandais": "nl"
}

# Function to load translation model for dynamic language pairs
def load_translator(src_lang: str, tgt_lang: str):
    src_code = LANGUAGE_CODES.get(src_lang)
    tgt_code = LANGUAGE_CODES.get(tgt_lang)

    if not src_code or not tgt_code:
        raise ValueError(f"Unsupported language pair: {src_lang} -> {tgt_lang}")

    try:
        model_name = f"Helsinki-NLP/opus-mt-{src_code}-{tgt_code}"
        return pipeline("translation", model=model_name)
    except Exception as e:
        if src_code != "en" and tgt_code != "en":
            model_src_to_en = pipeline("translation", model=f"Helsinki-NLP/opus-mt-{src_code}-en")
            model_en_to_tgt = pipeline("translation", model=f"Helsinki-NLP/opus-mt-en-{tgt_code}")
            return (model_src_to_en, model_en_to_tgt)
        else:
            raise ValueError(f"No available translation model for {src_lang} -> {tgt_lang}")

# Function to split text into manageable chunks
def chunk_text(text, max_length=400):
    return textwrap.wrap(text, max_length)

# Extract text from different file types
def extract_text(file: UploadFile):
    if file.filename.endswith(".txt"):
        return file.file.read().decode("utf-8")
    elif file.filename.endswith(".pdf"):
        doc = fitz.open(stream=file.file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    elif file.filename.endswith(".docx"):
        doc = Document(file.file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.filename.endswith(".xlsx"):
        wb = openpyxl.load_workbook(file.file)
        sheets = wb.sheetnames
        text = ""
        for sheet in sheets:
            ws = wb[sheet]
            for row in ws.iter_rows():
                text += "\t".join([str(cell.value or "") for cell in row]) + "\n"
        return text
    elif file.filename.endswith(".pptx"):
        prs = Presentation(file.file)
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

# Upload and translate files
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), src_lang: str = Form(...), tgt_lang: str = Form(...)):
    try:
        text = extract_text(file)
        translators = load_translator(src_lang, tgt_lang)

        chunks = chunk_text(text)
        if isinstance(translators, tuple):
            translated_chunks = [translators[1](translators[0](chunk, max_length=400)[0]['translation_text'], max_length=400)[0]['translation_text'] for chunk in chunks]
        else:
            translated_chunks = [translators(chunk, max_length=400)[0]['translation_text'] for chunk in chunks]

        translated_text = " ".join(translated_chunks)
        return JSONResponse(content={"filename": file.filename, "translated_text": translated_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
"""