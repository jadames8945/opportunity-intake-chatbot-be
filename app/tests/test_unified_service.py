#!/usr/bin/env python3
"""
Test script for the Unified Service
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_unified_service():
    """Test the UnifiedService class"""
    
    # Import the service
    from app.services.unified_service import UnifiedService
    
    # Create an instance
    service = UnifiedService()
    
    # Test that the service has the expected attributes
    assert hasattr(service, 'router_agent')
    assert hasattr(service, 'opportunity_intake_advisor_agent')
    assert hasattr(service, 'opportunity_intake_creation_agent')
    
    print(f"✅ Service has router_agent: {hasattr(service, 'router_agent')}")
    print(f"✅ Service has opportunity_intake_advisor_agent: {hasattr(service, 'opportunity_intake_advisor_agent')}")
    print(f"✅ Service has opportunity_intake_creation_agent: {hasattr(service, 'opportunity_intake_creation_agent')}")
    
    # Test that the service can handle requests
    assert hasattr(service, 'handle_request')
    
    print("✅ UnifiedService test passed!")

if __name__ == "__main__":
    test_unified_service() 