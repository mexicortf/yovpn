from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TelegramInitData(BaseModel):
    """Telegram WebApp init data"""
    init_data: str


class ValidationResponse(BaseModel):
    """Validation response"""
    valid: bool
    user_id: Optional[int] = None


class SubscriptionResponse(BaseModel):
    """Subscription response"""
    user_id: int
    subscription_uri: str
    expires_at: str
    is_active: bool
    subscription_type: str


class VersionResponse(BaseModel):
    """Version response"""
    platform: str
    version: str
    download_url: str
    release_date: Optional[str] = None


class ActivationTrackRequest(BaseModel):
    """Activation tracking request"""
    user_id: int
    platform: str


class ActivationTrackResponse(BaseModel):
    """Activation tracking response"""
    success: bool
    message: str


class ActivateSubscriptionRequest(BaseModel):
    """Subscription activation request"""
    user_id: int
    platform: str
    telegram_username: Optional[str] = None


class ActivateSubscriptionResponse(BaseModel):
    """Subscription activation response"""
    success: bool
    message: str
    subscription_uri: Optional[str] = None
    expires_at: Optional[str] = None
    marzban_username: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    status_code: int
