# api/app.py
from fastapi import FastAPI, Request, Depends
import stripe
from services.kafka_service import KafkaService
from config import STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET

app = FastAPI()
kafka_service = KafkaService()
inward_topic = 'customer_inward_sync'

stripe.api_key = STRIPE_API_KEY
webhook_secret = STRIPE_WEBHOOK_SECRET

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return {"error": "Invalid payload"}
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return {"error": "Invalid signature"}
    
    # Handle the event
    if event['type'] == 'customer.created' or event['type'] == 'customer.updated':
        customer = event['data']['object']
        message = {
            'event_type': 'stripe_customer_updated',
            'stripe_customer': {
                'id': customer['id'],
                'name': customer.get('name'),
                'email': customer.get('email')
            }
        }
        kafka_service.send_message(inward_topic, message)
    
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)