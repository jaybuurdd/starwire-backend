from pydantic import BaseModel, Field
from typing import Optional, List

class Account(BaseModel):
    email: str
    first_name: str
    last_name: str
    wallet: Optional[str] = None
    phone: Optional[str] = None

class SocialMedia(BaseModel):
    platform: str
    username: str
    url: str

class RegisterRequest(BaseModel):
    first_name: str = Field(..., serialization_alias='firstName')
    last_name: str = Field(..., serialization_alias='lastName')
    email: str
    phone: str
    wallet: Optional[str]
    address: Optional[str] = Field(..., serialization_alias='address') 
    city: Optional[str]
    state: str
    country: str
    postal_code: Optional[str] = Field(..., serialization_alias='postalCode')
    socials: List[SocialMedia]


    class Config:
        populate_by_name = True

class SignInRequest(BaseModel):
    email: str
    otp: int