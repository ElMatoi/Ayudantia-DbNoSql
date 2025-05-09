from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")

class ResponseMessage(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None

class ErrorMessage(BaseModel):
    success: bool = False
    message: str
    error: str
