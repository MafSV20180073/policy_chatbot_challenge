import os
import requests

from dotenv import load_dotenv


load_dotenv()
if os.getenv("USE_NGROK_URL", "false").lower() == "true":
    ORDERS_MOCK_API_URL = os.getenv("ORDERS_MOCK_API_NGROK_URL")
else:
    ORDERS_MOCK_API_URL = os.getenv("ORDERS_MOCK_API_DOCKER_URL")


def cancel_order(tracking_number: int):
    print("\n\nI reached cancel_order_tool, yey!!!")
    response = requests.post(
        f"{ORDERS_MOCK_API_URL}cancel_order",
        json={"tracking_number": tracking_number}
    )
    print("I have a response now. Returning!!")
    try:
        return response.json()
    except:
        return {"status": response.status_code, "message": response.text}


def track_order(tracking_number: int):
    print("\n\nI reached track_order_tool, yey!!!")
    response = requests.get(
        f"{ORDERS_MOCK_API_URL}track_order",
        params={"tracking_number": tracking_number}
    )
    print("I have a response now. Returning.")
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
                        "description": "The tracking number of the order to cancel."
                    }
                },
                "required": ["tracking_number"],
            }
        }
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
                        "description": "The tracking number of the order to be tracked."
                    }
                },
                "required": ["tracking_number"],
            }
        }
    }
]


TOOL_MAPPING = {
    "cancel_order": cancel_order,
    "track_order": track_order
}
