from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .base import SourceTypeEnum


class PricingPolicy(BaseModel):
    id: Optional[int] = Field(None, title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    configuration_code: str = Field(..., title="Configuration Code", max_length=255, min_length=1)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    notes: Optional[str] = Field(None, title="Notes", description="Notes, any useful information about the object")
    expr: Optional[str] = Field(None, title="Expression", max_length=4096)
    is_active: Optional[bool] = Field(True, title="Is active")
    actual_at: Optional[datetime] = Field(None, title="Actual at")
    source_type: Optional[SourceTypeEnum] = Field(SourceTypeEnum.MANUAL, title="Source type")
    source_origin: Optional[str] = Field("manual", title="Source origin", min_length=1)
    external_id: Optional[str] = Field(None, title="External id", min_length=1)
    is_manual_locked: Optional[bool] = Field(False, title="Is manual locked")
    is_locked: Optional[bool] = Field(True, title="Is locked")
    created_at: Optional[datetime] = Field(None, title="Created at", description="readonly")
    modified_at: Optional[datetime] = Field(None, title="Modified at", description="readonly")
    deleted_at: Optional[datetime] = Field(None, title="Deleted at", description="readonly")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)