"""
Health check endpoints for monitoring
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import time
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Store startup time
STARTUP_TIME = time.time()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring
    
    Returns:
        JSON with health status
    """
    try:
        uptime = time.time() - STARTUP_TIME
        
        # Check Redis connection
        redis_healthy = False
        try:
            from app.utils.cache import cache
            if cache.client:
                await cache.client.ping()
                redis_healthy = True
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
        
        # Check Marzban API
        marzban_healthy = False
        try:
            from app.services.subscription_service import subscription_service
            if subscription_service.marzban_service:
                marzban_healthy = await subscription_service.marzban_service.check_api_availability()
        except Exception as e:
            logger.warning(f"Marzban health check failed: {e}")
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "uptime_seconds": int(uptime),
                "services": {
                    "redis": "healthy" if redis_healthy else "unhealthy",
                    "marzban": "healthy" if marzban_healthy else "unhealthy",
                },
                "timestamp": time.time(),
            },
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time(),
            },
        )


@router.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check - verifies all critical services are available
    
    Returns:
        JSON with readiness status
    """
    try:
        ready = True
        services_status = {}
        
        # Check Redis
        try:
            from app.utils.cache import cache
            if cache.client:
                await cache.client.ping()
                services_status["redis"] = "ready"
            else:
                services_status["redis"] = "not_ready"
                ready = False
        except Exception:
            services_status["redis"] = "not_ready"
            ready = False
        
        # Check Marzban
        try:
            from app.services.subscription_service import subscription_service
            if subscription_service.marzban_service:
                if await subscription_service.marzban_service.check_api_availability():
                    services_status["marzban"] = "ready"
                else:
                    services_status["marzban"] = "not_ready"
                    ready = False
            else:
                services_status["marzban"] = "not_ready"
                ready = False
        except Exception:
            services_status["marzban"] = "not_ready"
            ready = False
        
        status_code = 200 if ready else 503
        
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "ready" if ready else "not_ready",
                "services": services_status,
                "timestamp": time.time(),
            },
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "error": str(e),
                "timestamp": time.time(),
            },
        )


@router.get("/health/live", tags=["Health"])
async def liveness_check():
    """
    Liveness check - verifies the application is running
    
    Returns:
        JSON with liveness status
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "alive",
            "timestamp": time.time(),
        },
    )
