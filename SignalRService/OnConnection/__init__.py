import logging
import json

import azure.functions as func


def main (invocation) -> None:
    invocation_json = json.loads(invocation)

    #not sure where 'ConnectionId' comes from: https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-signalr-service-trigger?tabs=in-process&pivots=programming-language-python
    logging.info(f"{invocation_json['ConnectionId']} has connected")