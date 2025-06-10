from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from .base import SourceTypeEnum, ValueTypeEnum, KindEnum


class GenericClassifierRecursiveField(BaseModel):
    pass


class GenericClassifier(BaseModel):
    id: Optional[int] = Field(None, title="Id")
    name: str = Field(..., title="Name", max_length=255)
    level: int = Field(..., title="Level", description="readonly")
    children: Optional[List[GenericClassifierRecursiveField]] = None


class GenericClassifierWithoutChildren(BaseModel):
    id: Optional[int] = Field(None, title="Id")
    name: str = Field(..., title="Name", max_length=255)
    level: int = Field(..., title="Level", description="readonly")
    parent: int = Field(..., title="Parent", description="readonly")


class GenericClassifierNode(BaseModel):
    id: Optional[int] = Field(None, title="Id")
    attribute_type: int = Field(..., title="Attribute type", description="readonly")
    level: int = Field(..., title="Level", description="readonly")
    parent: int = Field(..., title="Parent", description="readonly")
    name: str = Field(..., title="Name", max_length=255)


class GenericClassifierView(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    name: str = Field(..., title="Name", max_length=255)
    level: int = Field(..., title="Level", description="readonly")
    parent: int = Field(..., title="Parent", description="readonly")
    parent_object: Optional[GenericClassifierRecursiveField] = None


class GenericAttributeType(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    configuration_code: str = Field(..., title="Configuration Code", max_length=255, min_length=1)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    notes: Optional[str] = Field(None, title="Notes", description="Notes, any useful information about the object")
    prefix: Optional[str] = Field(None, title="Prefix", max_length=255)
    favorites: Optional[str] = Field(None, title="Favorites")
    expr: Optional[str] = Field('""', title="Expr", max_length=4096)
    can_recalculate: bool = Field(False, title="Can recalculate")
    tooltip: Optional[str] = Field(None, title="Tooltip")
    kind: KindEnum = Field(..., title="Kind")
    content_type: str = Field(..., title="Content type")
    value_type: ValueTypeEnum = Field(..., title="Value type")
    order: int = Field(0, title="Order", ge=-2147483648, le=2147483647)
    is_hidden: bool = Field(False, title="Is hidden")
    classifiers: Optional[List[GenericClassifier]] = None
    classifiers_flat: List[GenericClassifierWithoutChildren] = Field([], description="readonly")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)


class GenericAttributeTypeView(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", description="Unique Code for this object. Used in Configuration and Permissions Logic", max_length=1024)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    notes: Optional[str] = Field(None, title="Notes", description="Notes, any useful information about the object")
    can_recalculate: bool = Field(False, title="Can recalculate")
    value_type: ValueTypeEnum = Field(..., title="Value type")
    order: int = Field(0, title="Order", ge=-2147483648, le=2147483647)
    is_hidden: bool = Field(False, title="Is hidden")
    kind: KindEnum = Field(..., title="Kind")


class GenericAttribute(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    attribute_type: str = Field(..., title="Attribute type")
    value_string: Optional[str] = Field(None, title="Value (String)", max_length=255)
    value_float: Optional[float] = Field(None, title="Value (Float)")
    value_date: Optional[date] = Field(None, title="Value (Date)")
    classifier: Optional[str] = Field(None, title="Classifier")
    attribute_type_object: Optional[GenericAttributeTypeView] = None
    classifier_object: Optional[GenericClassifierView] = None


class RecalculateAttributes(BaseModel):
    task_id: Optional[str] = Field(None, title="Task id")
    task_status: str = Field(..., title="Task status", description="readonly")
    processed_rows: str = Field(..., title="Processed rows", description="readonly")
    total_rows: str = Field(..., title="Total rows", description="readonly")
    stats: str = Field(..., title="Stats", description="readonly")
    stats_file_report: str = Field(..., title="Stats file report", description="readonly")