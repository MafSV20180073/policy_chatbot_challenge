import logging
import os

import requests
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()
if os.getenv("USE_NGROK_URL", "false").lower() == "true":
    ORDERS_MOCK_API_URL = os.getenv("ORDERS_MOCK_API_NGROK_URL")
else:
    ORDERS_MOCK_API_URL = os.getenv("ORDERS_MOCK_API_DOCKER_URL")


def cancel_order(tracking_number: int):
    """Tool that performs a POST request to cancel an order by its tracking number.

    Parameters
    ----------
    tracking_number : int
        The tracking number of the order to cancel.

    Returns
    -------
    dict
        JSON response from the API or error information.
    """
    logger.info("Calling cancel_order_tool with tracking number: %s", tracking_number)
    response = requests.post(
        f"{ORDERS_MOCK_API_URL}cancel_order", json={"tracking_number": tracking_number}
    )
    logger.info(
        "Received response from cancel_order endpoint with status code: %s",
        response.status_code,
    )
    try:
        return response.json()
    except:
        return {"status": response.status_code, "message": response.text}


def track_order(tracking_number: int):
    """Tool that performs a GET request to get the status of an order by its tracking number.

    Parameters
    ----------
    tracking_number : int
        The tracking number of the order to be tracked.

    Returns
    -------
    dict
        JSON response from the API or error information.
    """
    logger.info("Calling track_order_tool with tracking number: %s", tracking_number)
    response = requests.get(
        f"{ORDERS_MOCK_API_URL}track_order", params={"tracking_number": tracking_number}
    )
    logger.info(
        "Received response from track_order endpoint with status code: %s",
        response.status_code,
    )
    try:
        return response.json()
    except:
        return {"status": response.status_code, "message": response.text}


tools = [
    {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": "Performs a POST request on Orders API to cancel an order by passing its tracking number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tracking_number": {
                        "type": "integer",
                        "description": "The tracking number of the order to cancel.",
                    }
                },
                "required": ["tracking_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "track_order",
            "description": "Performs a GET request on Orders API to obtain the current status of an order by passing its tracking number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tracking_number": {
                        "type": "integer",
                        "description": "The tracking number of the order to be tracked.",
                    }
                },
                "required": ["tracking_number"],
            },
        },
    },
]


TOOL_MAPPING = {"cancel_order": cancel_order, "track_order": track_order}
