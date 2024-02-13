from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class PictureSchema(BaseModel):
    """Pydantic model for validating incoming picture data."""
    description: Optional[str] = Field(max_length=255)
    tags: Optional[str] = Field(default=None, description='Введіть теги через кому. Максимальна кількість тегів - 5')


class PictureUpdateSchema(BaseModel):
    """Pydantic model for validating incoming picture update data."""
    description: Optional[str] = Field(max_length=255)


class PictureResponseSchema(BaseModel):
    """Pydantic model for serializing picture data in responses."""
    user_id: int
    picture_id: int
    url: str
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    created_at: datetime
    comments: Optional[list[str]] = []
