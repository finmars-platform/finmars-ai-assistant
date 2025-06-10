from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from .base import SourceTypeEnum, StatusEnum, PeriodTypeEnum, PerformanceMethodEnum, SegmentationTypeEnum
from .common import GenericAttribute
from .pricing import PricingPolicy
from .currency import CurrencyView
from .instrument import InstrumentView


# Forward references
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .transaction import TransactionClass
    from .client import Clients
    from .account import AccountView
    from .responsible import ResponsibleView
    from .counterparty import CounterpartyView
    from .transaction import TransactionTypeView


class PortfolioClass(BaseModel):
    id: int = Field(..., title="ID", ge=0, le=32767)
    user_code: str = Field(..., title="User code", max_length=255, min_length=1)
    name: str = Field("", title="Name", max_length=255)
    description: str = Field("", title="Description")


class PortfolioView(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)


class PortfolioRegisterView(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)


class PortfolioType(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    configuration_code: str = Field(..., title="Configuration Code", max_length=255, min_length=1)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    notes: Optional[str] = Field(None, title="Notes", description="Notes, any useful information about the object")
    is_deleted: bool = Field(False, title="Is deleted", description="Mark object as deleted. Does not actually delete the object.")
    is_enabled: bool = Field(True, title="Is enabled")
    portfolio_class: int = Field(..., title="Portfolio class")
    portfolio_class_object: Optional[PortfolioClass] = None
    created_at: datetime = Field(..., title="Created at", description="readonly")
    modified_at: datetime = Field(..., title="Modified at", description="readonly")
    deleted_at: Optional[datetime] = Field(None, title="Deleted at", description="readonly")
    attributes: Optional[List[GenericAttribute]] = None
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)


class PortfolioTypeLight(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    is_deleted: bool = Field(False, title="Is deleted", description="Mark object as deleted. Does not actually delete the object.")
    is_enabled: bool = Field(True, title="Is enabled")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)


class PortfolioPortfolioRegister(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    notes: Optional[str] = Field(None, title="Notes", description="Notes, any useful information about the object")
    is_deleted: bool = Field(False, title="Is deleted", description="Mark object as deleted. Does not actually delete the object.")
    is_enabled: bool = Field(True, title="Is enabled")
    linked_instrument: Optional[int] = Field(None, title="Linked instrument")
    linked_instrument_object: Optional[InstrumentView] = None
    valuation_currency: str = Field(..., title="Valuation currency")
    valuation_currency_object: Optional[CurrencyView] = None
    valuation_pricing_policy: str = Field(..., title="Valuation pricing policy")
    valuation_pricing_policy_object: Optional[PricingPolicy] = None
    default_price: float = Field(1.0, title="Default price")
    is_active: bool = Field(True, title="Is active")
    actual_at: Optional[datetime] = Field(None, title="Actual at")
    source_type: SourceTypeEnum = Field(SourceTypeEnum.MANUAL, title="Source type")
    source_origin: str = Field("manual", title="Source origin", min_length=1)
    external_id: Optional[str] = Field(None, title="External id", min_length=1)
    is_manual_locked: bool = Field(False, title="Is manual locked")
    is_locked: bool = Field(True, title="Is locked")
    created_at: datetime = Field(..., title="Created at", description="readonly")
    modified_at: datetime = Field(..., title="Modified at", description="readonly")
    deleted_at: Optional[datetime] = Field(None, title="Deleted at", description="readonly")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)
    attributes: Optional[List[GenericAttribute]] = None


class PortfolioRegister(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    notes: Optional[str] = Field(None, title="Notes", description="Notes, any useful information about the object")
    is_deleted: bool = Field(False, title="Is deleted", description="Mark object as deleted. Does not actually delete the object.")
    is_enabled: bool = Field(True, title="Is enabled")
    portfolio: int = Field(..., title="Portfolio")
    portfolio_object: Optional[PortfolioView] = None
    linked_instrument: Optional[int] = Field(None, title="Linked instrument")
    linked_instrument_object: Optional[InstrumentView] = None
    valuation_currency: str = Field(..., title="Valuation currency")
    valuation_currency_object: Optional[CurrencyView] = None
    valuation_pricing_policy: str = Field(..., title="Valuation pricing policy")
    valuation_pricing_policy_object: Optional[PricingPolicy] = None
    default_price: float = Field(1.0, title="Default price")
    is_active: bool = Field(True, title="Is active")
    actual_at: Optional[datetime] = Field(None, title="Actual at")
    source_type: SourceTypeEnum = Field(SourceTypeEnum.MANUAL, title="Source type")
    source_origin: str = Field("manual", title="Source origin", min_length=1)
    external_id: Optional[str] = Field(None, title="External id", min_length=1)
    is_manual_locked: bool = Field(False, title="Is manual locked")
    is_locked: bool = Field(True, title="Is locked")
    created_at: datetime = Field(..., title="Created at", description="readonly")
    modified_at: datetime = Field(..., title="Modified at", description="readonly")
    deleted_at: Optional[datetime] = Field(None, title="Deleted at", description="readonly")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)
    attributes: Optional[List[GenericAttribute]] = None


