from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field

from libs.schema.base import PaginatedResponse
from libs.schema.via_data_model_codegen.finmars_schema import (
    Portfolio,
    PortfolioLight,
    PortfolioType,
    PortfolioTypeLight,
    PortfolioRegister,
    PortfolioRegisterRecord,
    PortfolioHistory,
    PortfolioBundle,
    FirstTransactionDateRequest,
    PortfolioReconcileGroup,
    PortfolioReconcileHistory,
    GenericAttributeType,
    Clients,
)

T = TypeVar("T")


class PaginatedResponseGeneric(PaginatedResponse, Generic[T]):
    results: List[T]


# Portfolio responses
class PortfolioListResponse(PaginatedResponse):
    results: List[Portfolio]


class PortfolioLightListResponse(PaginatedResponse):
    results: List[PortfolioLight]


class PortfolioTypeListResponse(PaginatedResponse):
    results: List[PortfolioType]


class PortfolioTypeLightListResponse(PaginatedResponse):
    results: List[PortfolioTypeLight]


class PortfolioRegisterListResponse(PaginatedResponse):
    results: List[PortfolioRegister]


class PortfolioRegisterRecordListResponse(PaginatedResponse):
    results: List[PortfolioRegisterRecord]


class PortfolioHistoryListResponse(PaginatedResponse):
    results: List[PortfolioHistory]


class PortfolioBundleListResponse(PaginatedResponse):
    results: List[PortfolioBundle]


class FirstTransactionDateListResponse(PaginatedResponse):
    results: List[FirstTransactionDateRequest]


# Reconcile responses
class PortfolioReconcileGroupListResponse(PaginatedResponse):
    results: List[PortfolioReconcileGroup]


class PortfolioReconcileHistoryListResponse(PaginatedResponse):
    results: List[PortfolioReconcileHistory]


# Attribute responses
class GenericAttributeTypeListResponse(PaginatedResponse):
    results: List[GenericAttributeType]


# Client responses
class ClientsListResponse(PaginatedResponse):
    results: List[Clients]
