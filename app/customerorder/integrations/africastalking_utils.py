import xml.etree.ElementTree as ET
import requests
from django.conf import settings
from typing import Dict, Any

def _send_request(data: Dict[str, Any]) -> str:
    """
    Send an HTTP POST request to Africa's Talking API.

    Args:
        data (dict): The data payload to send in the POST request.

    Returns:
        str: The raw response text from the API.
    """
    url = "https://api.sandbox.africastalking.com/version1/messaging"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apiKey": settings.AFRICASTALKING_API_KEY
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()  # Raises an error for any HTTP errors
    return response.text

def send_sms_alert(customer_name: str, customer_phone: str, order_item: str, order_amount: float, order_number: str) -> Dict[str, Any]:
    """
    Sends an SMS alert to the customer when an order is placed.

    Args:
        customer_name (str): The name of the customer.
        customer_phone (str): The phone number of the customer.
        order_item (str): Description of the ordered item.
        order_amount (float): The amount of the order.
        order_number (str): Unique identifier for the order.

    Returns:
        dict: Contains the message status and cost of the SMS.

    Raises:
        Exception: If there is an error in sending the SMS or parsing the response.
    """
    message = f"Dear {customer_name}, your order #{order_number} for {order_item} amounting to {order_amount} has been received."
    data = {
        "username": settings.AFRICASTALKING_USERNAME,
        "to": customer_phone,
        "message": message,
        "from": "2409"
    }

    try:
        response_text = _send_request(data)
        root = ET.fromstring(response_text)

        # Extract the status and cost from the XML response
        status = root.find('.//Recipient//status').text
        cost = root.find('.//Recipient//cost').text

        return {'message': 'Sent', 'status': status, 'cost': cost}

    except ET.ParseError:
        raise Exception("Failed to parse the response from Africa's Talking API.")
    except requests.RequestException as e:
        raise Exception(f"HTTP request error: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error sending SMS: {e}")
