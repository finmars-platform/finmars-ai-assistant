from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from .base import StatusEnum


class Params(BaseModel):
    only_errors: bool = Field(False, title="Only errors")
    round_digits: int = Field(2, title="Round digits", ge=0)
    report_ttl: int = Field(90, title="Report ttl", ge=1)
    precision: float = Field(1.0, title="Precision", ge=0)
    notifications: Dict[str, Optional[str]] = Field({}, title="Notifications")


class PortfolioReconcileGroup(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    notes: Optional[str] = Field(None, title="Notes", description="Notes, any useful information about the object")
    portfolios: List[str] = Field(..., title="Portfolios")
    params: Params = Field(..., title="Params")
    last_calculated_at: Optional[datetime] = Field(None, title="Last time calculation was done")
    created_at: datetime = Field(..., title="Created at", description="readonly")
    modified_at: datetime = Field(..., title="Modified at", description="readonly")
    deleted_at: Optional[datetime] = Field(None, title="Deleted at", description="readonly")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)


class FileReport(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    name: str = Field(..., title="Name", max_length=255, min_length=1)
    notes: str = Field("", title="Notes")
    type: str = Field("", title="Type", max_length=255)
    created_at: datetime = Field(..., title="Created at", description="readonly")
    content_type: str = Field("", title="Content type", max_length=255)
    content_type_verbose: str = Field(..., title="Content type verbose", description="readonly")
    file_url: str = Field("", title="File URL")


class PortfolioReconcileHistory(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    portfolio_reconcile_group: int = Field(..., title="Portfolio reconcile group")
    date: date = Field(..., title="Date")
    verbose_result: Optional[str] = Field(None, title="Verbose result")
    error_message: Optional[str] = Field(None, alias="error_message", description="Error message if any")
    status: StatusEnum = Field(StatusEnum.OK, title="Status")
    file_report: Optional[int] = Field(None, title="File report")
    is_enabled: bool = Field(True, title="Is enabled")
    report_ttl: int = Field(0, title="Number of days until report expires", ge=0, le=2147483647)
    created_at: datetime = Field(..., title="Created at", description="readonly")
    modified_at: datetime = Field(..., title="Modified at", description="readonly")
    deleted_at: Optional[datetime] = Field(None, title="Deleted at", description="readonly")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)
    portfolio_reconcile_group_object: Optional[PortfolioReconcileGroup] = None
    file_report_object: Optional[FileReport] = None


class BulkCalculateReconcileHistory(BaseModel):
    reconcile_groups: List[str] = Field(..., title="Reconcile groups")
    dates: List[date] = Field(..., title="Dates")


class CalculateReconcileHistory(BaseModel):
    portfolio_reconcile_group: str = Field(..., title="Portfolio reconcile group")
    dates: List[date] = Field(..., title="Dates")


class PortfolioReconcileStatus(BaseModel):
    portfolios: List[str] = Field(..., title="Portfolios")
    date: date = Field(..., title="Date")