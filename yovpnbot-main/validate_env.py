#!/usr/bin/env python3
"""
Environment Validation Script
Run this before deployment to ensure all required configuration is present
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from api.app.utils.validators import EnvironmentValidator
    
    def print_section(title: str):
        """Print a section header"""
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}\n")
    
    def main():
        """Main validation function"""
        print_section("YoVPN Environment Validation")
        
        # Load .env file if present
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            print(f"✅ Found .env file: {env_file}")
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
                print("✅ Loaded environment variables from .env")
            except ImportError:
                print("⚠️ python-dotenv not installed, using system environment only")
        else:
            print("⚠️ No .env file found, using system environment variables only")
        
        print_section("Validation Results")
        
        # Run validation
        results = EnvironmentValidator.validate_all()
        
        # Print warnings
        if results["warnings"]:
            print("⚠️  WARNINGS:")
            for warning in results["warnings"]:
                print(f"   • {warning}")
            print()
        
        # Print errors
        if results["errors"]:
            print("❌ ERRORS:")
            for error in results["errors"]:
                print(f"   • {error}")
            print()
        
        # Print summary
        print_section("Summary")
        summary = results["summary"]
        print(f"Total environment variables: {summary['total_vars']}")
        print(f"Validated variables: {summary['validated_vars']}")
        print(f"Required variables: {summary['required_vars']}")
        
        if "missing_required" in summary:
            print(f"\n❌ Missing required: {len(summary['missing_required'])}")
            for var in summary["missing_required"]:
                config = EnvironmentValidator.VALIDATED_VARS.get(var, {})
                desc = config.get("description", "No description")
                print(f"   • {var}: {desc}")
        
        # Final status
        print_section("Final Status")
        
        if results["valid"]:
            print("✅ Configuration is VALID")
            print("🚀 Ready for deployment!")
            return 0
        else:
            print("❌ Configuration is INVALID")
            print("🛑 Fix errors before deployment")
            print("\n💡 Next steps:")
            print("   1. Review errors above")
            print("   2. Update .env file or environment variables")
            print("   3. Run this script again to verify")
            return 1
    
    if __name__ == "__main__":
        sys.exit(main())

except ImportError as e:
    print(f"❌ Error importing validation module: {e}")
    print("💡 Make sure you're in the project root directory")
    print("💡 Install dependencies: pip install -r requirements.txt")
    sys.exit(1)
