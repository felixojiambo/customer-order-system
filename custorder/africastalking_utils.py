import xml.etree.ElementTree as ET
import requests
from django.conf import settings


def _send_request(data):
    """
    Send an HTTP POST request to Africa's Talking API.
    """
    url = "https://api.sandbox.africastalking.com/version1/messaging"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apiKey": settings.AFRICASTALKING_API_KEY
    }
    response = requests.post(url, headers=headers, data=data)
    return response.text


def send_sms_alert(customer_name, customer_phone, order_item, order_amount, order_number):
    """
    Sends an SMS alert to the customer when an order is placed.
    """
    message = f"Dear {customer_name}, your order #{order_number} for {order_item} amounting to {order_amount} has been received."

    data = {
        "username": settings.AFRICASTALKING_USERNAME,
        "to": customer_phone,
        "message": message,
        "from": 2409
    }

    try:
        response_text = _send_request(data)
        root = ET.fromstring(response_text)
        status = root.find('.//Recipient//status').text
        cost = root.find('.//Recipient//cost').text

        return {'message': 'Sent', 'status': status, 'cost': cost}
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return {'status': 'Error', 'message': str(e)}
