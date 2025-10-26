"""
Environment variable validation utilities
Ensures all required configuration is present and valid
"""
import os
import sys
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing"""
    pass


class EnvironmentValidator:
    """
    Validates environment variables and configuration
    """
    
    REQUIRED_VARS = [
        "TELEGRAM_BOT_TOKEN",
        "SECRET_KEY",
        "MARZBAN_API_URL",
    ]
    
    OPTIONAL_VARS = [
        "MARZBAN_USERNAME",
        "MARZBAN_PASSWORD",
        "MARZBAN_ADMIN_TOKEN",
        "REDIS_URL",
        "CORS_ORIGINS",
        "API_HOST",
        "API_PORT",
    ]
    
    VALIDATED_VARS = {
        "TELEGRAM_BOT_TOKEN": {
            "type": "string",
            "min_length": 40,
            "pattern": r"^\d+:[A-Za-z0-9_-]{35}$",
            "description": "Telegram Bot API token from @BotFather"
        },
        "SECRET_KEY": {
            "type": "string",
            "min_length": 32,
            "description": "Secret key for signing tokens"
        },
        "MARZBAN_API_URL": {
            "type": "url",
            "description": "Marzban API base URL"
        },
        "REDIS_URL": {
            "type": "url",
            "default": "redis://localhost:6379",
            "description": "Redis connection URL"
        },
        "API_PORT": {
            "type": "int",
            "min": 1,
            "max": 65535,
            "default": 8000,
            "description": "API server port"
        },
    }
    
    @staticmethod
    def validate_required_vars() -> List[str]:
        """
        Check if all required environment variables are present
        
        Returns:
            List of missing variable names
        """
        missing = []
        for var in EnvironmentValidator.REQUIRED_VARS:
            if not os.getenv(var):
                missing.append(var)
        return missing
    
    @staticmethod
    def validate_var_format(var_name: str, value: str) -> Optional[str]:
        """
        Validate format of a specific variable
        
        Args:
            var_name: Name of the variable
            value: Value to validate
            
        Returns:
            Error message if invalid, None if valid
        """
        if var_name not in EnvironmentValidator.VALIDATED_VARS:
            return None
        
        config = EnvironmentValidator.VALIDATED_VARS[var_name]
        
        # Check type
        if config["type"] == "string":
            if "min_length" in config and len(value) < config["min_length"]:
                return f"{var_name} must be at least {config['min_length']} characters"
            
            if "pattern" in config:
                import re
                if not re.match(config["pattern"], value):
                    return f"{var_name} format is invalid"
        
        elif config["type"] == "int":
            try:
                int_value = int(value)
                if "min" in config and int_value < config["min"]:
                    return f"{var_name} must be >= {config['min']}"
                if "max" in config and int_value > config["max"]:
                    return f"{var_name} must be <= {config['max']}"
            except ValueError:
                return f"{var_name} must be an integer"
        
        elif config["type"] == "url":
            if not value.startswith(("http://", "https://", "redis://")):
                return f"{var_name} must be a valid URL"
        
        return None
    
    @staticmethod
    def validate_all() -> Dict[str, Any]:
        """
        Validate all environment variables
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "summary": {}
        }
        
        # Check required vars
        missing = EnvironmentValidator.validate_required_vars()
        if missing:
            results["valid"] = False
            results["errors"].append(f"Missing required variables: {', '.join(missing)}")
            results["summary"]["missing_required"] = missing
        
        # Validate format of present vars
        for var_name, config in EnvironmentValidator.VALIDATED_VARS.items():
            value = os.getenv(var_name)
            
            # Skip if not present and not required
            if not value:
                if var_name in EnvironmentValidator.REQUIRED_VARS:
                    continue  # Already handled above
                elif "default" in config:
                    results["warnings"].append(
                        f"{var_name} not set, using default: {config['default']}"
                    )
                continue
            
            # Validate format
            error = EnvironmentValidator.validate_var_format(var_name, value)
            if error:
                results["valid"] = False
                results["errors"].append(error)
        
        # Check for conflicting auth methods
        has_username = bool(os.getenv("MARZBAN_USERNAME"))
        has_password = bool(os.getenv("MARZBAN_PASSWORD"))
        has_token = bool(os.getenv("MARZBAN_ADMIN_TOKEN"))
        
        if not (has_token or (has_username and has_password)):
            results["valid"] = False
            results["errors"].append(
                "Must provide either MARZBAN_ADMIN_TOKEN or both MARZBAN_USERNAME and MARZBAN_PASSWORD"
            )
        
        if has_token and (has_username or has_password):
            results["warnings"].append(
                "Both token and username/password provided - token will be used"
            )
        
        # Summary
        results["summary"]["total_vars"] = len(os.environ)
        results["summary"]["validated_vars"] = len(EnvironmentValidator.VALIDATED_VARS)
        results["summary"]["required_vars"] = len(EnvironmentValidator.REQUIRED_VARS)
        
        return results
    
    @staticmethod
    def validate_or_exit():
        """
        Validate configuration and exit if invalid
        """
        logger.info("🔍 Validating environment configuration...")
        
        results = EnvironmentValidator.validate_all()
        
        # Print warnings
        if results["warnings"]:
            logger.warning("⚠️ Configuration warnings:")
            for warning in results["warnings"]:
                logger.warning(f"  - {warning}")
        
        # Print errors and exit if invalid
        if not results["valid"]:
            logger.error("❌ Configuration validation failed!")
            logger.error("Errors:")
            for error in results["errors"]:
                logger.error(f"  - {error}")
            
            logger.error("\n📋 Required environment variables:")
            for var in EnvironmentValidator.REQUIRED_VARS:
                config = EnvironmentValidator.VALIDATED_VARS.get(var, {})
                desc = config.get("description", "No description")
                logger.error(f"  - {var}: {desc}")
            
            logger.error("\n💡 How to fix:")
            logger.error("  1. Create a .env file in the project root")
            logger.error("  2. Add all required variables")
            logger.error("  3. Ensure all values are in the correct format")
            
            sys.exit(1)
        
        logger.info("✅ Configuration validated successfully")
        logger.info(f"📊 Summary: {results['summary']['validated_vars']} variables validated")
        
        return results


def validate_config():
    """Convenience function to validate configuration"""
    return EnvironmentValidator.validate_or_exit()
