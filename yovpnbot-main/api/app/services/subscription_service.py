import sys
import os
from typing import Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Add parent directory to path to import from existing bot services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

try:
    from bot.services.marzban_service import MarzbanService
    from bot.services.user_service import UserService
    from app.config import settings
    
    logger.info("✅ Successfully imported bot services")
except ImportError as e:
    logger.warning(f"⚠️ Failed to import bot services: {e}")
    # Fallback if imports fail
    MarzbanService = None
    UserService = None
    settings = None


class SubscriptionServiceAPI:
    """Service for managing subscriptions via API"""
    
    def __init__(self):
        if MarzbanService and settings:
            # Initialize with config from settings
            logger.info(f"🔧 Initializing MarzbanService with URL: {settings.marzban_api_url}")
            
            # Note: MarzbanService expects admin_token, but settings might have username/password
            # We'll need to adapt based on what's available
            try:
                self.marzban_service = MarzbanService(
                    api_url=settings.marzban_api_url,
                    admin_token=getattr(settings, 'marzban_admin_token', '') or ''
                )
                # Check API availability on init
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Don't check availability on init to avoid blocking
                logger.info("✅ MarzbanService initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize MarzbanService: {e}")
                self.marzban_service = None
        else:
            logger.warning("⚠️ MarzbanService not available")
            self.marzban_service = None
        
        self.user_service = UserService() if UserService else None
    
    async def get_subscription_uri(self, user_id: int) -> Optional[dict]:
        """
        Get subscription URI for user
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Subscription data or None
        """
        try:
            if not self.marzban_service or not self.user_service:
                # Mock data for development
                return {
                    'user_id': user_id,
                    'subscription_uri': f'v2ray://mock-subscription-{user_id}',
                    'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
                    'is_active': True,
                    'subscription_type': 'premium'
                }
            
            # Get user from database
            user = await self.user_service.get_user(user_id)
            
            if not user:
                return None
            
            # Get subscription from Marzban
            subscription_data = await self.marzban_service.get_user_subscription(user.marzban_username)
            
            if not subscription_data:
                return None
            
            return {
                'user_id': user_id,
                'subscription_uri': subscription_data.get('subscription_url'),
                'expires_at': subscription_data.get('expire', ''),
                'is_active': subscription_data.get('status') == 'active',
                'subscription_type': subscription_data.get('data_limit_reset_strategy', 'unknown')
            }
            
        except Exception as e:
            print(f"Error getting subscription: {e}")
            return None
    
    async def track_activation(self, user_id: int, platform: str) -> bool:
        """
        Track activation event
        
        Args:
            user_id: Telegram user ID
            platform: Platform name
            
        Returns:
            Success status
        """
        try:
            # Here you can log activation to database or analytics
            print(f"User {user_id} activated subscription on {platform}")
            return True
        except Exception as e:
            print(f"Error tracking activation: {e}")
            return False
    
    async def activate_subscription(self, user_id: int, platform: str, telegram_username: Optional[str] = None) -> Optional[dict]:
        """
        Activate subscription - creates or updates user in Marzban
        
        Args:
            user_id: Telegram user ID
            platform: Platform name
            telegram_username: Optional Telegram username
            
        Returns:
            Subscription data with URI or None on failure
        """
        try:
            if not self.marzban_service or not self.user_service:
                print(f"⚠️ Marzban service not available, returning mock data")
                # Mock data for development
                return {
                    'success': True,
                    'message': 'Subscription activated (mock mode)',
                    'subscription_uri': f'v2ray://mock-subscription-{user_id}',
                    'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
                    'marzban_username': f'user_{user_id}'
                }
            
            # Create marzban username from telegram username or user_id
            if telegram_username:
                marzban_username = telegram_username.lstrip('@')
            else:
                marzban_username = f'user_{user_id}'
            
            print(f"🔄 Activating subscription for user {user_id} (marzban: {marzban_username})")
            
            # Check if user exists in Marzban
            existing_user = await self.marzban_service.get_user(marzban_username)
            
            if existing_user:
                print(f"👤 User {marzban_username} already exists in Marzban, updating...")
                
                # Update existing user - extend subscription by 30 days
                expire_date = datetime.now() + timedelta(days=30)
                expire_timestamp = int(expire_date.timestamp())
                
                update_result = await self.marzban_service.update_user(marzban_username, {
                    'expire': expire_timestamp,
                    'status': 'active',
                })
                
                if update_result:
                    subscription_data = await self.marzban_service.get_user_subscription(marzban_username)
                    
                    return {
                        'success': True,
                        'message': 'Subscription extended successfully',
                        'subscription_uri': subscription_data.get('subscription_url') if subscription_data else None,
                        'expires_at': expire_date.isoformat(),
                        'marzban_username': marzban_username
                    }
                else:
                    print(f"❌ Failed to update user in Marzban")
                    return None
            
            else:
                print(f"🆕 Creating new user {marzban_username} in Marzban...")
                
                # Create new user with 30 days trial
                new_user = await self.marzban_service.create_user(
                    username=marzban_username,
                    telegram_id=user_id,
                    days=30,
                    data_limit=0  # Unlimited traffic
                )
                
                if new_user:
                    # Get subscription URL
                    subscription_data = await self.marzban_service.get_user_subscription(marzban_username)
                    
                    # Update user in local database
                    await self.user_service.update_user(user_id, {
                        'marzban_username': marzban_username,
                        'subscription_active': True,
                        'subscription_expires': datetime.now() + timedelta(days=30)
                    })
                    
                    return {
                        'success': True,
                        'message': 'Subscription created successfully',
                        'subscription_uri': subscription_data.get('subscription_url') if subscription_data else None,
                        'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
                        'marzban_username': marzban_username
                    }
                else:
                    print(f"❌ Failed to create user in Marzban")
                    return None
                    
        except Exception as e:
            print(f"❌ Error activating subscription: {e}")
            import traceback
            traceback.print_exc()
            return None


subscription_service = SubscriptionServiceAPI()
