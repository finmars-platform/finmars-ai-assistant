from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field, EmailStr

if TYPE_CHECKING:
    from .portfolio import PortfolioView


class ClientSecretLight(BaseModel):
    id: Optional[int] = Field(None, title="ID", description="readonly")
    client: Optional[int] = Field(None, title="Client", description="readonly")
    user_code: str = Field(..., title="User code", description="Unique Code for this object. Used in Configuration and Permissions Logic", max_length=1024, min_length=1)
    provider: Optional[str] = Field(None, title="Provider", max_length=255)
    portfolio: Optional[str] = Field(None, title="Portfolio", max_length=255)
    path_to_secret: Optional[str] = Field(None, title="Path to secret", max_length=255)
    notes: Optional[str] = Field(None, title="Notes", max_length=255)


class Clients(BaseModel):
    id: Optional[int] = Field(None, title="ID", description="readonly")
    user_code: Optional[str] = Field(None, title="User code", max_length=255)
    name: str = Field(..., title="Name", description="Human Readable Name of the object", max_length=255, min_length=1)
    short_name: Optional[str] = Field(None, title="Short name", description="Short Name of the object. Used in dropdown menus")
    public_name: Optional[str] = Field(None, title="Public name", description="Used if user does not have permissions to view object", max_length=255)
    first_name: Optional[str] = Field(None, title="First name", description="First name of client", max_length=255)
    last_name: Optional[str] = Field(None, title="Last name", description="Last name of client", max_length=255)
    telephone: Optional[str] = Field(None, title="Telephone", description="Telephone number of client (symbol '+' is optional, length from 5 to 15 digits)", max_length=255)
    email: Optional[EmailStr] = Field(None, title="Email", description="Email address of client (example email@outlook.com)", max_length=255)
    notes: Optional[str] = Field(None, title="Notes", description="Notes, any useful information about the object")
    portfolios: Optional[List[int]] = Field(None, title="Portfolios")
    portfolios_object: Optional[List['PortfolioView']] = Field(None, description="readonly")
    client_secrets: Optional[List[int]] = Field(None, title="Client secrets", description="readonly")
    client_secrets_object: Optional[List[ClientSecretLight]] = Field(None, title="Client secrets object")
    deleted_user_code: Optional[str] = Field(None, title="Deleted user code", description="readonly", max_length=255)