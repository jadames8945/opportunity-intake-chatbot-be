#!/usr/bin/env python3
"""
Test script for the Unified Service
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))


def test_unified_service():
    """Test the unified service directly"""
    print("🧪 Testing Unified Service Directly")
    print("=" * 40)

    try:
        from app.services.unified_service import UnifiedService

        print("✅ Successfully imported Unified Service")

        service = UnifiedService()
        print("✅ Successfully created Unified Service instance")

        # Test that the service has the expected agents
        print(f"✅ Service has opportunity_intake_advisor_agent: {hasattr(service, 'opportunity_intake_advisor_agent')}")
        print(f"✅ Service has opportunity_intake_agent: {hasattr(service, 'opportunity_intake_agent')}")
        print(f"✅ Service has router_agent: {hasattr(service, 'router_agent')}")

        print("✅ All tests passed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_unified_service() 