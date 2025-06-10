from typing import Optional
from pydantic import BaseModel, Field


class ResponsibleGroupView(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", description="Unique Code for this object. Used in Configuration and Permissions Logic", max_length=1024)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)


class ResponsibleView(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    group: str = Field(..., title="Group")
    group_object: Optional[ResponsibleGroupView] = None
    user_code: Optional[str] = Field(None, title="User code", description="Unique Code for this object. Used in Configuration and Permissions Logic", max_length=1024)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)