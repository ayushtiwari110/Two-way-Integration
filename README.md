# 🔄 Customer Sync Hub 🔄

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95.1-green?logo=fastapi)
![Kafka](https://img.shields.io/badge/Kafka-3.4-red?logo=apache-kafka)
![Stripe](https://img.shields.io/badge/Stripe%20API-Latest-blueviolet?logo=stripe)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A real-time two-way customer catalog integration system between your application and external services like Stripe.

<p align="center">
  <img src="https://via.placeholder.com/800x400?text=Customer+Sync+Hub+Architecture" alt="Architecture Diagram"/>
</p>

## 📑 Table of Contents

- Overview
- Features
- System Architecture
- Tech Stack
- Project Structure
- Database Design
- Event Flow
- Screenshots
- API Documentation
- Installation & Setup
- Extending the System
- Future Improvements
- License

## 🌐 Overview

Customer Sync Hub is a robust system that maintains real-time synchronization between your local customer database and external services (currently Stripe). The system is designed with extensibility in mind, allowing easy addition of new integrations and support for other catalog types beyond customers.

The platform provides a clean UI for managing customers and monitoring integration status. Behind the scenes, it uses a message queue architecture for reliable, asynchronous processing of sync operations.

## ✨ Features

### 📊 Dashboard

- Real-time statistics on customer sync status
- Visual charts showing synced vs. unsynced customers
- Recent customer activity feed
- One-click refresh for latest metrics

### 👥 Customer Management

- Create, view, update and delete customers
- Automatic sync of customer data to external services
- Visual indicators for sync status
- Form validation for customer data

### 🔌 External Integrations

- Bidirectional sync with Stripe (currently implemented)
- Webhook support for real-time updates from Stripe
- Integration status monitoring
- Designed for adding more integrations (e.g., Salesforce)

### 🔄 Sync Engine

- Kafka-based message queue for reliable event processing
- Event-driven architecture for handling sync operations
- Automatic retry logic for failed operations
- Separate inbound and outbound processing paths

### 🧩 Extensibility

- Polymorphic database design for supporting multiple catalog types
- Service abstraction layer for consistent integration interfaces
- Repository pattern for clean data access
- Event-driven architecture for loose coupling

## 🏗️ System Architecture

The system follows a modern, event-driven microservices architecture:

1. **Web Layer**: FastAPI-powered web server handling HTTP requests
2. **API Layer**: RESTful endpoints for customer operations
3. **Service Layer**: Core business logic for sync operations
4. **Repository Layer**: Data access using repository pattern
5. **Message Queue**: Kafka for reliable, asynchronous processing
6. **Workers**: Background processes handling sync operations
7. **External Services**: Integration with Stripe and other services

<p align="center">
  <img src="https://via.placeholder.com/800x500?text=System+Architecture+Diagram" alt="System Architecture"/>
</p>

## 💻 Tech Stack

### Backend
- **Python**: Primary programming language
- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings management
- **Stripe API**: External customer management system

### Frontend
- **HTML/CSS/JavaScript**: Core web technologies
- **Bootstrap 5**: UI framework for responsive design
- **Chart.js**: Interactive data visualization
- **FontAwesome**: Icon library

### Infrastructure
- **SQLite**: Database (easily replaceable with PostgreSQL/MySQL)
- **Kafka**: Message broker for event handling
- **Docker**: Containerization for Kafka and Zookeeper
- **Uvicorn**: ASGI server for FastAPI

## 📁 Project Structure

```
customer-sync-hub/
├── api/                     # API endpoints
│   ├── app.py               # Webhook API
│   └── customer_api.py      # Customer management API
├── database/                # Database models and repositories
│   ├── models.py            # SQLAlchemy ORM models
│   ├── repositories/        # Repository pattern implementations
│       ├── catalogue_repository.py    # Base repository
│       ├── customer_repository.py     # Customer repository
│       └── invoice_repository.py      # (Example extension)
├── services/                # Business logic
│   ├── integration_service.py  # Abstract integration service
│   ├── stripe_service.py    # Stripe implementation
│   ├── kafka_service.py     # Message queue service
│   └── outward_sync_service.py  # Service for outbound sync
├── static/                  # Frontend static assets
│   ├── dashboard.js         # Dashboard functionality
│   ├── customers.js         # Customer page functionality
│   └── integrations.js      # Integrations page functionality
├── templates/               # HTML templates
│   ├── dashboard.html       # Dashboard page
│   ├── customers.html       # Customer management page
│   └── integrations.html    # Integration status page
├── workers/                 # Background workers
│   ├── stripe_worker.py     # Processes outward sync events
│   └── inward_sync_worker.py  # Processes inward sync events
├── config.py                # Configuration settings
├── main.py                  # Application entry point
├── docker-compose.yml       # Docker configuration
└── requirements.txt         # Python dependencies
```

## 🗃️ Database Design

The system uses a polymorphic database design to support multiple catalog types:

```
┌────────────────┐       ┌─────────────────┐
│  catalog_items │       │    customers    │
├────────────────┤       ├─────────────────┤
│ id (PK)        │◄──────┤ id (PK, FK)     │
│ catalog_type   │       │ name            │
│ created_at     │       │ email (unique)  │
│ updated_at     │       └─────────────────┘
└────────────────┘               ▲
        ▲                        │
        │                        │
        │                        │
        │       ┌─────────────────────────┐
        └───────┤  catalog_integrations   │
                ├─────────────────────────┤
                │ id (PK)                 │
                │ catalog_item_id (FK)    │
                │ integration_type        │
                │ integration_id          │
                │ created_at              │
                └─────────────────────────┘
```

- **Polymorphic Inheritance**: `catalog_items` is the base table with `catalog_type` determining the entity type
- **Integration Mapping**: `catalog_integrations` stores mappings between local entities and external IDs
- **Extensibility**: The design allows adding new catalog types (e.g., invoices) without major schema changes

## 🔄 Event Flow

### Outward Sync Flow (Local → Stripe)
1. User creates/updates/deletes a customer in the web UI
2. API endpoint processes the request and updates local database
3. API sends an event to the Kafka `customer_outward_sync` topic
4. `StripeWorker` consumes the event from Kafka
5. `StripeWorker` calls appropriate `StripeService` method
6. `StripeService` makes API calls to Stripe
7. `StripeWorker` updates the integration record in the local database

### Inward Sync Flow (Stripe → Local)
1. Changes occur in Stripe (via Stripe Dashboard or API)
2. Stripe sends webhook event to `/webhooks/stripe` endpoint
3. Webhook handler sends event to Kafka `customer_inward_sync` topic
4. `InwardSyncWorker` consumes the event from Kafka
5. `InwardSyncWorker` processes the event based on its type:
   - For `customer.created`: Creates new customer and integration record
   - For `customer.updated`: Updates existing customer details
   - For `customer.deleted`: Removes integration record (doesn't deletes customer, so the customer becomes unsynced with stripe)

## 📸 Web Interface

### Dashboard
<p align="center">
  <img src="https://via.placeholder.com/800x400?text=Dashboard+Screenshot" alt="Dashboard"/>
</p>

The dashboard provides a comprehensive overview of your customer sync status with:
- Key metrics (total customers, synced customers, pending sync)
- Pie chart visualizing sync status distribution
- Recent customer activity with sync status indicators
- Quick action buttons for managing customers and viewing integrations

### Customer Management
<p align="center">
  <img src="https://via.placeholder.com/800x400?text=Customer+Management+Screenshot" alt="Customer Management"/>
</p>

The customer management page allows you to:
- View all customers in a clean, sortable table
- See sync status for each customer at a glance
- Add new customers with a simple modal form
- Edit existing customer details
- Delete customers with confirmation
- Refresh the customer list to see latest sync status

### Integrations View
<p align="center">
  <img src="https://via.placeholder.com/800x400?text=Integrations+Screenshot" alt="Integrations"/>
</p>

The integrations page shows:
- All integration records between local customers and external systems
- Customer details for each integration
- Integration type (e.g., Stripe)
- External IDs for reference
- Quick refresh functionality to see latest integration status

## 📚 API Documentation

The system provides a comprehensive REST API with OpenAPI/Swagger documentation:

### Customer Endpoints
- `GET /api/customers` - List all customers
- `GET /api/customers/{customer_id}` - Get customer details
- `POST /api/customers` - Create a new customer
- `PUT /api/customers/{customer_id}` - Update a customer
- `DELETE /api/customers/{customer_id}` - Delete a customer
- `GET /api/customers/{customer_id}/integration-status` - Check integration status

### Integration Endpoints
- `GET /api/integrations` - List all integration records

### Webhook Endpoints
- `POST /webhooks/stripe` - Receive events from Stripe

Access the interactive API documentation at `/docs` when running the application.

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- Docker and Docker Compose (for Kafka)
- Stripe account with API keys

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/customer-sync-hub.git
   cd customer-sync-hub
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Stripe API keys and other settings
   ```

   **Set up config.py** 
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()
   DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./customers.db")
   STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
   STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
   KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BROKER", "localhost:29092")
   ```  

5. **Start Kafka**
   ```bash
   docker-compose up -d
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

7. **Access the application**
   - Web UI: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

8. **Set up Stripe webhook forwarding**
   ```bash
   # Using ngrok (install separately if needed)
   ngrok http 8000
   
   # Configure the webhook URL in your Stripe Dashboard:
   # https://<your-ngrok-url>/webhooks/stripe
   # with events: customer.created, customer.updated, customer.deleted
   ```

## 🧩 Extending the System

### Adding Salesforce Integration

To add Salesforce as an integration:

1. Create a `SalesforceService` class implementing the `CatalogIntegrationService` interface:
   ```python
   class SalesforceService(CatalogIntegrationService):
       def __init__(self):
           super().__init__('customer')
           # Salesforce authentication setup
           
       def create_item(self, name, email):
           # Implementation using Salesforce API
           
       # Implement other required methods...
   ```

2. Create a `SalesforceWorker` similar to the `StripeWorker`:
   ```python
   class SalesforceWorker:
       def __init__(self):
           # Setup similar to StripeWorker
           
       # Implement message processing methods...
   ```

3. Update existing API endpoints to support Salesforce integration type.

### Supporting Invoice Catalog

To add invoice support:

1. Uncomment and implement the `Invoice` model in models.py
2. Create an `InvoiceRepository` extending the base `CatalogRepository`
3. Add API endpoints for invoice management
4. Create service implementations for syncing invoices with external systems
5. Update workers to handle invoice events

## 🔮 Future Improvements

- **Enhanced Error Handling**: Implement more robust error handling and retry mechanisms
- **Pagination**: Add pagination for large datasets
- **Search & Filters**: Implement search and filtering options in the UI
- **User Authentication**: Add user authentication and authorization
- **Audit Logging**: Track all sync operations for auditing
- **Conflict Resolution**: Implement more sophisticated conflict resolution strategies
- **Batch Operations**: Add support for bulk create/update/delete operations
- **Testing**: Comprehensive unit and integration tests
- **Multi-tenancy**: Support for multiple organizations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<p align="center">
  Made with ❤️ by Ayush Tiwari
</p>