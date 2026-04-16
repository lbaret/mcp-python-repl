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

@app.get("/files")
async def list_files():
    """
    List all PDF files in the data directory.

    This endpoint scans the local data directory for PDF files and returns a list of their filenames.

    Returns:
        dict: A dictionary containing a list of PDF filenames.
    """
    data_dir = "/app/data"

    if not os.path.exists(data_dir):
        return {"error": f"Directory '{data_dir}' does not exist."}

    try:
        pdf_files = [
            f
            for f in os.listdir(data_dir)
            if os.path.isfile(os.path.join(data_dir, f)) and f.lower().endswith(".pdf")
        ]

        return {"files": pdf_files}

    except Exception as e:
        return {"error": f"Error listing files: {str(e)}"}


@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """
    Delete a PDF file from the data directory.

    This endpoint deletes a specific PDF file from the local data directory.

    Args:
        filename (str): The name of the file to delete.

    Returns:
        dict: A dictionary containing a success message or an error message.
    """
    filepath = f"/app/data/{filename}"

    if not os.path.exists(filepath):
        return {"error": f"File {filename} does not exist."}

    try:
        os.remove(filepath)
        return {"info": f"File {filename} deleted successfully."}
    except Exception as e:
        return {"error": f"Error deleting file: {str(e)}"}


@app.get("/status")
async def status():
    """Simple checking route."""
    return {"status": "Online", "mcp_endpoint": "/mcp"}

app.mount("/mcp", mcp.sse_app())
