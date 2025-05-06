from datetime import datetime
from pydantic import BaseModel


class CFDIBill(BaseModel):
    id: str
    emitter_rfc: str
    emitter_reason: str
    receiver_rfc: str
    receiver_reason: str
    emitted_date: datetime
    certification_date: datetime
    certification_pac: str
    total_value: float
    effect: str
    status: str


class CFDIDownloadItem(BaseModel):
    request_id: str
    type: str
    count: int


class DownloadRequest(BaseModel):
    request_id: str


class PdfFile(BaseModel):
    pdf_url: str


class DownloadFile(BaseModel):
    download_url: str


class AcknowledgementResult(BaseModel):
    id: str
    period: str
    motive: str
    document_type: str
    send_type: str
    file_name: str
    reception_date: str
    status: str