class PortfolioHistory(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    portfolio: str = Field(..., title="Portfolio")
    currency: str = Field(..., title="Currency")
    pricing_policy: int = Field(..., title="Pricing policy")
    date: date = Field(..., title="Date")
    date_from: date = Field(..., title="Date from")
    period_type: PeriodTypeEnum = Field(..., alias="period_type")
    cost_method: int = Field(..., title="Cost method")
    performance_method: PerformanceMethodEnum = Field(..., title="Performance method")
    benchmark: str = Field("", title="Benchmark", max_length=255)
    nav: Optional[float] = Field(None, title="Nav", description="Net Asset Value")
    gav: Optional[float] = Field(None, title="Gav", description="Gross Asset Value")
    cash_flow: Optional[float] = Field(None, title="Cash flow")
    cash_inflow: Optional[float] = Field(None, title="Cash inflow")
    cash_outflow: Optional[float] = Field(None, title="Cash outflow")
    total: Optional[float] = Field(None, title="Total", description="Total Value of the Portfolio from P&L Report")
    cumulative_return: Optional[float] = Field(None, title="Cumulative return")
    annualized_return: Optional[float] = Field(None, title="Annualized return")
    portfolio_volatility: Optional[float] = Field(None, title="Portfolio volatility")
    annualized_portfolio_volatility: Optional[float] = Field(None, title="Annualized portfolio volatility")
    sharpe_ratio: Optional[float] = Field(None, alias="sharpe_ratio")
    max_annualized_drawdown: Optional[float] = Field(None, alias="max_annualized_drawdown")
    betta: Optional[float] = Field(None, title="Betta")
    alpha: Optional[float] = Field(None, title="Alpha")
    correlation: Optional[float] = Field(None, title="Correlation")
    weighted_duration: Optional[float] = Field(None, alias="weighted_duration")
    created_at: datetime = Field(..., title="Created at", description="readonly")
    modified_at: datetime = Field(..., title="Modified at", description="readonly")
    is_enabled: bool = Field(True, title="Is enabled")
    error_message: Optional[str] = Field(None, alias="error_message", description="Error message if any")
    status: StatusEnum = Field(StatusEnum.OK, title="Status")
    deleted_at: Optional[datetime] = Field(None, title="Deleted at", description="readonly")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)
    currency_object: Optional[CurrencyView] = None
    portfolio_object: Optional[PortfolioView] = None
    pricing_policy_object: Optional[PricingPolicy] = None


class CalculatePortfolioHistory(BaseModel):
    portfolio: str = Field(..., title="Portfolio")
    currency: Optional[str] = Field(None, title="Currency")
    pricing_policy: Optional[str] = Field(None, title="Pricing policy")
    date: date = Field(..., title="Date")
    calculation_period_date_from: Optional[date] = Field(None, title="Calculation period date from")
    segmentation_type: SegmentationTypeEnum = Field(SegmentationTypeEnum.BUSINESS_DAYS_END_OF_MONTHS, title="Segmentation type")
    period_type: PeriodTypeEnum = Field(PeriodTypeEnum.YTD, title="Period type")
    cost_method: Optional[str] = Field(None, title="Cost method")
    performance_method: PerformanceMethodEnum = Field(PerformanceMethodEnum.MODIFIED_DIETZ, title="Performance method")
    benchmark: str = Field("sp_500", title="Benchmark", min_length=1)


class PortfolioBundle(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    notes: Optional[str] = Field(None, title="Notes", description="Notes, any useful information about the object")
    registers: List[int] = Field([], title="Registers")
    is_active: bool = Field(True, title="Is active")
    actual_at: Optional[datetime] = Field(None, title="Actual at")
    source_type: SourceTypeEnum = Field(SourceTypeEnum.MANUAL, title="Source type")
    source_origin: str = Field("manual", title="Source origin", min_length=1)
    external_id: Optional[str] = Field(None, title="External id", min_length=1)
    is_manual_locked: bool = Field(False, title="Is manual locked")
    is_locked: bool = Field(True, title="Is locked")
    created_at: datetime = Field(..., title="Created at", description="readonly")
    modified_at: datetime = Field(..., title="Modified at", description="readonly")
    deleted_at: Optional[datetime] = Field(None, title="Deleted at", description="readonly")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)


class FirstTransactionDateRequest(BaseModel):
    portfolio: Optional[str] = Field(None, title="Portfolio")
    date_field: str = Field("transaction_date", title="Date field", min_length=1)


