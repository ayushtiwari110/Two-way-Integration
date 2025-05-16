# api/customer_api.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from database.repositories.customer_repository import CustomerRepository
from services.outward_sync_service import OutwardSyncService
from database.models import Session as DBSession
from services.kafka_service import KafkaService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency
def get_customer_repo():
    db_session = DBSession()
    repo = CustomerRepository(db_session)
    try:
        yield repo
    finally:
        db_session.close()

def get_outward_sync_service():
    kafka_service = KafkaService()
    return OutwardSyncService(kafka_service)

# Models
class CustomerCreate(BaseModel):
    name: str
    email: str

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    
class IntegrationResponse(BaseModel):
    id: int
    catalog_item_id: Optional[int] = None 
    integration_type: str
    integration_id: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None

@router.post("/customers", response_model=CustomerResponse)
def create_customer(
    customer: CustomerCreate,
    repo: CustomerRepository = Depends(get_customer_repo),
    sync_service: OutwardSyncService = Depends(get_outward_sync_service)
):
    existing = repo.get_by_email(customer.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_customer = repo.create(name=customer.name, email=customer.email)
    sync_service.queue_create_event(new_customer)
    
    return CustomerResponse(
        id=new_customer.id,
        name=new_customer.name,
        email=new_customer.email
    )

@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    repo: CustomerRepository = Depends(get_customer_repo),
    sync_service: OutwardSyncService = Depends(get_outward_sync_service)
):
    updated = repo.update(customer_id, name=customer.name, email=customer.email)
    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    sync_service.queue_update_event(updated)
    
    return CustomerResponse(
        id=updated.id,
        name=updated.name,
        email=updated.email
    )

@router.delete("/customers/{customer_id}", response_model=dict)
def delete_customer(
    customer_id: int,
    repo: CustomerRepository = Depends(get_customer_repo),
    sync_service: OutwardSyncService = Depends(get_outward_sync_service)
):
    logger.info(f"DELETE request received for customer_id: {customer_id}")
    customer = repo.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    integration = repo.get_integration(catalog_id=customer_id, integration_type='stripe')
    deleted = repo.delete(customer_id)
    
    # Queue the delete event for external sync
    if deleted and integration:
        sync_service.queue_delete_event(integration.integration_id)
    
    return {"success": deleted}

@router.get("/customers", response_model=List[CustomerResponse])
def get_customers(repo: CustomerRepository = Depends(get_customer_repo)):
    customers = repo.get_all()
    return [
        CustomerResponse(
            id=customer.id,
            name=customer.name,
            email=customer.email
        )
        for customer in customers
    ]

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, repo: CustomerRepository = Depends(get_customer_repo)):
    customer = repo.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        email=customer.email
    )
    
@router.get("/customers/{customer_id}/integration-status")
def get_customer_integration_status(customer_id: int, repo: CustomerRepository = Depends(get_customer_repo)):
    customer = repo.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    integration = repo.get_integration(catalog_id=customer_id, integration_type='stripe')
    return {"has_integration": integration is not None}

@router.get("/integrations", response_model=List[IntegrationResponse])
def get_all_integrations(repo: CustomerRepository = Depends(get_customer_repo)):
    """Get all integration records with customer information"""
    integrations = repo.get_all_integrations()
    result = []
    
    for integration in integrations:
        customer = repo.get(integration.catalog_item_id)
        response = IntegrationResponse(
            id=integration.id,
            catalog_item_id=integration.catalog_item_id,
            integration_type=integration.integration_type,
            integration_id=integration.integration_id,
            customer_name=customer.name if customer else None,
            customer_email=customer.email if customer else None
        )
        result.append(response)
    
    return result