from datetime import date, datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class SourceTypeEnum(str, Enum):
    MANUAL = "manual"
    EXTERNAL = "external"


class StatusEnum(str, Enum):
    OK = "ok"
    ERROR = "error"


class PeriodTypeEnum(str, Enum):
    DAILY = "daily"
    YTD = "ytd"
    MTD = "mtd"
    QTD = "qtd"
    INCEPTION = "inception"


class PerformanceMethodEnum(str, Enum):
    MODIFIED_DIETZ = "modified_dietz"
    TIME_WEIGHTED = "time_weighted"


class SegmentationTypeEnum(str, Enum):
    DAYS = "days"
    BUSINESS_DAYS = "business_days"
    BUSINESS_DAYS_END_OF_MONTHS = "business_days_end_of_months"


class ValueTypeEnum(int, Enum):
    TYPE_10 = 10
    TYPE_20 = 20
    TYPE_30 = 30
    TYPE_40 = 40


class KindEnum(int, Enum):
    TYPE_1 = 1
    TYPE_2 = 2


class TransactionUniqueCodeOptionsEnum(int, Enum):
    OPTION_1 = 1
    OPTION_2 = 2
    OPTION_3 = 3
    OPTION_4 = 4


class PaginatedResponse(BaseModel):
    count: int
    next: Optional[str] = Field(None, format="uri")
    previous: Optional[str] = Field(None, format="uri")
