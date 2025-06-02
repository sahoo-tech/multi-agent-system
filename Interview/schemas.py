from pydantic import BaseModel
from typing import Optional, Dict, Any

class IntakeRequest(BaseModel):
    file: Optional[bytes] = None
    json_body: Optional[str] = None
    email_body: Optional[str] = None

class ClassificationResult(BaseModel):
    format: str
    intent: str

class JSONAgentResult(BaseModel):
    flowbit_schema: Dict[str, Any]
    anomalies: Optional[list]

class EmailParserAgentResult(BaseModel):
    sender: str
    intent: str
    urgency: str
    conversation_id: Optional[str]
    timestamp: str

class IntakeResponse(BaseModel):
    classification: ClassificationResult
    extraction: Optional[Dict[str, Any]]
