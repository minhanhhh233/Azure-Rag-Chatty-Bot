import azure.functions as func
import logging
import json
from llama_index import GPTSimpleVectorIndex, LLMPredictor 
from langchain.llms import OpenAI 
from controllers.blobFunctions import read_index_file, is_file_exist

def main(invocation, outRMessages) -> func.HttpResponse:
    invocation_json = json.loads(invocation)
    logging.info("Loading index from file")
    logging.info("Receive {0} from {1}".format(invocation_json['Arguments'][0], invocation_json['ConnectionId']))
    INDEX_FILE = "./index.json"
    # Using GPT-4 
    #llm = LLMPredictor(llm=OpenAI(temperature=0, model_name="text-curie-001"))
    llm = LLMPredictor(llm=OpenAI(temperature=0, model_name="gpt-3.5-turbo"))
    message = json.loads(invocation_json['Arguments'][0])
    query = message["value"]
    id = message["id"]
    chatID = message["chatID"]
    connection_string = "..."
    container_name = "container1"

    if is_file_exist(connection_string, container_name, "index.json"):
        index_string = read_index_file(connection_string, container_name)  
        index = GPTSimpleVectorIndex.load_from_string(index_string)
    
        results = index.query(query, similarity_top_k=3)
        print("The query is", message["value"])
        reply_split = '\\n'.join(results.response.strip().split("\n"))
        #reply_split = '\"'.join(results.response.strip().split('"'))

        
        reply_json='{{"id":"{0}","value":"{1}","chatID":"{2}","isUser":true}}'.format(id,reply_split,chatID)
        #json_data = json.loads(reply_json)
        #reply_split = '\\\"'.join(results.response.strip().split('"'))
        #reply_json='{{"id":"{0}","value":"{1}","chatID":"{2}","isUser":true}}'.format(id,reply_split[0]+reply_split[1]+reply_split[2],chatID)

        #value = json_data["value"]
        #reply_json='{{"id":"{0}","value":"{1}","chatID":"{2}","isUser":true}}'.format(id,value,chatID)
        print("The reply is",reply_json)
        outRMessages.set(json.dumps({
            #message will only be sent to this user ID
            'userId': invocation_json["UserId"],
            'target': 'Send',
            'arguments': [reply_json]
        }))
    else:
        reply_json='{{"value":"{0}","code":"{1}","data":"{2}"}}'.format("Please upload a pdf file first.", "f1","You haven't upload any pdf file.")

        outRMessages.set(json.dumps({
            #message will only be sent to this user ID
            'target': 'Notify',
            'arguments': [reply_json]
        }))
    