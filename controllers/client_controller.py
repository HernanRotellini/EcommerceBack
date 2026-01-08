"""Client controller with proper dependency injection."""
from typing import Optional
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from controllers.base_controller_impl import BaseControllerImpl
from schemas.client_schema import ClientSchema
from schemas.login_schema import LoginRequest, LoginResponse
from services.client_service import ClientService
from config.database import get_db


class ClientController(BaseControllerImpl):
    """Controller for Client entity with CRUD operations."""

    def __init__(self):
        """
        Initialize ClientController with dependency injection.

        The service is created per request with the database session.
        """
        super().__init__(
            schema=ClientSchema,
            service_factory=lambda db: ClientService(db),
            tags=["Clients"]
        )
        self._register_login_route()

    def _register_login_route(self):
        """Register login endpoint."""

        @self.router.post("/login", response_model=LoginResponse)
        async def login(request: LoginRequest, db: Session = Depends(get_db)):
            service = self.service_factory(db)
            client = service.authenticate(request.email, request.password)
            if not client:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            return LoginResponse(
                id_key=client.id_key,
                name=client.name
            )
