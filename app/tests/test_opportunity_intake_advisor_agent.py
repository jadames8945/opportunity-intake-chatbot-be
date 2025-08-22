#!/usr/bin/env python3
"""
Test script for the Opportunity Intake Advisor Agent
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))


def test_opportunity_intake_advisor_agent():
    """Test the opportunity intake advisor agent directly"""
    print("🧪 Testing Opportunity Intake Advisor Agent Directly")
    print("=" * 40)

    try:
        from app.agent.opportunity_intake_advisor_agent import OpportunityIntakeAdvisorAgent

        print("✅ Successfully imported Opportunity Intake Advisor agent")

        agent = OpportunityIntakeAdvisorAgent()
        print("✅ Successfully created Opportunity Intake Advisor agent instance")

        # Test the prompt building
        prompt = agent.build_prompt()
        print("✅ Successfully built prompt")

        print(f"Prompt template: {type(prompt)}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_opportunity_intake_advisor_agent() 