from fastapi import FastAPI, WebSocket, UploadFile, HTTPException, Request
import sqlite3
import uuid
import os
import PyPDF2
import time
from collections import defaultdict
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

app = FastAPI()

# In-memory store for tracking request timestamps
request_timestamps = defaultdict(list)
RATE_LIMIT = 5 
TIME_WINDOW = 60

# Initialize LLM and embeddings
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.2,
    convert_system_message_to_human=True
)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",google_api_key=os.getenv("GEMINI_API_KEY"))

# Database setup
DATABASE = "documents.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def setup_database():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            '''CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                upload_date TEXT NOT NULL,
                text_content TEXT NOT NULL
            )'''
        )

# Rate limiting logic
def is_rate_limited(ip: str) -> bool:
    current_time = time.time()
    request_timestamps[ip] = [timestamp for timestamp in request_timestamps[ip] if current_time - timestamp < TIME_WINDOW]
    if len(request_timestamps[ip]) >= RATE_LIMIT:
        return True
    request_timestamps[ip].append(current_time)
    return False

# PDF Upload Endpoint
@app.post("/upload/")
async def upload_pdf(file: UploadFile, request: Request):
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    pdf_id = str(uuid.uuid4())
    file_location = f"./uploaded_pdfs/{pdf_id}.pdf"
    os.makedirs("./uploaded_pdfs", exist_ok=True)
    
    with open(file_location, "wb") as f:
        f.write(await file.read())

    try:
        with open(file_location, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text_content = ""
            for page in reader.pages:
                text_content += page.extract_text()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF")

    with get_db() as conn:
        conn.execute(
            "INSERT INTO documents (id, filename, upload_date, text_content) VALUES (?, ?, datetime('now'), ?)",
            (pdf_id, file.filename, text_content),
        )

    return {"message": "File uploaded successfully", "id": pdf_id}

@app.get("/health")
async def health(request: Request):
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    return {"status": "ok"}

@app.websocket("/ws/qa/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:  
            data = await websocket.receive_json()
            client_ip = websocket.client.host 
            
            # Apply rate limiting for each request
            if is_rate_limited(client_ip):
                await websocket.send_json({"error": "Rate limit exceeded. Try again later."})
                continue 

            pdf_id = data.get("pdf_id")
            question = data.get("question")

            # Retrieve document text from the database
            with get_db() as conn:
                result = conn.execute("SELECT text_content FROM documents WHERE id = ?", (pdf_id,)).fetchone()
            
            if not result:
                await websocket.send_json({"error": "Document not found."})
                continue

            document_text = result["text_content"]

            # Split text and embed
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
            texts = text_splitter.split_text(document_text)
            vector_index = FAISS.from_texts(texts, embeddings).as_retriever(search_kwargs={"k": 5})  # FAISS used here

            template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Keep the answer as concise as possible.
            {context}
            Question: {question}
            Helpful Answer:"""
            QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
            qa_chain = RetrievalQA.from_chain_type(
                model,
                retriever=vector_index,
                return_source_documents=True,
                chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
            )

            result = qa_chain({"query": question})
            answer = result.get("result", "I don't know. Thanks for asking!")

            await websocket.send_json({"answer": answer})

    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()



@app.get("/get_all_pdfs/")
async def get_all_pdfs(request: Request):
    client_ip = request.client.host
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
    
    try:
        with get_db() as conn:
            cursor = conn.execute("SELECT id, filename, upload_date FROM documents")
            pdfs = cursor.fetchall()
        
        if not pdfs:
            return {"message": "No PDFs found in the database."}
        
        pdf_details = [
            {"id": row["id"], "filename": row["filename"], "upload_date": row["upload_date"]}
            for row in pdfs
        ]
        
        return {"pdfs": pdf_details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving PDFs: {str(e)}")
