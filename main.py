# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request, Depends
from api.customer_api import router as customer_router, get_customers, get_customer_integration_status
from api.app import app as webhook_app
from workers.stripe_worker import StripeWorker
from workers.inward_sync_worker import InwardSyncWorker
# from services.inward_sync_service import InwardSyncService # for polling
from services.stripe_service import StripeService
from services.kafka_service import KafkaService
import uvicorn
import signal
import sys
from contextlib import asynccontextmanager


# Workers
stripe_worker = StripeWorker()
inward_sync_worker = InwardSyncWorker()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    stripe_worker.start()
    inward_sync_worker.start()
    
    yield  # This yields control back to FastAPI
    
    # Shutdown logic
    stripe_worker.stop()
    inward_sync_worker.stop()

app = FastAPI(title="Customer Sync Integration", lifespan=lifespan)

# UI templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(customer_router, prefix="/api")
app.mount("/webhooks", webhook_app)

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

# UI Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    import time
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "timestamp": int(time.time())  # Add timestamp for cache busting
    })

@app.get("/customers", response_class=HTMLResponse)
async def customers_page(request: Request):
    return templates.TemplateResponse("customers.html", {"request": request})

@app.get("/integrations", response_class=HTMLResponse)
async def integrations_page(request: Request):
    return templates.TemplateResponse("integrations.html", {"request": request})
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)