from pydantic import BaseModel, Field, field_validator
from typing import List


class InvestigateRequest(BaseModel):
    """Request body for /investigate endpoint"""
    transaction_id: str = Field(..., min_length=1, description="Transaction ID to investigate")


class InvestigateResponse(BaseModel):
    """Response from /investigate endpoint"""
    transaction_id: str = Field(..., description="The transaction ID that was investigated")
    status: str = Field(..., description="Overall settlement status")
    plain_english: str = Field(..., description="Plain English explanation")
    exceptions: List[str] = Field(default_factory=list, description="List of exceptions or uncertainties")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0 to 1")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        allowed = {"SETTLED", "PENDING", "FAILED", "PARTIAL", "UNKNOWN"}
        if v not in allowed:
            return "UNKNOWN"
        return v