import paypalrestsdk
import os
import requests
import uuid

 # Set up the PayPal REST API client
paypalrestsdk.configure({
    "mode": "sandbox", # Change to "live" for production
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})

def get_paypal_payment_link(amount: int):
  # Define the payment details
  payment = paypalrestsdk.Payment({
      "intent": "sale",
      "payer": {
          "payment_method": "paypal"
      },
      "transactions": [{
          "amount": {
              "total": "10.00",
              "currency": "USD"
          },
          "description": "Payment for your order"
      }],
      "payment_options": {
        "allowed_payment_method": "IMMEDIATE_PAY"
      },
      "redirect_urls": {
          "return_url": "http://example.com/success",
          "cancel_url": "http://example.com/cancel"
      }
  })
  # Create the payment
  if payment.create():
    print(payment.links)
    # Get the payment approval URL
    for link in payment.links:
        if link.method == "REDIRECT":
            approval_url = str(link.href)
            print("Payment approval URL:", approval_url)
            return approval_url
  else:
      print("Error:", payment.error)
  

def create_paypal_invoice(amount, language="English"):
  headers = {
      'Authorization': 'Bearer zekwhYgsYYI0zDg0p_Nf5v78VelCfYR0',
      'Content-Type': 'application/json',
      'Prefer': 'return=representation',
  }

  # generate random uuid
  invoice_id = uuid.uuid4()

  payload = {
    "detail": {
      "currency_code": "USD"
    },
    "items": [
      {
        "name": "Yoga Mat",
        "description": "Elastic mat to practice yoga.",
        "quantity": "1",
        "unit_amount": {
          "currency_code": "USD",
          "value": "10.00"
        },
      },
    ]
  }


  response = requests.post('https://api-m.sandbox.paypal.com/v2/invoicing/invoices', headers=headers, json=payload)
  url = response['detail']['metadata']['recipient_view_url']
  print(url)

