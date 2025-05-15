# main.py
from fastapi import FastAPI
from api.customer_api import router as customer_router
from api.app import app as webhook_app
from workers.stripe_worker import StripeWorker
from workers.inward_sync_worker import InwardSyncWorker
# from services.inward_sync_service import InwardSyncService # for polling
from services.stripe_service import StripeService
from services.kafka_service import KafkaService
import uvicorn
import threading
import signal
import sys
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    stripe_worker.start()
    inward_sync_worker.start()
    
    yield  # This yields control back to FastAPI
    
    # Shutdown logic
    stripe_worker.stop()
    inward_sync_worker.stop()

app = FastAPI(title="Customer Sync Integration")

# Include routers
app.include_router(customer_router, prefix="/api")
app.mount("/webhooks", webhook_app)

# Workers
stripe_worker = StripeWorker()
inward_sync_worker = InwardSyncWorker()

# Services for polling (if not using webhooks)
stripe_service = StripeService()
kafka_service = KafkaService()

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("Shutting down...")
    stripe_worker.stop()
    inward_sync_worker.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)