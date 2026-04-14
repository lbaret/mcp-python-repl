import os
import shutil

from fastapi import FastAPI, UploadFile

from src.mcp_repl.server import mcp

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile):
    """
    Upload a PDF file to the server.
    
    This endpoint accepts an uploaded file, verifies that it is a PDF by checking
    its extension or MIME type, and saves it to the local data directory.
    
    Args:
        file (UploadFile): The file being uploaded.
        
    Returns:
        dict: A dictionary containing the filename and a success message,
              or an error message if the file is not a PDF or already exists.
    """
    if not file.filename.lower().endswith(".pdf") and file.content_type != "application/pdf":
        return {"error": "Only PDF files are allowed"}

    filepath = f"/app/data/{file.filename}"

    if os.path.exists(filepath):
        return {"error": f"File {file.filename} already exists"}
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {
        "filename": file.filename,
        "info": f"File {file.filename} uploaded successfully.",
    }

@app.get("/status")
async def status():
    """Simple checking route."""
    return {"status": "Online", "mcp_endpoint": "/mcp"}

app.mount("/mcp", mcp.sse_app())
