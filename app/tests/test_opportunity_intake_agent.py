#!/usr/bin/env python3
"""
Test script for the Opportunity Intake Agent
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

def test_opportunity_intake_creation_agent():
    """Test the OpportunityIntakeCreationAgent class"""
    
    # Mock the conversation store
    mock_conversation_store = Mock()
    mock_conversation_store.get_last_n_messages.return_value = []
    
    # Import the agent
    from app.agent.opportunity_intake_creation_agent import OpportunityIntakeCreationAgent
    
    # Create an instance
    agent = OpportunityIntakeCreationAgent()
    
    # Test that the agent has the expected attributes
    assert hasattr(agent, 'prompt')
    assert hasattr(agent, 'generate_response')
    
    # Test that the prompt is built correctly
    assert agent.prompt is not None
    
    print("✅ OpportunityIntakeCreationAgent test passed!")

if __name__ == "__main__":
    test_opportunity_intake_creation_agent() 