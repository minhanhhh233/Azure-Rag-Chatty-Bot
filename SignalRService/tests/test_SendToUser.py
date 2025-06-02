import json
from unittest.mock import MagicMock, patch
import azure.functions as func
from SendToUser.__init__ import main as main
import unittest
import openai
from dotenv import load_dotenv
import os


class TestFunction(unittest.TestCase):
    
    def test_main(self):
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")

        invocation = '{"Arguments": ["{\\"id\\":\\"1\\",\\"value\\":\\"What is this file?\\",\\"chatID\\":\\"test chatID\\"}"], "ConnectionId": "test connection id", "UserId": "test user id"}'
        outRMessages = MagicMock()

        main(invocation, outRMessages)

        outRMessages.set.assert_called_once()
        args, kwargs = outRMessages.set.call_args

        outRMessages_dict = json.loads(args[0])
        assert outRMessages_dict["userId"] == "test user id"
        assert outRMessages_dict["target"] == "Send"

        json_argument = json.loads(outRMessages_dict["arguments"][0])
        assert json_argument["id"] == "1"
        assert isinstance( json_argument["value"], str)
        print(json_argument["value"])
        assert json_argument["chatID"] == "test chatID"
        assert json_argument["isUser"] == True