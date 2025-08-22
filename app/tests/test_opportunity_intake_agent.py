#!/usr/bin/env python3
"""
Test script for the Opportunity Intake Agent
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))


def test_opportunity_intake_agent():
    """Test the opportunity intake agent directly"""
    print("🧪 Testing Opportunity Intake Agent Directly")
    print("=" * 40)

    try:
        from app.agent.opportunity_intake_agent import OpportunityIntakeAgent

        print("✅ Successfully imported Opportunity Intake agent")

        agent = OpportunityIntakeAgent()
        print("✅ Successfully created Opportunity Intake agent instance")

        # Test the prompt building
        prompt = agent.build_prompt()
        print("✅ Successfully built prompt")

        print(f"Prompt template: {type(prompt)}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_opportunity_intake_agent() 