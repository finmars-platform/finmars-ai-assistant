from datetime import date
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class InstrumentClass(BaseModel):
    id: int = Field(..., title="ID", ge=0, le=32767)
    user_code: str = Field(..., title="User code", max_length=255, min_length=1)
    name: str = Field("", title="Name", max_length=255)
    description: str = Field("", title="Description")


class InstrumentTypeView(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    instrument_class: int = Field(..., title="Instrument class")
    instrument_class_object: Optional[InstrumentClass] = None
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    instrument_form_layouts: Optional[str] = Field(None, title="Instrument form layouts")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)


class InstrumentView(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    instrument_type: int = Field(..., title="Instrument type")
    instrument_type_object: Optional[InstrumentTypeView] = None
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    notes: Optional[str] = Field(None, title="Notes", description="Notes, any useful information about the object")
    is_active: bool = Field(True, title="Is active")
    is_deleted: bool = Field(False, title="Is deleted", description="Mark object as deleted. Does not actually delete the object.")
    identifier: Dict[str, Any] = Field({}, title="Identifier", description="Dictionary of identifiers from different sources")
    has_linked_with_portfolio: bool = Field(False, title="Has linked with portfolio")
    user_text_1: Optional[str] = Field(None, title="User text 1", description="User specified field 1", max_length=255)
    user_text_2: Optional[str] = Field(None, title="User text 2", description="User specified field 2", max_length=255)
    user_text_3: Optional[str] = Field(None, title="User text 3", description="User specified field 3", max_length=255)
    maturity_date: Optional[date] = Field(None, title="Maturity date")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)