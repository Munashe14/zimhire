from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Tuple
from app.models.client import Client, ClientType, AccountStatus
from app.schemas.client import ClientCreate, ClientUpdate


class ClientService:
    def __init__(self, db: Session):
        self.db = db

    def create_client(self, client_data: ClientCreate) -> Client:
        """Create a new client."""
        # Check for duplicate phone number
        existing = self.db.query(Client).filter(
            Client.phone_number == client_data.phone_number
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already exists",
            )
        
        # Check for duplicate email if provided
        if client_data.email:
            existing_email = self.db.query(Client).filter(
                Client.email == client_data.email
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists",
                )
        
        client = Client(**client_data.model_dump())
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def get_client(self, client_id: int) -> Client:
        """Get a client by ID."""
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )
        return client

    def list_clients(
        self,
        skip: int = 0,
        limit: int = 100,
        client_type: ClientType = None,
        account_status: AccountStatus = None,
        search: str = None
    ) -> Tuple[list[Client], int]:
        """List clients with optional filters."""
        query = self.db.query(Client)
        
        if client_type:
            query = query.filter(Client.client_type == client_type)
        if account_status:
            query = query.filter(Client.account_status == account_status)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Client.full_name.ilike(search_pattern)) |
                (Client.business_name.ilike(search_pattern)) |
                (Client.phone_number.ilike(search_pattern)) |
                (Client.email.ilike(search_pattern))
            )
        
        total = query.count()
        clients = query.offset(skip).limit(limit).all()
        return clients, total

    def update_client(self, client_id: int, client_data: ClientUpdate) -> Client:
        """Update a client."""
        client = self.get_client(client_id)
        
        # Check phone number uniqueness if updating
        if client_data.phone_number and client_data.phone_number != client.phone_number:
            existing = self.db.query(Client).filter(
                Client.phone_number == client_data.phone_number
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already exists",
                )
        
        # Check email uniqueness if updating
        if client_data.email and client_data.email != client.email:
            existing_email = self.db.query(Client).filter(
                Client.email == client_data.email
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists",
                )
        
        update_data = client_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(client, field, value)
        
        self.db.commit()
        self.db.refresh(client)
        return client
