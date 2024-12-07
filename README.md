# SmartPDF

This backend service enables users to upload PDF documents and ask questions about the content in real time using NLP capabilities. The service processes the documents, extracts their content, and responds to user queries via WebSocket communication.

## Features
- **PDF Upload**: Upload and store PDF documents, with text extraction for processing.
- **Real-Time Q&A**: Users can ask questions about uploaded documents through WebSocket connections and get real-time answers.
- **Data Storage**: Metadata and text content are stored in SQLite for efficient retrieval.
- **NLP Integration**: Uses LangChain and FAISS for text retrieval and natural language processing.

## Setup Instructions

### Prerequisites
Ensure the following are installed:
- Python 3.9 or higher
- A virtual environment tool (e.g., `venv` or `conda`)
- SQLite (pre-installed with Python) or any database of your choice

### 1. Clone the Repository
```
git clone <repository_url>
cd <repository_directory>
```

### 2. Set Up the Virtual Environment
```
conda create -n env
conda activate env
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following:
```env
GEMINI_API_KEY=<Your_Google_Generative_AI_API_Key>
```

### 5. Run the Application
```
uvicorn main:app --reload
```

### 5. Run the Tests
```
pytest unit_testcase.py
```

The application will be available at `http://127.0.0.1:8000`.

**Deployed Link** : `https://smartpdf-1.onrender.com/`

## API Documentation

visit `http://127.0.0.1:8000/docs` for checking FastAPI documentation
**Documentation Link** : `https://drive.google.com/file/d/1TW846HV-Oa-RwluhbaTuHK7eC1p3jsBZ/view?usp=sharing`

### 1. **PDF Upload**
- **Endpoint**: `POST /upload/`
- **Description**: Upload a PDF document for text extraction and storage.
- **Request**:
  - `Content-Type`: `multipart/form-data`
  - **Parameters**: 
    - `file`: PDF file
- **Response**:
  - **Success**: 
    ```json
    {
      "message": "File uploaded successfully",
      "id": "unique_document_id"
    }
    ```
  - **Error**:
    ```json
    {
      "detail": "File must be a PDF"
    }
    ```

### 2. **Health Check**
- **Endpoint**: `GET /health`
- **Description**: Check the status of the backend service.
- **Response**:
  - **Success**: 
    ```json
    {
      "status": "ok"
    }

### 3. **Retrieve Stored PDFs**
- **Endpoint**: `GET /pdfs/`
- **Description**: Fetch metadata of all uploaded PDFs.
- **Response**:
  - **Success**: 
    ```json
    {
      [
         "id": "unique_document_id",
         "filename": "example.pdf",
         "upload_date": "2024-12-05"
      ]
    }

### 4. **Real-Time Q&A**
- **Endpoint**: `WS /ws/qa/`
- **Description**: Connect via WebSocket to ask questions about a specific PDF.
- **Request**:
  ```json
    {
      "pdf_id": "unique_document_id",
      "question": "What is the main topic of the document?"
    }
    ```
- **Response**:
  - **Success**: 
    ```json
    {
      "answer": "The document discusses XYZ."
    }
    ```
  - **Error**:
    ```json
    {
      "error": "Document not found."
    }
    ```

## Rate Limiting ##

The service enforces rate limiting to control excessive requests and ensure fair usage:

- **Limit** : Maximum 5 requests per minute per client.
- **Scope** : Applied to both REST API endpoints and WebSocket connections.
- **Response** : Clients exceeding the limit receive:
      - **REST API** : HTTP 429 error with `Rate limit exceeded. Try again later`.
      - **WebSocket** : JSON message with `{"error": "Rate limit exceeded. Try again later."}`

## Architectural Overview ##

### 1. Core Components ###
#### Frontend WebSocket Integration ####
The frontend will establish a WebSocket connection with the backend to enable real-time question-answering functionality. Users will send the pdf_id and their questions through this connection and receive responses dynamically without reloading the page.

#### Backend ####
- **FastAPI**: Handles REST API and WebSocket endpoints for uploading PDFs and real-time Q&A.
- **Retrieval-Augmented Generation (RAG)**: RAG combines document retrieval with generative models to ensure responses are accurate, context-aware, and derived directly from the uploaded PDF content.
- **LangChain and FAISS**: Powers NLP-based question answering and efficient text retrieval.
- **PyPDF** :  To extract text content from uploaded PDF files.
- **SQLite Database**: To store document metadata and text content.
- **Local File Storage** : To save uploaded PDFs.
- **Rate Limiting**: Prevents abuse by limiting client requests.
- **Pytest**: Ensures backend reliability with automated test cases

### 2. Data Flow ###
1. **PDF Upload**: 
- Users upload PDFs via the POST /upload/ endpoint.
- Extracts text content using PyPDF2.
- Stores the text and metadata (pdf_id, filename, upload date) in the SQLite database.
- Returns a unique pdf_id to the user.
2. **Real-Time Q&A**: 
- Users connect to the WebSocket endpoint /ws/qa/ with a pdf_id and a question.
- Backend retrieves the stored text content for the given pdf_id from the SQLite database.
- Text is split into chunks using LangChain's RecursiveCharacterTextSplitter.
- FAISS indexes these chunks for efficient search and retrieval.
**LangChain LLM**:
- Generates an answer by combining retrieved text chunks with the question.
- A prompt template ensures that the response is concise and context-aware.
- Backend sends the generated answer to the user in real time.
3. **Testing and Quality Assurance**: 
**Pytest**
- Automated test cases verify backend functionality, including file uploads, database queries, rate limiting, and WebSocket communication.
**Test Suite**:
- Includes functional tests for endpoints (/upload/, /health, /get_all_pdfs/) and integration tests for WebSocket Q&A.

<p align="center">
  <img src="/assets/dataflow.png" alt="Folder Structure" />
</p>

### 3. Folder Structure ###

<p align="center">
  <img src="/assets/folder.png" alt="Folder Structure" />
</p>