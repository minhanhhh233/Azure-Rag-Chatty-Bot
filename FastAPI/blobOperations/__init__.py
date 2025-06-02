import azure.functions as func
from app import app  # Main API application
from fastapi import UploadFile, File
from app.controllers.blobFunctions import delete_file, list_files, upload_file

connection_string = "..."
container_name = "container1"

@app.delete("/delete_file/{filename}")
async def delete_file_method(filename: str):
    return delete_file(filename, connection_string, container_name)

@app.post("/upload")
async def upload_files_method(uploaded_file: UploadFile = File(...)):
    contents = await uploaded_file.read()
    return upload_file(contents,connection_string, container_name,uploaded_file.filename)

@app.get("/list_files")
async def list_files_method():
    return list_files(connection_string, container_name)

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Each request is redirected to the ASGI handler."""
    return await func.AsgiMiddleware(app).handle_async(req, context)