class PortfolioRegisterRecord(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    portfolio: int = Field(..., title="Portfolio")
    instrument: int = Field(..., title="Instrument")
    transaction_class: int = Field(..., title="Transaction class")
    transaction_code: int = Field(..., title="Transaction code", ge=-2147483648, le=2147483647)
    transaction_date: date = Field(..., title="Transaction date")
    cash_amount: float = Field(..., title="Cash amount", description="Cash amount")
    cash_currency: int = Field(..., title="Cash currency")
    fx_rate: float = Field(1.0, title="Fx rate")
    cash_amount_valuation_currency: float = Field(..., title="Cash amount valuation currency", description="Cash amount valuation currency")
    valuation_currency: int = Field(..., title="Valuation currency")
    nav_valuation_currency: float = Field(..., title="Nav valuation currency")
    nav_previous_business_day_valuation_currency: float = Field(..., title="Nav previous business day valuation currency")
    nav_previous_register_record_day_valuation_currency: float = Field(..., title="Nav previous register record day valuation currency")
    n_shares_previous_day: float = Field(..., title="N shares previous day")
    n_shares_added: float = Field(..., title="N shares added")
    dealing_price_valuation_currency: float = Field(..., title="Dealing price valuation currency", description="Dealing price valuation currency")
    rolling_shares_of_the_day: float = Field(..., title="Rolling shares of the day")
    transaction: int = Field(..., title="Transaction")
    complex_transaction: int = Field(..., title="Complex transaction")
    portfolio_register: int = Field(..., title="Portfolio register")
    share_price_calculation_type: str = Field(..., title="Price calculation type", max_length=255, min_length=1)
    created_at: datetime = Field(..., title="Created at", description="readonly")
    modified_at: datetime = Field(..., title="Modified at", description="readonly")
    deleted_at: Optional[datetime] = Field(None, title="Deleted at", description="readonly")
    cash_currency_object: Optional[CurrencyView] = None
    valuation_currency_object: Optional[CurrencyView] = None
    transaction_class_object: Optional['TransactionClass'] = None
    portfolio_object: Optional[PortfolioView] = None
    portfolio_register_object: Optional[PortfolioRegisterView] = None
    instrument_object: Optional[InstrumentView] = None
    valuation_pricing_policy_object: Optional[PricingPolicy] = None


class PrCalculatePriceHistoryRequest(BaseModel):
    date_from: Optional[date] = Field(None, title="Date from")
    date_to: Optional[date] = Field(None, title="Date to")
    portfolios: List[str] = Field([], min_items=0)


class PrCalculateRecordsRequest(BaseModel):
    portfolios: List[str] = Field([])


class PortfolioLight(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    is_default: str = Field(..., title="Is default", description="readonly")
    is_deleted: bool = Field(False, title="Is deleted", description="Mark object as deleted. Does not actually delete the object.")
    is_enabled: bool = Field(True, title="Is enabled")
    first_transaction: Dict[str, Any] = Field({}, title="First transaction", description="readonly")
    first_transaction_date: Optional[date] = Field(None, title="First transaction date")
    first_cash_flow_date: Optional[date] = Field(None, title="First cash flow date")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)


class Portfolio(BaseModel):
    id: int = Field(..., title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    notes: Optional[str] = Field(None, title="Notes", description="Notes, any useful information about the object")
    is_default: str = Field(..., title="Is default", description="readonly")
    is_deleted: bool = Field(False, title="Is deleted", description="Mark object as deleted. Does not actually delete the object.")
    is_enabled: bool = Field(True, title="Is enabled")
    registers: Optional[List[PortfolioPortfolioRegister]] = Field(None, title="Registers", description="readonly")
    first_transaction: Dict[str, Any] = Field({}, title="First transaction", description="readonly")
    first_transaction_date: str = Field(..., title="First transaction date", description="readonly")
    first_cash_flow_date: str = Field(..., title="First cash flow date", description="readonly")
    portfolio_type: Optional[int] = Field(None, title="Portfolio type")
    portfolio_type_object: Optional[PortfolioType] = None
    client: Optional[int] = Field(None, title="Client")
    client_object: Optional['Clients'] = None
    is_active: bool = Field(True, title="Is active")
    actual_at: Optional[datetime] = Field(None, title="Actual at")
    source_type: SourceTypeEnum = Field(SourceTypeEnum.MANUAL, title="Source type")
    source_origin: str = Field("manual", title="Source origin", min_length=1)
    external_id: Optional[str] = Field(None, title="External id", min_length=1)
    is_manual_locked: bool = Field(False, title="Is manual locked")
    is_locked: bool = Field(True, title="Is locked")
    created_at: datetime = Field(..., title="Created at", description="readonly")
    modified_at: datetime = Field(..., title="Modified at", description="readonly")
    deleted_at: Optional[datetime] = Field(None, title="Deleted at", description="readonly")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)
    attributes: Optional[List[GenericAttribute]] = None
    resource_groups: List[str] = Field([], title="Resource groups")
    resource_groups_object: List[str] = Field([], description="readonly")
    accounts_object: List['AccountView'] = Field([], description="readonly")
    responsibles_object: List['ResponsibleView'] = Field([], description="readonly")
    counterparties_object: List['CounterpartyView'] = Field([], description="readonly")
    transaction_types_object: List['TransactionTypeView'] = Field([], description="readonly")