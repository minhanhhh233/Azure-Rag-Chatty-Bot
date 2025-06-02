import unittest
import os
import json
from unittest.mock import MagicMock, patch
from azure.storage.blob import BlobServiceClient
import azure.functions as func

from generateIndexFile.__init__ import main as main

class TestMainFunction(unittest.TestCase):
    def test_main(self):
        connection_string = "..."
        container_name = "container1"
        # Create a mock output binding
        outRMessages_mock = MagicMock()
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)


        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container=container_name)
        newBlob_mock = MagicMock(spec=func.InputStream)
        with open("test_file.pdf", mode="rb") as data:
            blob_client = container_client.upload_blob(name="test_file.pdf",data=data, overwrite=True)
            newBlob_mock.name = 'container1/test_file.pdf'
            newBlob_mock.read.return_value = data
        
        outRMessages = MagicMock()
        main(newBlob_mock, outRMessages)

        #outRMessages.set.assert_called_once()
        args, kwargs = outRMessages.set.call_args

        outRMessages_dict = json.loads(args[0])
        assert outRMessages_dict["target"] == "Notify"
        
        json_argument = json.loads(outRMessages_dict["arguments"][0])
        assert json_argument["value"] == "Index file is generated"
        assert json_argument["code"] == "f2"
        assert json_argument["data"] == "test_file.pdf"

        # Assert that the index.json file has been generated
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob="index.json")
        blob_data = blob_client.download_blob().readall()
        self.assertTrue(blob_data)