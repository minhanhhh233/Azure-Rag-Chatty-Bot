import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import openai
from dotenv import load_dotenv
import os
import json
from llama_index import GPTSimpleVectorIndex, LLMPredictor, Document, StringIterableReader
from langchain.llms import OpenAI
from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
from controllers.blobFunctions import read_file, upload_string, read_index_file, is_file_exist

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def main(newBlob: func.InputStream, outRMessages):
    connection_string = "..."
    container_name = "container1"
    
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    INDEX_FILE = "index.json"
    llm = LLMPredictor(llm=OpenAI(temperature=0, model_name="gpt-3.5-turbo"))

    # Read the pdf data
    file_name = newBlob.name.split("/")[1]
    logging.info('Python Blob trigger function processed %s', file_name)
    
    if file_name != "index.json":
        # Initialize the connection to Azure
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

        # Retrieve existing metadata
        blob_metadata = blob_client.get_blob_properties().metadata

        if blob_metadata == {}:
            pdf_reader = read_file(file_name, connection_string, container_name)        
            documents = StringIterableReader().load_data(texts=[pdf_reader])
            
            text_splitter = TokenTextSplitter(separator=" ", chunk_size=2056, chunk_overlap=20)
            text_chunks = text_splitter.split_text(documents[0].text)
            doc_chunks = []
            number_of_chunks=0
            
            for i, text in enumerate(text_chunks):
                doc = Document(text, doc_id=f"{file_name}_{i}")
                doc_chunks.append(doc)
                number_of_chunks = i

            more_blob_metadata = {'number_of_chunks': str(number_of_chunks)}
            blob_metadata.update(more_blob_metadata)
        
            # Set metadata on the blob
            blob_client.set_blob_metadata(metadata=blob_metadata)            
            
            if not is_file_exist(connection_string, container_name, "index.json"):
                index = GPTSimpleVectorIndex(doc_chunks, chunk_size_limit=256, llm_predictor=llm)
                
            else:
                # Read current index_file content in Blob Storage
                index_string = read_index_file(connection_string, container_name)
                index = GPTSimpleVectorIndex.load_from_string(index_string)            
            
                for doc_chunk in doc_chunks:
                    index.insert(doc_chunk)

            index_Json = index.save_to_string()        
            upload_string(index_Json, connection_string, container_name)

            message ='{{"value":"{0}","code":"{1}","data":"{2}"}}'.format("Index file is generated","f2", file_name)
            outRMessages.set(json.dumps({
                'target': 'Notify',
                'arguments': [message]
            }))