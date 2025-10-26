import hashlib
import hmac
from urllib.parse import parse_qsl
from typing import Optional, Dict
from app.config import settings


def validate_telegram_init_data(init_data: str) -> tuple[bool, Optional[Dict]]:
    """
    Validate Telegram WebApp init data
    
    Args:
        init_data: The init data string from Telegram WebApp
        
    Returns:
        Tuple of (is_valid, parsed_data)
    """
    try:
        # Parse init data
        parsed_data = dict(parse_qsl(init_data))
        
        # Get hash
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            return False, None
        
        # Create data check string
        data_check_arr = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
        data_check_string = '\n'.join(data_check_arr)
        
        # Calculate hash
        secret_key = hmac.new(
            "WebAppData".encode(),
            settings.telegram_bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare hashes
        is_valid = hmac.compare_digest(calculated_hash, received_hash)
        
        if is_valid:
            return True, parsed_data
        else:
            return False, None
            
    except Exception as e:
        print(f"Error validating init data: {e}")
        return False, None


def extract_user_id_from_init_data(init_data: str) -> Optional[int]:
    """
    Extract user ID from Telegram init data
    
    Args:
        init_data: The init data string from Telegram WebApp
        
    Returns:
        User ID or None
    """
    is_valid, parsed_data = validate_telegram_init_data(init_data)
    
    if not is_valid or not parsed_data:
        return None
    
    try:
        import json
        user_data = json.loads(parsed_data.get('user', '{}'))
        return user_data.get('id')
    except:
        return None
