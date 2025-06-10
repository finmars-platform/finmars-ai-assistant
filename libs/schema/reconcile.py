from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from .base import StatusEnum


class Params(BaseModel):
    only_errors: Optional[bool] = Field(False, title="Only errors")
    round_digits: Optional[int] = Field(2, title="Round digits", ge=0)
    report_ttl: Optional[int] = Field(90, title="Report ttl", ge=1)
    precision: Optional[float] = Field(1.0, title="Precision", ge=0)
    notifications: Optional[Dict[str, str]] = Field({}, title="Notifications")


class PortfolioReconcileGroup(BaseModel):
    id: Optional[int] = Field(None, title="ID", description="readonly")
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    notes: Optional[str] = Field(None, title="Notes", description="Notes, any useful information about the object")
    portfolios: List[str] = Field(..., title="Portfolios")
    params: Params = Field(..., title="Params")
    last_calculated_at: Optional[datetime] = Field(None, title="Last time calculation was done")
    created_at: Optional[datetime] = Field(None, title="Created at", description="readonly")
    modified_at: Optional[datetime] = Field(None, title="Modified at", description="readonly")
    deleted_at: Optional[datetime] = Field(None, title="Deleted at", description="readonly")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)


class FileReport(BaseModel):
    id: Optional[int] = Field(None, title="ID", description="readonly")
    name: str = Field(..., title="Name", max_length=255, min_length=1)
    notes: Optional[str] = Field(None, title="Notes")
    type: Optional[str] = Field(None, title="Type", max_length=255)
    created_at: Optional[datetime] = Field(None, title="Created at", description="readonly")
    content_type: Optional[str] = Field(None, title="Content type", max_length=255)
    content_type_verbose: Optional[str] = Field(None, title="Content type verbose", description="readonly")
    file_url: Optional[str] = Field(None, title="File URL")


class PortfolioReconcileHistory(BaseModel):
    id: Optional[int] = Field(None, title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    portfolio_reconcile_group: int = Field(..., title="Portfolio reconcile group")
    date: Optional[date] = Field(None, title="Date")
    verbose_result: Optional[str] = Field(None, title="Verbose result")
    error_message: Optional[str] = Field(None, alias="error_message", description="Error message if any")
    status: Optional[StatusEnum] = Field(None, title="Status")
    file_report: Optional[int] = Field(None, title="File report")
    is_enabled: Optional[bool] = Field(None, title="Is enabled")
    report_ttl: Optional[int] = Field(None, title="Number of days until report expires", ge=0, le=2147483647)
    created_at: Optional[datetime] = Field(None, title="Created at", description="readonly")
    modified_at: Optional[datetime] = Field(None, title="Modified at", description="readonly")
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