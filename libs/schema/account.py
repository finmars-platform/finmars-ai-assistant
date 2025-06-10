from typing import Optional
from pydantic import BaseModel, Field


class AccountTypeView(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)


class AccountView(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    type: str = Field(..., title="Type")
    type_object: Optional[AccountTypeView] = None
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)