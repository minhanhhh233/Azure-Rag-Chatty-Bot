import io
import PyPDF2
from azure.storage.blob import BlobServiceClient
from llama_index import GPTSimpleVectorIndex
import sys


def upload_file(local_file_path: str, connection_string: str, container_name:str, blob_name: str):
    # Initialize the connection to Azure
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container=container_name)
    
    with open(local_file_path, mode="rb") as data:
        blob_client = container_client.upload_blob(name=blob_name,data=data, overwrite=True)

def upload_string(data: str, connection_string: str, container_name:str):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container=container_name)
    container_client.upload_blob(name="index.json", data=data, overwrite=True)

def delete_file(filename: str, connection_string: str, container_name:str):
    # Initialize the connection to Azure
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
    
    
    index_string = read_index_file(connection_string, container_name)  
    index = GPTSimpleVectorIndex.load_from_string(index_string)
    number_of_chunks = int(blob_client.get_blob_properties().metadata["number_of_chunks"])
    blob_client.delete_blob()
    
    return {
        "message": f"{filename} has been deleted. {number_of_chunks}",
    }

def list_files(connection_string: str, container_name:str):
    # Initialize the connection to Azure
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    container_client = blob_service_client.get_container_client(container=container_name)
    blob_list = container_client.list_blobs()
    files = [blob.name for blob in blob_list if blob.name != "index.json"]
    return {
        "files": files,
    }

def read_file(blob_name: str, connection_string: str, container_name:str):
    
    sys.stdout.reconfigure(encoding='utf-8')
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    download_stream = blob_client.download_blob()
    stream = io.BytesIO(download_stream.readall())
    pdf_reader = PyPDF2.PdfReader(stream)
    num_pages = len(pdf_reader.pages)
    
    text = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
        text += "/n"

    return text
   
def read_index_file(connection_string: str, container_name:str):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    blob_client = blob_service_client.get_blob_client(container=container_name, blob="index.json")
    blob_contents = blob_client.download_blob().content_as_text()
    return blob_contents

def is_file_exist(connection_string: str, container_name:str, blob_name: str):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container=container_name)
    blob_list = container_client.list_blobs()
    files = [blob.name for blob in blob_list]

    if blob_name in files:
        return True
    else:
        return False