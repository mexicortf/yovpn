from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routes import api
import logging

logger = logging.getLogger(__name__)

# Create FastAPI app with optimized settings
app = FastAPI(
    title=settings.app_name,
    description="API for YoVPN WebApp - Telegram Mini App for v2raytun activation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting YoVPN WebApp API...")
    logger.info(f"📡 Marzban API URL: {settings.marzban_api_url}")
    
    # Initialize cache
    try:
        from app.utils.cache import cache
        await cache.connect()
        logger.info("✅ Redis cache initialized")
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize cache: {e}")
    
    # Import and check marzban service
    try:
        from app.services.subscription_service import subscription_service
        
        if subscription_service.marzban_service:
            # Check API availability
            is_available = await subscription_service.marzban_service.check_api_availability()
            if is_available:
                logger.info("✅ Marzban API is available and ready")
            else:
                logger.warning("⚠️ Marzban API is not available - check configuration")
        else:
            logger.warning("⚠️ Marzban service not initialized - check dependencies")
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        import traceback
        traceback.print_exc()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down YoVPN WebApp API...")
    
    # Close cache connection
    try:
        from app.utils.cache import cache
        await cache.close()
        logger.info("✅ Redis cache closed")
    except Exception as e:
        logger.warning(f"⚠️ Failed to close cache: {e}")
    
    # Close marzban service
    try:
        from app.services.subscription_service import subscription_service
        
        if subscription_service.marzban_service:
            await subscription_service.marzban_service.close()
            logger.info("✅ Marzban service closed")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "YoVPN WebApp API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
