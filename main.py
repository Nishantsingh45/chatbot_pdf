import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pdf_processor import extract_text_from_pdf
from vector_store import VectorStore
from chatbot import Chatbot
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Check if the API key is set
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

vector_store = VectorStore(OPENAI_API_KEY)
chatbot = None

# Create a directory to store uploaded PDFs
UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_index():
    return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global chatbot
    if file.filename.endswith(".pdf"):
        # Save the uploaded PDF
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as pdf_file:
            pdf_file.write(await file.read())

        # Process the saved PDF
        with open(file_path, "rb") as pdf_file:
            text = extract_text_from_pdf(pdf_file)

        vector_store.create_vector_store(text)
        chatbot = Chatbot(vector_store, OPENAI_API_KEY)
        return JSONResponse(content={"message": "PDF uploaded, saved, and processed successfully"}, status_code=200)
    else:
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a PDF file.")

@app.post("/chat")
async def chat(query: str = Form(...)):
    global chatbot
    if not chatbot:
        raise HTTPException(status_code=400, detail="Please upload a PDF file first.")
    response = chatbot.chat(query)
    return JSONResponse(content={"response": response}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
