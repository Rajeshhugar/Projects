
from pydantic import BaseModel
from typing import List

class QueryInput(BaseModel):
    query: str
    session_id: str

class QueryResponse(BaseModel):
    response: str
    session_id: str

class DocumentInfo(BaseModel):
    filename: str
    doc_id: str

class DeleteFileRequest(BaseModel):
    doc_id: str
