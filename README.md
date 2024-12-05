# PDF QA Backend Service

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
```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Set Up the Virtual Environment
```bash
conda create -n env
conda activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following:
```env
GEMINI_API_KEY=<Your_Google_Generative_AI_API_Key>
```

### 5. Run the Application
```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:8000`.

## API Documentation

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
      - ***REST API*** : HTTP 429 error with `Rate limit exceeded. Try again later`.
      - ***WebSocket*** : JSON message with `{"error": "Rate limit exceeded. Try again later."}`

## Architectural Overview ##

### 1. Core Components ###
- **FastAPI**: For building RESTful and WebSocket APIs.
- **LangChain**: For NLP capabilities, using FAISS as a vector store.
- **SQLite**: To store document metadata and text content.
- **Local File Storage** : To save uploaded PDFs.

### 2. Data Flow ###
1. **PDF Upload**: 
- Users upload PDFs via the POST /upload/ endpoint.
- Text is extracted and stored in the SQLite database.
2. **Real-Time Q&A**: 
- Users connect via WebSocket and provide a pdf_id and a question.
- Extracted text is split into chunks, indexed with FAISS, and used for NLP-based question answering.

<!-- ### 3. Folder Structure ###

<p align="center">
  <img src="/assets/er.jpg" alt="Folder Structure" />
</p> -->