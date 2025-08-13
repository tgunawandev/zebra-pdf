"""
Pydantic models for FastAPI request/response validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class LabelData(BaseModel):
    """Single label data for printing."""
    qr_code: str = Field(..., description="QR code content", example="TEST123456")
    do_number: str = Field(..., description="Delivery Order number", example="DO-TEST/001")
    route: str = Field(..., description="Delivery route", example="Route A")
    date: str = Field(..., description="Date in DD/MM/YY format", example="13/08/25")
    customer: str = Field(..., description="Customer name", example="Test Customer")
    so_number: str = Field(..., description="Sales Order number", example="SO-TEST001")
    mo_number: str = Field(..., description="Manufacturing Order number", example="MO-TEST001")
    item: str = Field(..., description="Product/Item name", example="Test Product")
    qty: str = Field(..., description="Quantity", example="1")
    uom: str = Field(..., description="Unit of measure", example="PCS")


class PrintRequest(BaseModel):
    """Request model for printing labels."""
    labels: List[LabelData] = Field(..., description="List of labels to print", min_items=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "labels": [
                    {
                        "qr_code": "TEST123456",
                        "do_number": "DO-TEST/001",
                        "route": "Route A",
                        "date": "13/08/25",
                        "customer": "Test Customer",
                        "so_number": "SO-TEST001",
                        "mo_number": "MO-TEST001",
                        "item": "Test Product",
                        "qty": "1",
                        "uom": "PCS"
                    }
                ]
            }
        }


class PrintResponse(BaseModel):
    """Response model for print operations."""
    success: bool = Field(..., description="Whether the print job was successful")
    message: str = Field(..., description="Human-readable status message")
    labels_count: int = Field(..., description="Number of labels processed")
    job_info: str = Field(..., description="Printer job information")
    timestamp: str = Field(..., description="ISO timestamp of the operation")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Health status", example="healthy")
    timestamp: str = Field(..., description="ISO timestamp")
    printer: str = Field(..., description="Printer name")


class PrinterStatus(BaseModel):
    """Printer status details."""
    exists: bool = Field(..., description="Whether printer exists")
    enabled: bool = Field(..., description="Whether printer is enabled")
    accepting_jobs: bool = Field(..., description="Whether printer accepts jobs")
    state: str = Field(..., description="Printer state")
    connection: str = Field(..., description="Connection type")
    jobs_queued: int = Field(..., description="Number of queued jobs")


class PrinterStatusResponse(BaseModel):
    """Response model for printer status."""
    printer: str = Field(..., description="Printer name")
    status: str = Field(..., description="Overall status")
    details: PrinterStatus = Field(..., description="Detailed printer information")
    timestamp: str = Field(..., description="ISO timestamp")


class TokenRequest(BaseModel):
    """Request model for token generation."""
    name: str = Field(..., description="Token name", example="production")
    description: Optional[str] = Field(None, description="Token description", example="Production API access")


class TokenResponse(BaseModel):
    """Response model for token generation."""
    success: bool = Field(..., description="Whether token generation was successful")
    token: str = Field(..., description="Generated API token")
    name: str = Field(..., description="Token name")
    message: str = Field(..., description="Status message")
    webhook_examples: Dict[str, str] = Field(..., description="Usage examples")


class TokenInfo(BaseModel):
    """Token information."""
    name: str = Field(..., description="Token name")
    description: Optional[str] = Field(None, description="Token description")
    created_at: str = Field(..., description="Creation timestamp")
    is_active: bool = Field(..., description="Whether token is active")


class TokenListResponse(BaseModel):
    """Response model for listing tokens."""
    success: bool = Field(..., description="Whether operation was successful")
    tokens: List[TokenInfo] = Field(..., description="List of tokens")
    current_token: str = Field(..., description="Currently used token name")


class AuthInfoResponse(BaseModel):
    """Response model for authentication information."""
    authentication_enabled: bool = Field(..., description="Whether authentication is enabled")
    total_tokens: int = Field(..., description="Total number of tokens")
    active_tokens: int = Field(..., description="Number of active tokens")
    tokens: List[TokenInfo] = Field(..., description="List of all tokens")
    endpoints: Dict[str, Any] = Field(..., description="Endpoint categorization and auth methods")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="ISO timestamp")