from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.models.schemas import (
    TelegramInitData,
    ValidationResponse,
    SubscriptionResponse,
    VersionResponse,
    ActivationTrackRequest,
    ActivationTrackResponse,
    ActivateSubscriptionRequest,
    ActivateSubscriptionResponse,
    ErrorResponse,
)
from app.utils.telegram import validate_telegram_init_data, extract_user_id_from_init_data
from app.services.subscription_service import subscription_service
from app.config import settings

router = APIRouter(tags=["api"])


@router.post("/validate", response_model=ValidationResponse)
async def validate_init_data(data: TelegramInitData):
    """Validate Telegram WebApp init data"""
    is_valid, parsed_data = validate_telegram_init_data(data.init_data)
    
    if is_valid:
        user_id = extract_user_id_from_init_data(data.init_data)
        return ValidationResponse(valid=True, user_id=user_id)
    else:
        return ValidationResponse(valid=False)


@router.get("/subscription/{user_id}", response_model=SubscriptionResponse)
async def get_subscription(
    user_id: int,
    x_telegram_init_data: Optional[str] = Header(None)
):
    """Get subscription for user"""
    
    # Validate init data if provided
    if x_telegram_init_data:
        is_valid, _ = validate_telegram_init_data(x_telegram_init_data)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Telegram data")
    
    # Get subscription
    subscription_data = await subscription_service.get_subscription_uri(user_id)
    
    if not subscription_data:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return SubscriptionResponse(**subscription_data)


@router.get("/version/{platform}", response_model=VersionResponse)
async def get_latest_version(platform: str):
    """Get latest version for platform"""
    
    platform_urls = {
        'android': settings.android_apk_url,
        'ios': settings.ios_app_store_url,
        'macos': settings.macos_dmg_url,
        'windows': settings.windows_exe_url,
        'androidtv': settings.android_tv_apk_url,
    }
    
    download_url = platform_urls.get(platform.lower())
    
    if not download_url:
        raise HTTPException(status_code=404, detail="Platform not found")
    
    return VersionResponse(
        platform=platform,
        version="latest",  # You can implement version checking from GitHub releases
        download_url=download_url,
    )


@router.post("/track/activation", response_model=ActivationTrackResponse)
async def track_activation(
    data: ActivationTrackRequest,
    x_telegram_init_data: Optional[str] = Header(None)
):
    """Track activation event"""
    
    # Validate init data if provided
    if x_telegram_init_data:
        is_valid, _ = validate_telegram_init_data(x_telegram_init_data)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Telegram data")
    
    # Track activation
    success = await subscription_service.track_activation(data.user_id, data.platform)
    
    return ActivationTrackResponse(
        success=success,
        message="Activation tracked successfully" if success else "Failed to track activation"
    )


@router.post("/subscription/activate", response_model=ActivateSubscriptionResponse)
async def activate_subscription(
    data: ActivateSubscriptionRequest,
    x_telegram_init_data: Optional[str] = Header(None)
):
    """
    Activate subscription - creates or updates user in Marzban
    This is the main endpoint for subscription activation
    """
    
    # Validate init data if provided
    if x_telegram_init_data:
        is_valid, _ = validate_telegram_init_data(x_telegram_init_data)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid Telegram data")
    
    # Activate subscription in Marzban
    result = await subscription_service.activate_subscription(
        user_id=data.user_id,
        platform=data.platform,
        telegram_username=data.telegram_username
    )
    
    if not result:
        raise HTTPException(
            status_code=500, 
            detail="Failed to activate subscription. Please check Marzban connection."
        )
    
    return ActivateSubscriptionResponse(**result)


@router.get("/health")
async def health_check():
    """Health check endpoint for Railway and monitoring"""
    return {
        "status": "healthy",
        "service": "YoVPN WebApp API",
        "version": "1.0.0"
    }
